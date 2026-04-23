#!/usr/bin/env python3
"""Generate per-domain backlog reports from prompt atoms.

Reads prompt-atoms.jsonl and intention-trajectories.jsonl, produces:
  - One backlog-{domain}.md per domain (12 files)
  - One backlogs-summary.md cross-domain overview

All output goes to:
  ~/Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/backlogs/

stdlib only.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ATOMS_DIR = Path.home() / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms"
ATOMS_FILE = ATOMS_DIR / "prompt-atoms.jsonl"
TRAJECTORIES_FILE = ATOMS_DIR / "intention-trajectories.jsonl"
OUTPUT_DIR = ATOMS_DIR / "backlogs"

DOMAINS = [
    "general", "code", "creative", "architecture", "content",
    "research", "governance", "career", "email", "data",
    "infrastructure", "security",
]

ACTIONABLE_STATUSES = {"OPEN", "PARTIAL", "DEFERRED"}
ALL_STATUSES = ["ANSWERED", "OPEN", "PARTIAL", "DEFERRED", "FAILED"]
TODAY = datetime.now().strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
def load_jsonl(path: Path) -> list[dict]:
    items: list[dict] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def load_atoms() -> list[dict]:
    print(f"Loading atoms from {ATOMS_FILE} ...")
    atoms = load_jsonl(ATOMS_FILE)
    print(f"  Loaded {len(atoms)} atoms")
    return atoms


def load_trajectories() -> list[dict]:
    print(f"Loading trajectories from {TRAJECTORIES_FILE} ...")
    trajs = load_jsonl(TRAJECTORIES_FILE)
    print(f"  Loaded {len(trajs)} trajectories")
    return trajs


# ---------------------------------------------------------------------------
# Index builders
# ---------------------------------------------------------------------------
def build_domain_index(atoms: list[dict]) -> dict[str, list[dict]]:
    """Map domain -> list of atoms."""
    idx: dict[str, list[dict]] = defaultdict(list)
    for a in atoms:
        idx[a.get("domain", "general")].append(a)
    return idx


def build_trajectory_member_index(trajs: list[dict]) -> dict[str, list[dict]]:
    """Map atom_id -> list of trajectories it belongs to."""
    idx: dict[str, list[dict]] = defaultdict(list)
    for t in trajs:
        for mid in t.get("member_ids", []):
            idx[mid].append(t)
    return idx


def build_trajectory_domain_index(trajs: list[dict]) -> dict[str, list[dict]]:
    """Map domain -> list of trajectories whose domain matches."""
    idx: dict[str, list[dict]] = defaultdict(list)
    for t in trajs:
        d = t.get("domain", "general")
        idx[d].append(t)
    return idx


# ---------------------------------------------------------------------------
# Priority scoring
# ---------------------------------------------------------------------------
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
STATUS_WEIGHT = {"OPEN": 0, "PARTIAL": 1, "DEFERRED": 2}


def sort_key(atom: dict) -> tuple:
    """Lower = higher priority."""
    p = PRIORITY_ORDER.get(atom.get("priority", "P3"), 3)
    s = STATUS_WEIGHT.get(atom.get("status", "OPEN"), 0)
    # Newer dates first within same priority band
    ts = atom.get("source", {}).get("timestamp", "")
    return (p, s, ts)


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------
def extract_date(atom: dict) -> str:
    ts = atom.get("source", {}).get("timestamp", "")
    if ts:
        return ts[:10]
    return "unknown"


def date_range(atoms: list[dict]) -> tuple[str, str]:
    dates = [extract_date(a) for a in atoms]
    dates = [d for d in dates if d != "unknown"]
    if not dates:
        return ("unknown", "unknown")
    return (min(dates), max(dates))


# ---------------------------------------------------------------------------
# Markdown generators
# ---------------------------------------------------------------------------
def truncate(text: str, limit: int = 200) -> str:
    text = text.replace("\n", " ").strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


def atom_title(atom: dict) -> str:
    return atom.get("title", "(untitled)").strip()


def render_atom_full(atom: dict) -> str:
    """Full content block for P0 items."""
    lines = [
        f"#### `{atom['id']}` -- {atom.get('priority', '?')} / {atom.get('status', '?')}",
        "",
        f"**Date:** {extract_date(atom)}  ",
        f"**Provider:** {atom.get('source', {}).get('provider', '?')}  ",
        f"**Type:** {atom.get('prompt_type', '?')}  ",
        f"**Tags:** {', '.join(atom.get('tags', []))}",
        "",
        "```",
        atom.get("content", "(no content)"),
        "```",
        "",
    ]
    return "\n".join(lines)


def render_atom_line(atom: dict) -> str:
    """Single-line for P1 items."""
    date = extract_date(atom)
    title = truncate(atom_title(atom), 100)
    return f"- `{atom['id']}` [{atom.get('status', '?')}] ({date}) -- {title}"


def render_trajectory_block(traj: dict) -> str:
    label = traj.get("intention_label", "(unlabeled)")
    count = traj.get("count", 0)
    span = traj.get("span", {})
    span_str = f"{span.get('first', '?')} to {span.get('latest', '?')} ({span.get('months', '?')} months)"
    status = traj.get("status", "?")
    phrases = ", ".join(traj.get("top_phrases", [])[:8])
    return (
        f"- **{label}** ({count} atoms, {status})\n"
        f"  Span: {span_str}\n"
        f"  Phrases: {phrases}"
    )


# ---------------------------------------------------------------------------
# Per-domain report
# ---------------------------------------------------------------------------
def generate_domain_report(
    domain: str,
    atoms: list[dict],
    traj_member_idx: dict[str, list[dict]],
    traj_domain_idx: dict[str, list[dict]],
) -> str:
    status_counts: Counter = Counter()
    for a in atoms:
        status_counts[a.get("status", "UNKNOWN")] += 1

    earliest, latest = date_range(atoms)

    # Partition by actionability
    actionable = [a for a in atoms if a.get("status") in ACTIONABLE_STATUSES]
    actionable.sort(key=sort_key)

    p0_items = [a for a in actionable if a.get("priority") == "P0"]
    p1_items = [a for a in actionable if a.get("priority") == "P1"]
    p2_items = [a for a in actionable if a.get("priority") == "P2"]
    p3_items = [a for a in actionable if a.get("priority") == "P3"]

    # Trajectory analysis: find trajectories that contain atoms in this domain
    traj_set: dict[str, dict] = {}
    for a in atoms:
        for t in traj_member_idx.get(a["id"], []):
            traj_set[t["trajectory_id"]] = t
    # Also include trajectories whose domain matches
    for t in traj_domain_idx.get(domain, []):
        traj_set[t["trajectory_id"]] = t

    # Sort trajectories by member count descending
    trajectories = sorted(traj_set.values(), key=lambda t: t.get("count", 0), reverse=True)

    # Provider breakdown
    provider_counts: Counter = Counter()
    for a in atoms:
        provider_counts[a.get("source", {}).get("provider", "unknown")] += 1

    # Prompt type breakdown
    type_counts: Counter = Counter()
    for a in atoms:
        type_counts[a.get("prompt_type", "unknown")] += 1

    # Build markdown
    lines: list[str] = []
    lines.append(f"# Backlog: {domain.upper()}")
    lines.append("")
    lines.append(f"*Generated: {TODAY}*")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total prompts | {len(atoms)} |")
    lines.append(f"| Date range | {earliest} to {latest} |")
    lines.append(f"| Actionable (OPEN+PARTIAL+DEFERRED) | {len(actionable)} |")
    lines.append(f"| Trajectories | {len(trajectories)} |")
    lines.append("")

    # Status breakdown
    lines.append("### Status Breakdown")
    lines.append("")
    lines.append("| Status | Count | % |")
    lines.append("|--------|-------|---|")
    for st in ALL_STATUSES:
        c = status_counts.get(st, 0)
        pct = (c / len(atoms) * 100) if atoms else 0
        lines.append(f"| {st} | {c} | {pct:.1f}% |")
    lines.append("")

    # Provider breakdown
    lines.append("### Source Providers")
    lines.append("")
    for prov, cnt in provider_counts.most_common():
        lines.append(f"- {prov}: {cnt}")
    lines.append("")

    # Prompt type breakdown
    lines.append("### Prompt Types")
    lines.append("")
    for pt, cnt in type_counts.most_common():
        lines.append(f"- {pt}: {cnt}")
    lines.append("")

    # P0 items -- full content
    lines.append("## P0 Items (Critical)")
    lines.append("")
    if p0_items:
        lines.append(f"*{len(p0_items)} items*")
        lines.append("")
        for a in p0_items:
            lines.append(render_atom_full(a))
    else:
        lines.append("No P0 items in this domain.")
        lines.append("")

    # P1 items -- title + date
    lines.append("## P1 Items (High Priority)")
    lines.append("")
    if p1_items:
        lines.append(f"*{len(p1_items)} items*")
        lines.append("")
        for a in p1_items:
            lines.append(render_atom_line(a))
        lines.append("")
    else:
        lines.append("No P1 items in this domain.")
        lines.append("")

    # P2/P3 counts only
    lines.append("## P2/P3 Items")
    lines.append("")
    lines.append(f"- P2: {len(p2_items)} items")
    lines.append(f"- P3: {len(p3_items)} items")
    lines.append("")

    # Trajectory analysis
    lines.append("## Trajectory Analysis")
    lines.append("")
    if trajectories:
        lines.append(f"*{len(trajectories)} recurring themes touch this domain*")
        lines.append("")
        for t in trajectories[:20]:
            lines.append(render_trajectory_block(t))
            lines.append("")
        if len(trajectories) > 20:
            lines.append(f"*... and {len(trajectories) - 20} more trajectories*")
            lines.append("")
    else:
        lines.append("No trajectories mapped to this domain.")
        lines.append("")

    # Recommended next actions
    lines.append("## Recommended Next Actions")
    lines.append("")
    recommendations = derive_recommendations(domain, p0_items, p1_items, actionable, trajectories, status_counts)
    for i, rec in enumerate(recommendations, 1):
        lines.append(f"{i}. {rec}")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Recommendation engine
# ---------------------------------------------------------------------------
def derive_recommendations(
    domain: str,
    p0: list[dict],
    p1: list[dict],
    actionable: list[dict],
    trajectories: list[dict],
    status_counts: Counter,
) -> list[str]:
    recs: list[str] = []

    if p0:
        recs.append(f"Resolve {len(p0)} P0 items immediately -- these are critical unfinished prompts.")

    if p1:
        recs.append(f"Triage {len(p1)} P1 items -- validate which remain relevant and schedule execution.")

    deferred = [a for a in actionable if a.get("status") == "DEFERRED"]
    if deferred:
        recs.append(f"Review {len(deferred)} DEFERRED items -- decide: promote to OPEN, close as ANSWERED, or drop.")

    partial = [a for a in actionable if a.get("status") == "PARTIAL"]
    if partial:
        recs.append(f"Complete {len(partial)} PARTIAL items -- these have incomplete outputs that need finishing.")

    failed = status_counts.get("FAILED", 0)
    if failed:
        recs.append(f"Investigate {failed} FAILED items -- determine root cause and retry or close.")

    # Trajectory-based recommendations
    active_trajs = [t for t in trajectories if t.get("status") == "ACTIVE"]
    if active_trajs:
        labels = ", ".join(t.get("intention_label", "?") for t in active_trajs[:3])
        recs.append(f"Active trajectories need attention: {labels}")

    evolved_trajs = [t for t in trajectories if t.get("status") == "EVOLVED"]
    if evolved_trajs:
        recs.append(f"{len(evolved_trajs)} trajectories have EVOLVED -- check if their direction still aligns with current priorities.")

    if not recs:
        recs.append("Domain appears clean. Maintain current state.")

    return recs


# ---------------------------------------------------------------------------
# Summary report
# ---------------------------------------------------------------------------
def generate_summary(
    domain_index: dict[str, list[dict]],
    traj_domain_idx: dict[str, list[dict]],
) -> str:
    lines: list[str] = []
    lines.append("# Backlogs Summary -- Cross-Domain Overview")
    lines.append("")
    lines.append(f"*Generated: {TODAY}*")
    lines.append("")

    total_atoms = sum(len(v) for v in domain_index.values())
    total_actionable = sum(
        1 for atoms in domain_index.values()
        for a in atoms if a.get("status") in ACTIONABLE_STATUSES
    )

    lines.append("## Overview")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total atoms | {total_atoms} |")
    lines.append(f"| Total actionable | {total_actionable} |")
    lines.append(f"| Domains | {len(DOMAINS)} |")
    lines.append(f"| Actionable rate | {(total_actionable / total_atoms * 100) if total_atoms else 0:.1f}% |")
    lines.append("")

    # Per-domain table
    lines.append("## Domain Breakdown")
    lines.append("")
    lines.append("| Domain | Total | ANSWERED | OPEN | PARTIAL | DEFERRED | FAILED | Actionable | Trajectories |")
    lines.append("|--------|-------|----------|------|---------|----------|--------|------------|--------------|")

    domain_rows: list[tuple[str, int, dict, int, int]] = []
    for domain in DOMAINS:
        atoms = domain_index.get(domain, [])
        sc: Counter = Counter()
        for a in atoms:
            sc[a.get("status", "UNKNOWN")] += 1
        act = sum(1 for a in atoms if a.get("status") in ACTIONABLE_STATUSES)
        traj_count = len(traj_domain_idx.get(domain, []))
        domain_rows.append((domain, len(atoms), sc, act, traj_count))

        lines.append(
            f"| {domain} | {len(atoms)} "
            f"| {sc.get('ANSWERED', 0)} "
            f"| {sc.get('OPEN', 0)} "
            f"| {sc.get('PARTIAL', 0)} "
            f"| {sc.get('DEFERRED', 0)} "
            f"| {sc.get('FAILED', 0)} "
            f"| {act} "
            f"| {traj_count} |"
        )
    lines.append("")

    # Priority distribution across domains
    lines.append("## Priority Distribution")
    lines.append("")
    lines.append("| Domain | P0 | P1 | P2 | P3 |")
    lines.append("|--------|----|----|----|----|")
    for domain in DOMAINS:
        atoms = domain_index.get(domain, [])
        actionable = [a for a in atoms if a.get("status") in ACTIONABLE_STATUSES]
        pc: Counter = Counter()
        for a in actionable:
            pc[a.get("priority", "P3")] += 1
        lines.append(f"| {domain} | {pc.get('P0', 0)} | {pc.get('P1', 0)} | {pc.get('P2', 0)} | {pc.get('P3', 0)} |")
    lines.append("")

    # Top domains by actionable count
    sorted_by_action = sorted(domain_rows, key=lambda r: r[3], reverse=True)
    lines.append("## Hottest Domains (by actionable count)")
    lines.append("")
    for domain, total, sc, act, traj_count in sorted_by_action[:5]:
        pct = (act / total * 100) if total else 0
        lines.append(f"1. **{domain}** -- {act} actionable / {total} total ({pct:.1f}%), {traj_count} trajectories")
    lines.append("")

    # Global P0 items across all domains
    lines.append("## All P0 Items (Cross-Domain)")
    lines.append("")
    all_p0: list[dict] = []
    for atoms in domain_index.values():
        for a in atoms:
            if a.get("priority") == "P0" and a.get("status") in ACTIONABLE_STATUSES:
                all_p0.append(a)
    all_p0.sort(key=sort_key)

    if all_p0:
        lines.append(f"*{len(all_p0)} critical items across all domains*")
        lines.append("")
        for a in all_p0:
            domain = a.get("domain", "?")
            date = extract_date(a)
            title = truncate(atom_title(a), 120)
            lines.append(f"- [{domain}] `{a['id']}` ({date}) -- {title}")
        lines.append("")
    else:
        lines.append("No P0 actionable items.")
        lines.append("")

    # Cross-domain recommendations
    lines.append("## Cross-Domain Recommendations")
    lines.append("")
    top_domain = sorted_by_action[0] if sorted_by_action else None
    if top_domain:
        lines.append(f"1. **{top_domain[0]}** has the highest actionable backlog ({top_domain[3]} items) -- prioritize triage here.")

    total_deferred = sum(
        1 for atoms in domain_index.values()
        for a in atoms if a.get("status") == "DEFERRED"
    )
    if total_deferred:
        lines.append(f"2. {total_deferred} DEFERRED items system-wide need disposition -- promote, close, or archive.")

    total_failed = sum(
        1 for atoms in domain_index.values()
        for a in atoms if a.get("status") == "FAILED"
    )
    if total_failed:
        lines.append(f"3. {total_failed} FAILED items need root-cause investigation.")

    total_partial = sum(
        1 for atoms in domain_index.values()
        for a in atoms if a.get("status") == "PARTIAL"
    )
    if total_partial:
        lines.append(f"4. {total_partial} PARTIAL items represent incomplete work -- batch-complete where possible.")

    if all_p0:
        lines.append(f"5. {len(all_p0)} P0 items demand immediate resolution before any new work begins.")

    lines.append("")

    # File index
    lines.append("## File Index")
    lines.append("")
    for domain in DOMAINS:
        lines.append(f"- [`backlog-{domain}.md`](backlog-{domain}.md)")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    if not ATOMS_FILE.exists():
        print(f"ERROR: {ATOMS_FILE} not found", file=sys.stderr)
        sys.exit(1)

    atoms = load_atoms()
    trajs = load_trajectories() if TRAJECTORIES_FILE.exists() else []

    domain_index = build_domain_index(atoms)
    traj_member_idx = build_trajectory_member_index(trajs)
    traj_domain_idx = build_trajectory_domain_index(trajs)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")

    # Generate per-domain reports
    for domain in DOMAINS:
        domain_atoms = domain_index.get(domain, [])
        if not domain_atoms:
            print(f"  {domain}: 0 atoms -- skipping")
            continue

        report = generate_domain_report(domain, domain_atoms, traj_member_idx, traj_domain_idx)
        out_path = OUTPUT_DIR / f"backlog-{domain}.md"
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(report)
        actionable_count = sum(1 for a in domain_atoms if a.get("status") in ACTIONABLE_STATUSES)
        print(f"  {domain}: {len(domain_atoms)} atoms, {actionable_count} actionable -> {out_path.name}")

    # Generate summary
    summary = generate_summary(domain_index, traj_domain_idx)
    summary_path = OUTPUT_DIR / "backlogs-summary.md"
    with open(summary_path, "w", encoding="utf-8") as fh:
        fh.write(summary)
    print(f"  summary -> {summary_path.name}")

    print(f"\nDone. {len(DOMAINS)} domain reports + 1 summary written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
