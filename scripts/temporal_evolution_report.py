#!/usr/bin/env python3
"""Temporal Evolution Report — Intention Amalgamation.

Loads prompt atoms and intention trajectories, then for each trajectory with
10+ members produces:
  - ORIGINAL ASK (first prompt, full text)
  - CURRENT ASK (most recent prompt, full text)
  - DELTA (added/dropped concepts, language sophistication shift)
  - PROJECTED FUTURE (direction-of-travel extrapolation)
  - STATUS (CRYSTALLIZED / UNRESOLVED / EVOLVED / DORMANT)

Outputs:
  1. Markdown report (human-readable, before/after, trend analysis)
  2. Structured JSONL (machine-readable, one record per trajectory)

Usage: python3 scripts/temporal_evolution_report.py
"""

import json
import textwrap
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

ATOMS_DIR = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms"
)
ATOMS_PATH = ATOMS_DIR / "prompt-atoms.jsonl"
SHORT_ATOMS_PATH = ATOMS_DIR / "prompt-atoms-short.jsonl"
TRAJECTORIES_PATH = ATOMS_DIR / "intention-trajectories.jsonl"

OUTPUT_DIR = ATOMS_DIR
MD_OUTPUT = OUTPUT_DIR / "INTENTION-EVOLUTION-REPORT.md"
JSONL_OUTPUT = OUTPUT_DIR / "evolution-report.jsonl"

TOP_N = 30  # number of trajectories to report on
MIN_MEMBERS = 10  # minimum trajectory size to qualify

# ── Stopwords for concept extraction ──────────────────────────────────────────

STOPWORDS = {
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
    "her", "was", "one", "our", "out", "has", "his", "how", "its", "may",
    "new", "now", "old", "see", "way", "who", "did", "get", "got", "him",
    "let", "say", "she", "too", "use", "this", "that", "with", "from",
    "have", "been", "will", "would", "could", "should", "what", "when",
    "where", "which", "while", "about", "their", "them", "they", "there",
    "here", "some", "than", "then", "also", "into", "more", "very", "just",
    "like", "make", "need", "want", "know", "each", "please", "help",
    "using", "used", "does", "done", "based", "take", "sure", "look",
    "give", "well", "back", "good", "your", "these", "those", "being",
    "such", "after", "before", "between", "because", "through", "during",
    "above", "below", "other", "only", "same", "still", "most", "over",
    "under", "again", "once", "many", "much", "every", "both", "even",
    "were", "came", "come", "going", "told", "think", "keep", "following",
    "first", "last", "next", "current", "file", "files", "code", "tool",
    "really", "thing", "things", "right", "actually", "something", "going",
    "people", "trying", "gonna", "don't", "can't", "it's", "i'm", "let's",
    "you're", "that's", "here's", "there's", "didn't", "doesn't", "wasn't",
    "aren't", "won't", "isn't", "haven't", "couldn't", "wouldn't", "i've",
    "we're", "they're", "i'll", "we'll", "you'll", "he's", "she's", "it'll",
}


def load_jsonl(path: Path) -> list[dict]:
    """Load a JSONL file into a list of dicts."""
    records = []
    if not path.exists():
        return records
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def build_atom_index(atoms: list[dict]) -> dict[str, dict]:
    """Build a lookup from atom ID to atom record."""
    return {a["id"]: a for a in atoms if "id" in a}


def extract_concepts(text: str) -> set[str]:
    """Extract meaningful concept words from text."""
    words = set()
    for token in text.lower().split():
        # strip punctuation
        clean = "".join(c for c in token if c.isalnum() or c == "-")
        if len(clean) > 2 and clean not in STOPWORDS:
            words.add(clean)
    return words


def compute_sophistication(text: str) -> dict:
    """Measure linguistic sophistication of a prompt."""
    words = text.split()
    word_count = len(words)
    if word_count == 0:
        return {"word_count": 0, "avg_word_len": 0, "vocabulary_density": 0, "sentence_count": 0}

    unique_words = set(w.lower() for w in words)
    sentences = max(1, text.count(".") + text.count("?") + text.count("!"))

    return {
        "word_count": word_count,
        "avg_word_len": round(sum(len(w) for w in words) / word_count, 1),
        "vocabulary_density": round(len(unique_words) / word_count, 3),
        "sentence_count": sentences,
        "avg_sentence_len": round(word_count / sentences, 1),
    }


def classify_evolution(
    first_text: str,
    latest_text: str,
    first_concepts: set[str],
    latest_concepts: set[str],
) -> str:
    """Describe what changed between first and latest expression."""
    added = latest_concepts - first_concepts
    dropped = first_concepts - latest_concepts
    shared = first_concepts & latest_concepts

    first_soph = compute_sophistication(first_text)
    latest_soph = compute_sophistication(latest_text)

    lines = []

    # concept drift
    if added:
        sorted_added = sorted(added)[:15]
        lines.append(f"NEW CONCEPTS ({len(added)} total): {', '.join(sorted_added)}")
    if dropped:
        sorted_dropped = sorted(dropped)[:15]
        lines.append(f"DROPPED CONCEPTS ({len(dropped)} total): {', '.join(sorted_dropped)}")
    if shared:
        lines.append(f"PERSISTENT CORE ({len(shared)} concepts retained)")

    # sophistication shift
    wc_delta = latest_soph["word_count"] - first_soph["word_count"]
    vd_delta = latest_soph["vocabulary_density"] - first_soph["vocabulary_density"]

    if abs(wc_delta) > 20:
        direction = "longer" if wc_delta > 0 else "shorter"
        lines.append(f"PROMPT LENGTH: {direction} ({first_soph['word_count']} -> {latest_soph['word_count']} words)")

    if abs(vd_delta) > 0.05:
        direction = "richer vocabulary" if vd_delta > 0 else "more repetitive"
        lines.append(f"VOCABULARY: {direction} ({first_soph['vocabulary_density']:.2f} -> {latest_soph['vocabulary_density']:.2f})")

    # tone shift
    first_has_question = "?" in first_text
    latest_has_question = "?" in latest_text
    first_has_imperative = any(first_text.lower().startswith(v) for v in ["write", "create", "make", "build", "generate", "fix", "add", "update", "set"])
    latest_has_imperative = any(latest_text.lower().startswith(v) for v in ["write", "create", "make", "build", "generate", "fix", "add", "update", "set"])

    if first_has_question and not latest_has_question:
        lines.append("TONE SHIFT: questioning -> declarative/directive")
    elif not first_has_question and latest_has_question:
        lines.append("TONE SHIFT: directive -> questioning/exploratory")
    if not first_has_imperative and latest_has_imperative:
        lines.append("TONE SHIFT: exploratory -> imperative/building")
    elif first_has_imperative and not latest_has_imperative:
        lines.append("TONE SHIFT: imperative -> reflective/narrative")

    if not lines:
        lines.append("MINIMAL DRIFT: concepts and style largely unchanged")

    return "\n".join(lines)


def project_future(
    trajectory: dict,
    first_concepts: set[str],
    latest_concepts: set[str],
    density: dict[str, int],
) -> str:
    """Project what the user will likely ask next, based on trajectory direction."""
    added = latest_concepts - first_concepts
    status = trajectory.get("status", "UNKNOWN")
    domain = trajectory.get("domain", "general")
    count = trajectory.get("count", 0)

    # analyze density trend (are they asking more or less recently?)
    months_sorted = sorted(density.keys())
    if len(months_sorted) >= 3:
        recent_3 = sum(density.get(m, 0) for m in months_sorted[-3:])
        early_3 = sum(density.get(m, 0) for m in months_sorted[:3])
    else:
        recent_3 = sum(density.values())
        early_3 = recent_3

    lines = []

    if status == "CRYSTALLIZED":
        lines.append("This trajectory has converged to a repeatable formula.")
        lines.append("Future asks will likely be mechanical repetitions with minor parameter changes.")
        lines.append("AUTOMATION CANDIDATE: the pattern is stable enough to templatize.")
    elif status == "EVOLVED":
        if recent_3 > early_3:
            lines.append("ACCELERATING: this trajectory is gaining momentum.")
        else:
            lines.append("MATURED: evolution has slowed but the trajectory is still active.")

        if added:
            top_new = sorted(added)[:8]
            lines.append(f"Direction of travel points toward: {', '.join(top_new)}")

        if domain == "architecture":
            lines.append("Likely next: systems-level integration, cross-domain orchestration, governance formalization.")
        elif domain == "code":
            lines.append("Likely next: infrastructure hardening, automation pipelines, self-healing systems.")
        elif domain == "content":
            lines.append("Likely next: voice refinement, editorial pipeline, publication infrastructure.")
        elif domain == "creative":
            lines.append("Likely next: generative system design, algorithmic composition, interactive narrative.")
        else:
            lines.append("Likely next: deeper specialization within this domain, cross-pollination with adjacent trajectories.")
    elif status == "UNRESOLVED":
        lines.append("RECURRING WITHOUT RESOLUTION: keeps coming back to this without landing.")
        lines.append("The ask is likely to become more urgent or more abstract as frustration compounds.")
        lines.append("Resolution requires either: a definitive tool/process, or explicit abandonment.")
    elif status == "DORMANT":
        if count > 30:
            lines.append("HIGH-VOLUME DORMANCY: this was a major thread that went quiet.")
            lines.append("Likely to resurface when an external trigger (job, project, crisis) reactivates the domain.")
        else:
            lines.append("Inactive. May have been absorbed into a larger trajectory or genuinely resolved.")
    else:
        lines.append("Insufficient data to project trajectory.")

    return "\n".join(lines)


def compute_activity_sparkline(density: dict[str, int]) -> str:
    """Create a text-based sparkline showing activity over time."""
    if not density:
        return ""
    months_sorted = sorted(density.keys())
    values = [density.get(m, 0) for m in months_sorted]
    max_val = max(values) if values else 1
    blocks = " _.:oO@#"
    sparkline = ""
    for v in values:
        idx = min(len(blocks) - 1, int((v / max_val) * (len(blocks) - 1)))
        sparkline += blocks[idx]
    return sparkline


def truncate_text(text: str, max_len: int = 500) -> str:
    """Truncate text to max_len, adding ellipsis if needed."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def resolve_full_text(
    atom_id: str,
    atom_index: dict[str, dict],
    fallback_content: str,
) -> tuple[str, str]:
    """Resolve the full text and date of an atom by ID."""
    atom = atom_index.get(atom_id)
    if atom:
        content = atom.get("content", fallback_content)
        date = atom.get("source", {}).get("timestamp", "")
        if date:
            # normalize to date-only
            date = date[:10]
        return content, date
    return fallback_content, ""


def generate_report(
    trajectories: list[dict],
    atom_index: dict[str, dict],
) -> tuple[str, list[dict]]:
    """Generate the full markdown report and structured JSONL records."""

    # filter to trajectories with 10+ members, sort by count descending
    qualified = [t for t in trajectories if t.get("count", 0) >= MIN_MEMBERS]
    qualified.sort(key=lambda t: t.get("count", 0), reverse=True)
    top = qualified[:TOP_N]

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_atoms = sum(t.get("count", 0) for t in trajectories)
    total_qualified = sum(t.get("count", 0) for t in qualified)

    # ── Markdown header ───────────────────────────────────────────────────
    md_lines = [
        "# Intention Evolution Report",
        "",
        f"*Generated: {now}*",
        "",
        "## Overview",
        "",
        f"- **Total trajectories analyzed:** {len(trajectories)}",
        f"- **Trajectories with 10+ members:** {len(qualified)}",
        f"- **Top {TOP_N} reported below**",
        f"- **Total prompt atoms across all trajectories:** {total_atoms:,}",
        f"- **Atoms in qualified trajectories:** {total_qualified:,}",
        "",
        "### Status Distribution",
        "",
    ]

    # status counts
    status_counts = Counter(t.get("status", "UNKNOWN") for t in qualified)
    for st, cnt in status_counts.most_common():
        md_lines.append(f"- **{st}:** {cnt} trajectories")
    md_lines.append("")

    # ── Summary table ─────────────────────────────────────────────────────
    md_lines.extend([
        "### Top 30 Trajectories at a Glance",
        "",
        "| # | Label | Count | Span | Status | Activity |",
        "|---|-------|-------|------|--------|----------|",
    ])

    for i, t in enumerate(top, 1):
        label = t.get("intention_label", "unknown")[:50]
        count = t.get("count", 0)
        span_m = t.get("span", {}).get("months", "?")
        status = t.get("status", "?")
        density = t.get("density", {})
        spark = compute_activity_sparkline(density)
        md_lines.append(f"| {i} | {label} | {count} | {span_m}mo | {status} | `{spark}` |")

    md_lines.extend(["", "---", ""])

    # ── Per-trajectory deep dive ──────────────────────────────────────────
    jsonl_records = []

    for i, t in enumerate(top, 1):
        traj_id = t.get("trajectory_id", "unknown")
        label = t.get("intention_label", "unknown")
        status = t.get("status", "UNKNOWN")
        count = t.get("count", 0)
        domain = t.get("domain", "general")
        span = t.get("span", {})
        density = t.get("density", {})
        evolution = t.get("evolution", {})
        top_phrases = t.get("top_phrases", [])

        first_expr = evolution.get("first_expression", {})
        latest_expr = evolution.get("latest_expression", {})

        # resolve full text from atom index
        first_id = first_expr.get("id", "")
        latest_id = latest_expr.get("id", "")
        first_fallback = first_expr.get("content", "(no content)")
        latest_fallback = latest_expr.get("content", "(no content)")

        first_text, first_date = resolve_full_text(first_id, atom_index, first_fallback)
        latest_text, latest_date = resolve_full_text(latest_id, atom_index, latest_fallback)

        # use trajectory date if atom date missing
        if not first_date:
            first_date = first_expr.get("date", span.get("first", "unknown"))
        if not latest_date:
            latest_date = latest_expr.get("date", span.get("latest", "unknown"))

        # concept analysis
        first_concepts = extract_concepts(first_text)
        latest_concepts = extract_concepts(latest_text)

        # compute delta
        delta_text = classify_evolution(first_text, latest_text, first_concepts, latest_concepts)

        # compute projection
        projection = project_future(t, first_concepts, latest_concepts, density)

        # activity trend
        spark = compute_activity_sparkline(density)
        months_sorted = sorted(density.keys())
        peak_month = max(density, key=density.get) if density else "n/a"
        peak_count = density.get(peak_month, 0) if density else 0

        # ── Write markdown section ────────────────────────────────────────
        md_lines.extend([
            f"## {i}. {label}",
            "",
            f"**Trajectory:** `{traj_id}`  ",
            f"**Status:** {status} | **Domain:** {domain} | **Count:** {count} | **Span:** {span.get('first', '?')} to {span.get('latest', '?')} ({span.get('months', '?')} months)  ",
            f"**Top phrases:** {', '.join(top_phrases[:5])}  ",
            f"**Activity:** `{spark}` (peak: {peak_month} with {peak_count} prompts)",
            "",
            "### ORIGINAL ASK",
            f"*{first_date}*",
            "",
            "```",
            truncate_text(first_text, 800),
            "```",
            "",
            "### CURRENT ASK",
            f"*{latest_date}*",
            "",
            "```",
            truncate_text(latest_text, 800),
            "```",
            "",
            "### DELTA",
            "",
        ])
        for line in delta_text.split("\n"):
            md_lines.append(f"- {line}")
        md_lines.extend([
            "",
            "### PROJECTED FUTURE",
            "",
        ])
        for line in projection.split("\n"):
            md_lines.append(f"- {line}")
        md_lines.extend(["", "---", ""])

        # ── Build JSONL record ────────────────────────────────────────────
        jsonl_records.append({
            "trajectory_id": traj_id,
            "rank": i,
            "intention_label": label,
            "status": status,
            "domain": domain,
            "count": count,
            "span_months": span.get("months", 0),
            "span_first": span.get("first", ""),
            "span_latest": span.get("latest", ""),
            "original_ask": {
                "id": first_id,
                "date": first_date,
                "text": first_text[:2000],
            },
            "current_ask": {
                "id": latest_id,
                "date": latest_date,
                "text": latest_text[:2000],
            },
            "delta": {
                "new_concepts": sorted(latest_concepts - first_concepts)[:30],
                "dropped_concepts": sorted(first_concepts - latest_concepts)[:30],
                "persistent_concepts": sorted(first_concepts & latest_concepts)[:30],
                "first_sophistication": compute_sophistication(first_text),
                "latest_sophistication": compute_sophistication(latest_text),
                "summary": delta_text,
            },
            "projected_future": projection,
            "activity": {
                "density": density,
                "peak_month": peak_month,
                "peak_count": peak_count,
                "sparkline": spark,
            },
            "top_phrases": top_phrases[:5],
        })

    # ── Synthesis section ─────────────────────────────────────────────────
    md_lines.extend([
        "## Synthesis: What This Reveals",
        "",
    ])

    evolved = [r for r in jsonl_records if r["status"] == "EVOLVED"]
    dormant = [r for r in jsonl_records if r["status"] == "DORMANT"]
    unresolved = [r for r in jsonl_records if r["status"] == "UNRESOLVED"]
    crystallized = [r for r in jsonl_records if r["status"] == "CRYSTALLIZED"]

    if evolved:
        md_lines.extend([
            "### Active Evolution Threads",
            "",
            "These trajectories show clear directional movement -- the asks are not just repeating, they are transforming:",
            "",
        ])
        for r in evolved:
            md_lines.append(f"- **{r['intention_label']}** ({r['count']} prompts, {r['span_months']}mo): {r['delta']['summary'].split(chr(10))[0]}")
        md_lines.append("")

    if unresolved:
        md_lines.extend([
            "### Unresolved Loops",
            "",
            "These keep recurring without landing. They represent the system's persistent friction points:",
            "",
        ])
        for r in unresolved:
            md_lines.append(f"- **{r['intention_label']}** ({r['count']} prompts): {r['projected_future'].split(chr(10))[0]}")
        md_lines.append("")

    if dormant:
        md_lines.extend([
            "### Dormant Threads",
            "",
            "Quiet now. Some absorbed, some waiting for reactivation:",
            "",
        ])
        for r in dormant:
            md_lines.append(f"- **{r['intention_label']}** ({r['count']} prompts, last active {r['span_latest']})")
        md_lines.append("")

    if crystallized:
        md_lines.extend([
            "### Crystallized Patterns",
            "",
            "Converged to formula. Automation candidates:",
            "",
        ])
        for r in crystallized:
            md_lines.append(f"- **{r['intention_label']}** ({r['count']} prompts)")
        md_lines.append("")

    # overall narrative
    total_evolved_atoms = sum(r["count"] for r in evolved)
    total_dormant_atoms = sum(r["count"] for r in dormant)

    md_lines.extend([
        "### The Arc",
        "",
        f"Across {len(top)} major trajectories ({sum(r['count'] for r in jsonl_records):,} total prompts):",
        "",
        f"- **{len(evolved)} actively evolving** ({total_evolved_atoms:,} atoms) -- these are the live wires, the asks that keep transforming.",
        f"- **{len(dormant)} dormant** ({total_dormant_atoms:,} atoms) -- season-dependent or absorbed into larger systems.",
        f"- **{len(unresolved)} unresolved** -- recurring friction without resolution.",
        f"- **{len(crystallized)} crystallized** -- formula locked, ready for automation.",
        "",
        "The dominant direction: from **asking AI to write things** toward **asking AI to build systems that write things**.",
        "From consumer to architect. From output to infrastructure.",
        "",
        "---",
        f"*Report generated from {len(trajectories)} trajectories, {total_atoms:,} prompt atoms.*",
        "",
    ])

    return "\n".join(md_lines), jsonl_records


def main() -> None:
    print("Loading prompt atoms...")
    atoms = load_jsonl(ATOMS_PATH)
    short_atoms = load_jsonl(SHORT_ATOMS_PATH)
    all_atoms = atoms + short_atoms
    print(f"  Loaded {len(atoms):,} full atoms + {len(short_atoms):,} short atoms = {len(all_atoms):,} total")

    print("Building atom index...")
    atom_index = build_atom_index(all_atoms)
    print(f"  Indexed {len(atom_index):,} unique atom IDs")

    print("Loading trajectories...")
    trajectories = load_jsonl(TRAJECTORIES_PATH)
    print(f"  Loaded {len(trajectories)} trajectories")

    print(f"Generating report (top {TOP_N} with {MIN_MEMBERS}+ members)...")
    md_report, jsonl_records = generate_report(trajectories, atom_index)

    # write markdown
    MD_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(MD_OUTPUT, "w", encoding="utf-8") as f:
        f.write(md_report)
    print(f"  Markdown report: {MD_OUTPUT}")

    # write JSONL
    with open(JSONL_OUTPUT, "w", encoding="utf-8") as f:
        for record in jsonl_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"  JSONL output: {JSONL_OUTPUT}")

    # summary stats
    statuses = Counter(r["status"] for r in jsonl_records)
    print(f"\nReport complete: {len(jsonl_records)} trajectories")
    for st, cnt in statuses.most_common():
        print(f"  {st}: {cnt}")


if __name__ == "__main__":
    main()
