#!/usr/bin/env python3
"""Extract all user prompts from knowledge.db into the atomized task pipeline.

Layer 1 of the prompt atomization pipeline — mechanical extraction.
No AI required. Pulls every substantive user prompt, assigns atom IDs,
attaches provider/thread/timestamp metadata, and exports as JSONL
matching the atomized-tasks.jsonl schema.

Usage:
    python3 scripts/extract_prompt_atoms.py [--min-length 50] [--output PATH]
"""

import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "knowledge.db"
DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent.parent.parent
    / "organvm-corpvs-testamentvm"
    / "data"
    / "atoms"
    / "prompt-atoms.jsonl"
)

# Noise prompts to skip — single-word acknowledgements, navigation commands
NOISE_PATTERNS = {
    "yes", "no", "ok", "okay", "sure", "thanks", "thank you", "y", "n", "k",
    "correct", "right", "got it", "yep", "nope", "exactly", "continue",
    "go", "done", "next", "go ahead", "please", "thx", "ty", "np",
    "sounds good", "perfect", "great", "good", "fine", "agreed",
}


def short_hash(text: str, length: int = 12) -> str:
    """Generate a short deterministic hash for an atom ID."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:length]


def is_noise(content: str) -> bool:
    """Check if a prompt is just noise (acknowledgement, single word, etc.)."""
    normalized = content.strip().lower().rstrip(".!?,")
    if normalized in NOISE_PATTERNS:
        return True
    # Skip prompts that are just whitespace or punctuation
    if len(normalized) < 5 and not any(c.isalpha() for c in normalized):
        return True
    return False


def infer_domain(content: str) -> str:
    """Basic domain inference from prompt content keywords."""
    lower = content.lower()
    domain_signals = {
        "architecture": ["architecture", "organ", "organvm", "system design", "schema"],
        "infrastructure": ["deploy", "ci/cd", "docker", "launchagent", "homebrew", "chezmoi", "dotfile"],
        "code": ["function", "class", "import", "def ", "const ", "async ", "test", "bug", "fix", "refactor"],
        "content": ["essay", "write", "draft", "article", "blog", "readme", "documentation"],
        "research": ["research", "analyze", "compare", "investigate", "study", "review"],
        "career": ["job", "application", "resume", "portfolio", "interview", "linkedin", "company"],
        "governance": ["governance", "sop", "protocol", "policy", "compliance", "audit"],
        "creative": ["art", "music", "generative", "visual", "three.js", "canvas", "performance"],
        "data": ["database", "sqlite", "query", "ingest", "pipeline", "atom", "corpus"],
        "security": ["security", "secret", "credential", "auth", "encrypt", "vulnerability"],
        "email": ["email", "inbox", "gmail", "mail", "reply", "send"],
    }
    for domain, signals in domain_signals.items():
        if any(signal in lower for signal in signals):
            return domain
    return "general"


def infer_priority(content: str, length: int) -> str:
    """Rough priority inference from prompt characteristics."""
    lower = content.lower()
    if any(w in lower for w in ["urgent", "critical", "p0", "emergency", "breaking", "broken"]):
        return "P0"
    if any(w in lower for w in ["important", "p1", "need", "must", "required", "blocker"]):
        return "P1"
    if length > 1000:
        return "P1"  # Long prompts indicate significant intent
    if length > 200:
        return "P2"
    return "P3"


def classify_prompt_type(content: str) -> str:
    """Classify what kind of prompt this is."""
    lower = content.lower()
    if "?" in content and len(content) < 500:
        return "question"
    if any(w in lower for w in ["fix", "bug", "error", "broken", "failing", "issue"]):
        return "bug_fix"
    if any(w in lower for w in ["create", "build", "implement", "add", "new", "write"]):
        return "creation"
    if any(w in lower for w in ["refactor", "clean", "reorganize", "rename", "move"]):
        return "refactor"
    if any(w in lower for w in ["review", "audit", "check", "verify", "validate"]):
        return "review"
    if any(w in lower for w in ["research", "find", "search", "look", "explore"]):
        return "research"
    if any(w in lower for w in ["deploy", "push", "commit", "merge", "release"]):
        return "operations"
    if any(w in lower for w in ["plan", "design", "architect", "strategy", "approach"]):
        return "planning"
    return "directive"


def extract_prompts(min_length: int = 50, output_path: Path = DEFAULT_OUTPUT) -> None:
    if not DB_PATH.exists():
        print(f"ERROR: database not found at {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Pull all user prompts with thread context
    cursor.execute("""
        SELECT
            ct.id as turn_id,
            ct.content,
            ct.timestamp as turn_timestamp,
            ct.turn_index,
            t.id as thread_id,
            t.provider_ref_id,
            t.title as thread_title,
            t.source_path,
            t.created_at as thread_created_at
        FROM chat_turns ct
        JOIN chat_threads t ON ct.thread_id = t.id
        WHERE ct.role = 'user'
        ORDER BY t.provider_ref_id, t.created_at, ct.turn_index
    """)

    rows = cursor.fetchall()
    conn.close()

    print(f"Total user prompts in DB: {len(rows)}")

    # Map provider_ref_id to clean names
    provider_map = {
        "provider-claude": "claude",
        "provider-chatgpt": "chatgpt",
        "provider-copilot": "copilot",
        "provider-gemini": "gemini",
        "provider-grok": "grok",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)

    atoms = []
    skipped_noise = 0
    skipped_short = 0

    for row in rows:
        content = row["content"].strip()

        if is_noise(content):
            skipped_noise += 1
            continue

        if len(content) < min_length:
            skipped_short += 1
            continue

        provider = provider_map.get(row["provider_ref_id"], row["provider_ref_id"])

        # Deterministic ID from provider + thread + turn_index
        id_seed = f"{row['provider_ref_id']}:{row['thread_id']}:{row['turn_index']}"
        atom_id = f"prompt-{short_hash(id_seed)}"

        # Title: first line or first 80 chars
        first_line = content.split("\n")[0].strip()
        title = first_line[:80] if first_line else content[:80]

        domain = infer_domain(content)
        priority = infer_priority(content, len(content))
        prompt_type = classify_prompt_type(content)

        atom = {
            "id": atom_id,
            "title": title,
            "content": content,
            "source": {
                "type": "user_prompt",
                "provider": provider,
                "thread_id": row["thread_id"],
                "thread_title": row["thread_title"],
                "turn_index": row["turn_index"],
                "source_path": row["source_path"],
                "timestamp": row["turn_timestamp"] or row["thread_created_at"],
            },
            "agent": provider,
            "status": "OPEN",  # Layer 3 will infer actual status
            "prompt_type": prompt_type,
            "actionable": True,
            "tags": [provider, domain, prompt_type],
            "priority": priority,
            "domain": domain,
            "complexity": {
                "char_length": len(content),
                "line_count": content.count("\n") + 1,
                "has_code_block": "```" in content,
                "sub_item_count": 0,  # Layer 2 will decompose
            },
            "decomposition": {
                "sub_prompts": [],  # Layer 2 populates this
                "layer": 1,        # Extraction layer only
            },
        }

        atoms.append(atom)

    # Write JSONL
    with open(output_path, "w", encoding="utf-8") as f:
        for atom in atoms:
            f.write(json.dumps(atom, ensure_ascii=False) + "\n")

    # Stats
    by_provider = {}
    by_domain = {}
    by_priority = {}
    by_type = {}
    for a in atoms:
        prov = a["source"]["provider"]
        by_provider[prov] = by_provider.get(prov, 0) + 1
        by_domain[a["domain"]] = by_domain.get(a["domain"], 0) + 1
        by_priority[a["priority"]] = by_priority.get(a["priority"], 0) + 1
        by_type[a["prompt_type"]] = by_type.get(a["prompt_type"], 0) + 1

    print(f"\nExtracted: {len(atoms)} prompt atoms")
    print(f"Skipped: {skipped_noise} noise, {skipped_short} too short (<{min_length} chars)")
    print(f"\nBy provider: {json.dumps(by_provider, indent=2)}")
    print(f"\nBy domain: {json.dumps(by_domain, indent=2)}")
    print(f"\nBy priority: {json.dumps(by_priority, indent=2)}")
    print(f"\nBy type: {json.dumps(by_type, indent=2)}")
    print(f"\nOutput: {output_path}")
    print(f"Size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    min_len = 50
    output = DEFAULT_OUTPUT

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--min-length" and i + 1 < len(args):
            min_len = int(args[i + 1])
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output = Path(args[i + 1])
            i += 2
        else:
            i += 1

    extract_prompts(min_length=min_len, output_path=output)
