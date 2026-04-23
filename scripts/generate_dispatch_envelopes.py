#!/usr/bin/env python3
"""
generate_dispatch_envelopes.py — Read VERIFIED_OPEN items from review-results.db,
assign each to an agent (codex/gemini/claude), and write dispatch envelopes
ready for `agent-dispatch <agent> "prompt" --dir <path>`.

Tables consumed:
  - filesystem_triage  (status = VERIFIED_OPEN, creation_intent = 1)
  - triage_results     (classification = VERIFIED_OPEN, priority IN (P0, P1))

Output: ~/.local/state/agent-dispatch/envelopes/session-YYYY-MM-DD/
"""

import json
import os
import re
import sqlite3
import sys
import textwrap
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "review-results.db"
SESSION_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")
ENVELOPE_DIR = (
    Path.home() / ".local" / "state" / "agent-dispatch" / "envelopes"
    / f"session-{SESSION_DATE}"
)
WORKSPACE = Path.home() / "Workspace"

# ---------------------------------------------------------------------------
# Agent routing
# ---------------------------------------------------------------------------

# Domain -> default agent. Claude handles architecture/governance;
# Codex handles code/infra; Gemini handles content/research/creative.
DOMAIN_AGENT = {
    "architecture": "claude",
    "governance": "claude",
    "infrastructure": "codex",
    "code": "codex",
    "data": "codex",
    "research": "gemini",
    "content": "gemini",
    "creative": "gemini",
    "career": "gemini",
    "email": "gemini",
    "general": "gemini",
}

# prompt_type overrides: some types warrant a specific agent regardless of domain
PROMPT_TYPE_OVERRIDE = {
    "bug_fix": "codex",
    "refactor": "codex",
    "creation": "gemini",
    "research": "gemini",
}

# File extension -> agent for filesystem_triage items
EXT_AGENT = {
    ".py": "codex",
    ".js": "codex",
    ".ts": "codex",
    ".sh": "codex",
    ".go": "codex",
    ".rs": "codex",
    ".json": "codex",
    ".yaml": "codex",
    ".yml": "codex",
    ".toml": "codex",
    ".md": "gemini",
    ".html": "codex",
    ".css": "codex",
}


def classify_agent_for_triage(row: dict) -> str:
    """Determine which agent should handle a triage_results item."""
    domain = (row.get("domain") or "general").lower()
    prompt_type = (row.get("prompt_type") or "").lower()

    # Architecture and governance are always Claude (strategic)
    if domain in ("architecture", "governance"):
        return "claude"

    # prompt_type overrides for mechanical/tactical work
    if prompt_type in PROMPT_TYPE_OVERRIDE:
        return PROMPT_TYPE_OVERRIDE[prompt_type]

    return DOMAIN_AGENT.get(domain, "gemini")


def classify_agent_for_file(row: dict) -> str:
    """Determine which agent should handle a filesystem_triage item."""
    basename = row.get("file_basename", "")
    ref_type = (row.get("ref_type") or "").lower()

    # Directory creation is boilerplate -> codex
    if ref_type == "create_dir":
        return "codex"

    ext = os.path.splitext(basename)[1].lower()
    return EXT_AGENT.get(ext, "codex")


# ---------------------------------------------------------------------------
# Directory inference
# ---------------------------------------------------------------------------

def infer_directory(row: dict, source: str) -> str:
    """Best-effort directory inference from context clues."""
    if source == "filesystem":
        file_ref = row.get("file_ref", "")
        # Absolute paths use their parent
        if file_ref.startswith("/"):
            return str(Path(file_ref).parent)
        # Relative paths with slashes — look for known workspace patterns
        if "/" in file_ref:
            top = file_ref.split("/")[0]
            candidate = WORKSPACE / top
            if candidate.exists():
                return str(candidate)
        # Fall back to knowledge-base root
        return str(DB_PATH.parent.parent)

    # triage_results: use content_preview or tags for hints
    content = (row.get("content_preview") or "").lower()
    tags_raw = row.get("tags") or "[]"
    try:
        tags = json.loads(tags_raw) if isinstance(tags_raw, str) else tags_raw
    except (json.JSONDecodeError, TypeError):
        tags = []

    # Keyword heuristics against known workspace repos
    for kw, subdir in [
        ("domus", "4444J99/domus-semper-palingenesis"),
        ("chezmoi", "4444J99/domus-semper-palingenesis"),
        ("organvm", "a-organvm"),
        ("knowledge", "organvm/my-knowledge-base"),
        ("gcp", "organvm/my-knowledge-base"),
        ("deploy", "organvm/my-knowledge-base"),
        ("pipeline", "organvm/my-knowledge-base"),
    ]:
        if kw in content or kw in str(tags).lower():
            candidate = WORKSPACE / subdir
            if candidate.exists():
                return str(candidate)

    # Default to knowledge-base
    return str(DB_PATH.parent.parent)


# ---------------------------------------------------------------------------
# Prompt generation
# ---------------------------------------------------------------------------

def build_prompt_for_file(row: dict) -> str:
    """Build a dispatch prompt for a missing file/directory."""
    basename = row["file_basename"]
    ref_type = row.get("ref_type", "bare_file")
    file_ref = row.get("file_ref", basename)
    title = (row.get("atom_title") or "").strip()
    request_count = row.get("request_count", 1)

    if ref_type == "create_dir":
        return (
            f"Create the directory '{file_ref}' if it does not exist. "
            f"This directory was referenced {request_count} time(s) across the codebase. "
            f"Context: {title[:200]}"
        )

    if ref_type == "create_file":
        return (
            f"Create the file '{file_ref}' with appropriate scaffolding. "
            f"This file was explicitly requested for creation {request_count} time(s). "
            f"Context: {title[:200]}"
        )

    # bare_file or quoted_path — the file was referenced but doesn't exist
    return (
        f"The file '{basename}' (path: {file_ref}) was referenced {request_count} time(s) "
        f"but does not exist. Determine if it should be created, and if so, "
        f"scaffold it with appropriate content. Context: {title[:200]}"
    )


def build_prompt_for_triage(row: dict) -> str:
    """Build a dispatch prompt for a VERIFIED_OPEN triage item."""
    title = (row.get("title") or "").strip()
    priority = row.get("priority", "P1")
    domain = row.get("domain", "general")
    prompt_type = row.get("prompt_type", "unknown")
    content = (row.get("content_preview") or "").strip()
    evidence = (row.get("evidence") or "").strip()
    item_id = row.get("id", "unknown")

    # Truncate content preview for the prompt
    preview = content[:500] if content else title[:200]

    return (
        f"[{priority}] {domain}/{prompt_type} — {title[:120]}\n\n"
        f"Atom ID: {item_id}\n"
        f"Evidence: {evidence}\n\n"
        f"Original request:\n{preview}\n\n"
        f"Resolve this item: implement, create, or close with justification."
    )


# ---------------------------------------------------------------------------
# Envelope structure
# ---------------------------------------------------------------------------

def make_envelope(
    agent: str,
    prompt: str,
    directory: str,
    source_table: str,
    source_id: str,
    priority: str,
    metadata: dict,
) -> dict:
    """Build a structured envelope dict."""
    return {
        "agent": agent,
        "prompt": prompt,
        "directory": directory,
        "source_table": source_table,
        "source_id": str(source_id),
        "priority": priority,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata,
        "command": f'agent-dispatch {agent} "{_escape_prompt(prompt[:200])}" --dir {directory}',
    }


def _escape_prompt(text: str) -> str:
    """Escape double-quotes and newlines for shell embedding."""
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").strip()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    # ── 1. Filesystem triage: aggregate by file_basename to deduplicate ──
    fs_rows = conn.execute("""
        SELECT
            file_basename,
            ref_type,
            COUNT(*) as request_count,
            GROUP_CONCAT(DISTINCT atom_type) as atom_types,
            -- pick one representative row's fields
            MIN(file_ref) as file_ref,
            MIN(atom_title) as atom_title,
            MIN(atom_id) as atom_id
        FROM filesystem_triage
        WHERE status = 'VERIFIED_OPEN'
          AND creation_intent = 1
        GROUP BY file_basename, ref_type
        ORDER BY request_count DESC
    """).fetchall()

    # ── 2. Triage results: all VERIFIED_OPEN ──
    triage_rows = conn.execute("""
        SELECT *
        FROM triage_results
        WHERE classification = 'VERIFIED_OPEN'
          AND priority IN ('P0', 'P1')
        ORDER BY
            CASE priority WHEN 'P0' THEN 0 ELSE 1 END,
            timestamp ASC
    """).fetchall()

    conn.close()

    # ── 3. Generate envelopes ──
    envelopes: list[dict] = []
    agent_counter: Counter = Counter()
    priority_counter: Counter = Counter()

    # Filesystem items
    for row in fs_rows:
        row_dict = dict(row)
        agent = classify_agent_for_file(row_dict)
        directory = infer_directory(row_dict, source="filesystem")
        prompt = build_prompt_for_file(row_dict)
        priority = "P0" if row_dict["request_count"] >= 7 else "P1"

        env = make_envelope(
            agent=agent,
            prompt=prompt,
            directory=directory,
            source_table="filesystem_triage",
            source_id=row_dict["file_basename"],
            priority=priority,
            metadata={
                "file_basename": row_dict["file_basename"],
                "ref_type": row_dict["ref_type"],
                "request_count": row_dict["request_count"],
                "atom_types": row_dict["atom_types"],
            },
        )
        envelopes.append(env)
        agent_counter[agent] += 1
        priority_counter[priority] += 1

    # Triage items
    for row in triage_rows:
        row_dict = dict(row)
        agent = classify_agent_for_triage(row_dict)
        directory = infer_directory(row_dict, source="triage")
        prompt = build_prompt_for_triage(row_dict)

        env = make_envelope(
            agent=agent,
            prompt=prompt,
            directory=directory,
            source_table="triage_results",
            source_id=row_dict["id"],
            priority=row_dict["priority"],
            metadata={
                "domain": row_dict.get("domain"),
                "prompt_type": row_dict.get("prompt_type"),
                "source_provider": row_dict.get("source_provider"),
                "original_status": row_dict.get("status"),
            },
        )
        envelopes.append(env)
        agent_counter[agent] += 1
        priority_counter[row_dict["priority"]] += 1

    # ── 4. Write envelopes ──
    ENVELOPE_DIR.mkdir(parents=True, exist_ok=True)

    # Write individual envelope files, grouped by agent
    by_agent: dict[str, list[dict]] = defaultdict(list)
    for env in envelopes:
        by_agent[env["agent"]].append(env)

    files_written = 0
    for agent, agent_envelopes in sorted(by_agent.items()):
        # Sort by priority (P0 first), then by source
        agent_envelopes.sort(key=lambda e: (e["priority"], e["source_table"]))

        for idx, env in enumerate(agent_envelopes, 1):
            filename = f"{agent}-{idx:04d}-{env['priority']}.json"
            filepath = ENVELOPE_DIR / filename
            filepath.write_text(json.dumps(env, indent=2) + "\n")
            files_written += 1

    # Write manifest (batch-executable summary)
    manifest = {
        "session": f"session-{SESSION_DATE}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_envelopes": len(envelopes),
        "by_agent": dict(agent_counter),
        "by_priority": dict(priority_counter),
        "envelope_dir": str(ENVELOPE_DIR),
        "agents": sorted(by_agent.keys()),
    }
    manifest_path = ENVELOPE_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    # Write batch-fire scripts per agent
    for agent, agent_envelopes in sorted(by_agent.items()):
        script_path = ENVELOPE_DIR / f"fire-{agent}.sh"
        lines = [
            "#!/usr/bin/env bash",
            "set -euo pipefail",
            f'# Batch dispatch: {len(agent_envelopes)} envelopes for {agent}',
            f'# Generated: {SESSION_DATE}',
            "",
        ]
        for env in agent_envelopes:
            # Truncate prompt to first line, max 200 chars for shell safety
            short_prompt = _escape_prompt(env["prompt"].split("\n")[0][:200])
            lines.append(
                f'agent-dispatch {agent} "{short_prompt}" --dir {env["directory"]}'
            )
        lines.append("")
        script_path.write_text("\n".join(lines))
        script_path.chmod(0o755)

    # ── 5. Report ──
    print(f"\n{'='*60}")
    print(f"  DISPATCH ENVELOPES GENERATED")
    print(f"{'='*60}")
    print(f"  Session:    session-{SESSION_DATE}")
    print(f"  Output:     {ENVELOPE_DIR}")
    print(f"  Total:      {len(envelopes)} envelopes")
    print()
    print(f"  By agent:")
    for agent in sorted(agent_counter):
        print(f"    {agent:12s}  {agent_counter[agent]:>4d}")
    print()
    print(f"  By priority:")
    for pri in sorted(priority_counter):
        print(f"    {pri:12s}  {priority_counter[pri]:>4d}")
    print()
    print(f"  Sources:")
    fs_count = sum(1 for e in envelopes if e["source_table"] == "filesystem_triage")
    tr_count = sum(1 for e in envelopes if e["source_table"] == "triage_results")
    print(f"    filesystem_triage  {fs_count:>4d}")
    print(f"    triage_results     {tr_count:>4d}")
    print()
    print(f"  Files written: {files_written} envelopes + manifest + {len(by_agent)} fire scripts")
    print()
    print(f"  Ready to fire:")
    for agent in sorted(by_agent):
        script = ENVELOPE_DIR / f"fire-{agent}.sh"
        print(f"    bash {script}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
