#!/usr/bin/env python3
"""Analyze unfulfilled prompt atoms and produce a prioritized action backlog.

Loads prompt-atoms.jsonl and sub-prompt-atoms.jsonl, filters for OPEN/PARTIAL
status, cross-links parent-child decompositions, and emits a sorted backlog
as both JSONL (machine-readable) and a human-readable summary to stdout.

Sorting: priority (P0 first) > recency (newest first) > domain clustering.

Usage: python3 scripts/analyze_open_prompts.py
"""

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ATOMS_DIR = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms"
)
PROMPT_ATOMS = ATOMS_DIR / "prompt-atoms.jsonl"
SUB_PROMPT_ATOMS = ATOMS_DIR / "sub-prompt-atoms.jsonl"
OUTPUT_PATH = ATOMS_DIR / "open-prompt-backlog.jsonl"

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
ACTIVE_STATUSES = {"OPEN", "PARTIAL"}


def load_jsonl(path: Path) -> list[dict]:
    """Load a JSONL file, skipping malformed lines."""
    atoms = []
    if not path.exists():
        print(f"  [WARN] File not found: {path}", file=sys.stderr)
        return atoms
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                atoms.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"  [WARN] Malformed JSON at {path.name}:{lineno}", file=sys.stderr)
    return atoms


def parse_timestamp(ts: str) -> datetime:
    """Parse ISO timestamp, tolerating microseconds and missing timezone."""
    if not ts:
        return datetime.min
    # Strip trailing Z or timezone offset for fromisoformat compatibility
    ts = ts.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        # Fall back: try truncating to seconds
        try:
            return datetime.fromisoformat(ts[:19])
        except ValueError:
            return datetime.min


def build_sub_prompt_index(sub_atoms: list[dict]) -> dict[str, list[dict]]:
    """Index sub-prompt atoms by parent_id for O(1) lookup."""
    index: dict[str, list[dict]] = defaultdict(list)
    for atom in sub_atoms:
        parent_id = atom.get("parent_id", "")
        if parent_id:
            index[parent_id].append(atom)
    return index


def extract_backlog_entry(
    atom: dict,
    sub_index: dict[str, list[dict]],
) -> dict:
    """Build a backlog entry from a prompt atom with sub-prompt linkage."""
    atom_id = atom.get("id", "")
    source = atom.get("source", {})
    timestamp = source.get("timestamp", "")
    provider = source.get("provider", "unknown")
    thread_title = source.get("thread_title", "")

    # Sub-prompt linkage
    declared_subs = atom.get("decomposition", {}).get("sub_prompts", [])
    linked_subs = sub_index.get(atom_id, [])
    # Merge: sub-prompts declared in decomposition AND found in sub-prompt-atoms
    sub_ids_from_decomp = set(declared_subs)
    sub_ids_from_file = {s["id"] for s in linked_subs}
    all_sub_ids = sub_ids_from_decomp | sub_ids_from_file
    has_sub_prompts = len(all_sub_ids) > 0

    # Sub-prompt status summary
    sub_status_counts: dict[str, int] = defaultdict(int)
    for sub in linked_subs:
        sub_status_counts[sub.get("status", "UNKNOWN")] += 1

    return {
        "id": atom_id,
        "title": atom.get("title", ""),
        "content": atom.get("content", ""),
        "status": atom.get("status", ""),
        "priority": atom.get("priority", "P3"),
        "domain": atom.get("domain", "general"),
        "prompt_type": atom.get("prompt_type", ""),
        "provider": provider,
        "timestamp": timestamp,
        "thread_title": thread_title,
        "tags": atom.get("tags", []),
        "actionable": atom.get("actionable", False),
        "complexity": atom.get("complexity", {}),
        "has_sub_prompts": has_sub_prompts,
        "sub_prompt_count": len(all_sub_ids),
        "sub_prompt_ids": sorted(all_sub_ids),
        "sub_prompt_statuses": dict(sub_status_counts),
    }


def sort_key(entry: dict) -> tuple:
    """Sort by priority (P0 first), then recency (newest first), then domain."""
    priority_rank = PRIORITY_ORDER.get(entry["priority"], 99)
    ts = parse_timestamp(entry["timestamp"])
    # Negate timestamp for descending sort (newer first)
    recency = -ts.timestamp() if ts != datetime.min else 0
    domain = entry["domain"]
    return (priority_rank, recency, domain)


def write_backlog(entries: list[dict], path: Path) -> None:
    """Write backlog entries as JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def fmt_date(ts: str) -> str:
    """Format timestamp to YYYY-MM-DD for display."""
    if not ts:
        return "no-date"
    return ts[:10]


def truncate(text: str, max_len: int = 80) -> str:
    """Truncate text for display."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def print_summary(entries: list[dict]) -> None:
    """Print a human-readable prioritized action summary."""
    total = len(entries)
    by_priority: dict[str, list[dict]] = defaultdict(list)
    by_domain: dict[str, int] = defaultdict(int)
    by_status: dict[str, int] = defaultdict(int)
    by_provider: dict[str, int] = defaultdict(int)
    with_subs = 0

    for e in entries:
        by_priority[e["priority"]].append(e)
        by_domain[e["domain"]] += 1
        by_status[e["status"]] += 1
        by_provider[e["provider"]] += 1
        if e["has_sub_prompts"]:
            with_subs += 1

    print("=" * 78)
    print("  OPEN PROMPT BACKLOG — PRIORITIZED ACTION LIST")
    print("=" * 78)
    print()
    print(f"  Total unfulfilled prompts: {total}")
    print(f"    OPEN: {by_status.get('OPEN', 0)}  |  PARTIAL: {by_status.get('PARTIAL', 0)}")
    print(f"    With sub-prompts: {with_subs}")
    print()

    # Priority breakdown
    print("  PRIORITY BREAKDOWN")
    print("  " + "-" * 40)
    for p in ["P0", "P1", "P2", "P3"]:
        count = len(by_priority.get(p, []))
        bar = "#" * min(count, 50)
        print(f"    {p}: {count:>4}  {bar}")
    print()

    # Domain breakdown
    print("  DOMAIN BREAKDOWN")
    print("  " + "-" * 40)
    for domain, count in sorted(by_domain.items(), key=lambda x: -x[1]):
        print(f"    {domain:<20} {count:>4}")
    print()

    # Provider breakdown
    print("  PROVIDER BREAKDOWN")
    print("  " + "-" * 40)
    for provider, count in sorted(by_provider.items(), key=lambda x: -x[1]):
        print(f"    {provider:<20} {count:>4}")
    print()

    # P0 detail: every single one, full content
    p0_items = by_priority.get("P0", [])
    if p0_items:
        print("=" * 78)
        print(f"  P0 — CRITICAL ({len(p0_items)} items)")
        print("=" * 78)
        # Group P0 by domain
        p0_by_domain: dict[str, list[dict]] = defaultdict(list)
        for e in p0_items:
            p0_by_domain[e["domain"]].append(e)
        for domain in sorted(p0_by_domain.keys()):
            items = p0_by_domain[domain]
            print(f"\n  [{domain.upper()}] ({len(items)} items)")
            print("  " + "-" * 60)
            for e in items:
                _print_atom_detail(e)

    # P1 detail: every single one, full content
    p1_items = by_priority.get("P1", [])
    if p1_items:
        print()
        print("=" * 78)
        print(f"  P1 — HIGH ({len(p1_items)} items)")
        print("=" * 78)
        p1_by_domain: dict[str, list[dict]] = defaultdict(list)
        for e in p1_items:
            p1_by_domain[e["domain"]].append(e)
        for domain in sorted(p1_by_domain.keys()):
            items = p1_by_domain[domain]
            print(f"\n  [{domain.upper()}] ({len(items)} items)")
            print("  " + "-" * 60)
            for e in items:
                _print_atom_detail(e)

    # P2/P3: titles only, grouped by domain
    for p in ["P2", "P3"]:
        items = by_priority.get(p, [])
        if not items:
            continue
        label = "MEDIUM" if p == "P2" else "LOW"
        print()
        print("=" * 78)
        print(f"  {p} — {label} ({len(items)} items, titles only)")
        print("=" * 78)
        p_by_domain: dict[str, list[dict]] = defaultdict(list)
        for e in items:
            p_by_domain[e["domain"]].append(e)
        for domain in sorted(p_by_domain.keys()):
            d_items = p_by_domain[domain]
            print(f"\n  [{domain.upper()}] ({len(d_items)} items)")
            print("  " + "-" * 60)
            for e in d_items:
                date = fmt_date(e["timestamp"])
                sub_marker = f" [{e['sub_prompt_count']} subs]" if e["has_sub_prompts"] else ""
                status_marker = " [PARTIAL]" if e["status"] == "PARTIAL" else ""
                print(f"    {date}  {e['id']}")
                print(f"            {truncate(e['title'], 70)}{sub_marker}{status_marker}")

    print()
    print("=" * 78)
    print(f"  Output written to: {OUTPUT_PATH}")
    print("=" * 78)


def _print_atom_detail(e: dict) -> None:
    """Print full detail for a single backlog atom."""
    date = fmt_date(e["timestamp"])
    sub_marker = f" [{e['sub_prompt_count']} sub-prompts]" if e["has_sub_prompts"] else ""
    status_marker = " [PARTIAL]" if e["status"] == "PARTIAL" else ""

    print(f"\n    {e['id']}{status_marker}")
    print(f"    Date: {date}  |  Provider: {e['provider']}  |  Type: {e['prompt_type']}")
    if e.get("thread_title"):
        print(f"    Thread: {e['thread_title']}")
    if e.get("tags"):
        print(f"    Tags: {', '.join(e['tags'])}")
    if sub_marker:
        print(f"    Decomposition: {sub_marker}")
        if e.get("sub_prompt_statuses"):
            parts = [f"{s}={c}" for s, c in sorted(e["sub_prompt_statuses"].items())]
            print(f"    Sub-prompt statuses: {', '.join(parts)}")

    # Content: show full for short, truncated for long
    content = e.get("content", "")
    content_lines = content.strip().split("\n")
    if len(content_lines) <= 10 and len(content) <= 500:
        print(f"    Content:")
        for line in content_lines:
            print(f"      {line}")
    else:
        print(f"    Content ({len(content)} chars, {len(content_lines)} lines):")
        for line in content_lines[:6]:
            print(f"      {line}")
        print(f"      ... [{len(content_lines) - 6} more lines]")


def main() -> None:
    print(f"Loading prompt atoms from {PROMPT_ATOMS}...", file=sys.stderr)
    all_atoms = load_jsonl(PROMPT_ATOMS)
    print(f"  Loaded {len(all_atoms)} atoms", file=sys.stderr)

    print(f"Loading sub-prompt atoms from {SUB_PROMPT_ATOMS}...", file=sys.stderr)
    all_sub_atoms = load_jsonl(SUB_PROMPT_ATOMS)
    print(f"  Loaded {len(all_sub_atoms)} sub-atoms", file=sys.stderr)

    # Build sub-prompt index
    sub_index = build_sub_prompt_index(all_sub_atoms)
    print(f"  Indexed {len(sub_index)} parent-child links", file=sys.stderr)

    # Filter for active (unfulfilled) atoms
    active_atoms = [
        a for a in all_atoms
        if a.get("status") in ACTIVE_STATUSES
    ]
    print(f"  Found {len(active_atoms)} OPEN/PARTIAL atoms", file=sys.stderr)

    # Build backlog entries with sub-prompt linkage
    backlog = [
        extract_backlog_entry(atom, sub_index)
        for atom in active_atoms
    ]

    # Sort: priority > recency > domain
    backlog.sort(key=sort_key)

    # Write JSONL output
    write_backlog(backlog, OUTPUT_PATH)
    print(f"  Wrote {len(backlog)} entries to {OUTPUT_PATH}", file=sys.stderr)

    # Print human-readable summary to stdout
    print_summary(backlog)


if __name__ == "__main__":
    main()
