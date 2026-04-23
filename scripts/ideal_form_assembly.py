#!/usr/bin/env python3
"""Ideal Form Assembly — Cubist prompt analysis.

Each prompt is a facet of an ideal form — the same intention viewed from
a different angle. This script assembles facets into forms, measures
completeness (how many angles explored), materialization (has any facet
been built), and coherence (do the facets describe the same object).

The unit of analysis is not the prompt. It is the FORM.

Usage: python3 scripts/ideal_form_assembly.py
"""

import hashlib
import json
import os
import re
from collections import defaultdict
from pathlib import Path

ATOMS_PATH = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/prompt-atoms.jsonl"
)
SHORT_PATH = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/prompt-atoms-short.jsonl"
)
TRAJECTORIES_PATH = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/intention-trajectories.jsonl"
)
DEEP_PATH = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/trajectory-deep-analysis.jsonl"
)
OUTPUT_PATH = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/ideal-forms.jsonl"
)
REPORT_PATH = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/IDEAL-FORMS-REPORT.md"
)

STOPWORDS = {
    "this", "that", "with", "from", "have", "been", "will", "would", "could",
    "should", "what", "when", "where", "which", "while", "about", "their",
    "them", "they", "there", "here", "some", "than", "then", "also", "into",
    "more", "very", "just", "like", "make", "need", "want", "know", "each",
    "please", "help", "using", "used", "does", "done", "based", "take",
    "sure", "look", "give", "well", "back", "good", "your", "these",
    "those", "being", "such", "after", "before", "between", "because",
    "through", "during", "other", "only", "same", "still", "most",
    "file", "files", "code", "tool", "following", "first", "last", "next",
}

# Viewing angles — what perspective does a facet bring?
ANGLE_PATTERNS = {
    "functional": ["build", "create", "implement", "make", "develop", "construct", "generate"],
    "operational": ["how to", "how do", "schedule", "run", "execute", "manage", "maintain"],
    "architectural": ["design", "architect", "structure", "organize", "system", "framework", "schema"],
    "governance": ["policy", "sop", "protocol", "governance", "compliance", "standard", "rule"],
    "analytical": ["analyze", "review", "audit", "evaluate", "assess", "measure", "compare"],
    "creative": ["write", "draft", "compose", "craft", "narrative", "story", "essay"],
    "research": ["research", "investigate", "study", "explore", "discover", "find", "learn"],
    "identity": ["resume", "portfolio", "profile", "brand", "personal", "career", "presentation"],
    "relational": ["email", "outreach", "connect", "network", "collaborate", "community"],
    "pedagogical": ["teach", "explain", "curriculum", "course", "student", "assignment", "lesson"],
    "economic": ["revenue", "monetize", "business", "client", "pricing", "market", "sell"],
    "technical": ["debug", "fix", "refactor", "optimize", "test", "deploy", "configure"],
}


def classify_angle(content: str) -> str:
    lower = content.lower()[:500]
    scores = {}
    for angle, keywords in ANGLE_PATTERNS.items():
        scores[angle] = sum(1 for k in keywords if k in lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unclassified"


def extract_essence(content: str) -> set:
    """Extract the essential concepts — what is this facet ABOUT, not HOW it asks."""
    words = re.sub(r"[^a-z\s]", " ", content.lower()[:1000]).split()
    # Filter for nouns/concepts (longer words, not verbs/stopwords)
    concepts = {w for w in words if len(w) > 4 and w not in STOPWORDS}
    # Remove common verb forms
    verbs = {"create", "build", "write", "review", "check", "update", "implement",
             "deploy", "analyze", "design", "explain", "describe", "provide",
             "generate", "develop", "configure", "setup", "install", "research"}
    return concepts - verbs


def load_jsonl(path):
    items = []
    if path.exists():
        with open(path) as f:
            for line in f:
                if line.strip():
                    items.append(json.loads(line))
    return items


def main():
    print("Loading atoms...")
    atoms = load_jsonl(ATOMS_PATH) + load_jsonl(SHORT_PATH)
    print(f"  {len(atoms)} atoms loaded")

    # Load existing trajectories as seed clusters
    trajectories = load_jsonl(TRAJECTORIES_PATH) + load_jsonl(DEEP_PATH)
    print(f"  {len(trajectories)} trajectories loaded")

    # Build atom index
    atoms_by_id = {a["id"]: a for a in atoms}

    # Phase 1: Start with trajectory clusters as proto-forms
    # Each trajectory is already a cluster of related prompts
    proto_forms = []
    assigned = set()

    for traj in trajectories:
        member_ids = traj.get("member_ids", [])
        members = [atoms_by_id[mid] for mid in member_ids if mid in atoms_by_id]
        if len(members) < 2:
            continue

        # Analyze the angles represented in this cluster
        angles = defaultdict(int)
        domains = defaultdict(int)
        essences = defaultdict(int)
        dates = []

        for m in members:
            angle = classify_angle(m.get("content", ""))
            angles[angle] += 1
            domains[m.get("domain", "general")] += 1
            for concept in extract_essence(m.get("content", "")):
                essences[concept] += 1
            ts = m.get("source", {}).get("timestamp", "")
            if ts and not ts.startswith("1969"):
                dates.append(ts[:10])

        # The ESSENCE of this form = the top concepts that appear across multiple facets
        core_concepts = sorted(essences.items(), key=lambda x: -x[1])
        # Concepts appearing in 30%+ of facets are core to the form
        threshold = max(2, len(members) * 0.3)
        core = [c for c, n in core_concepts if n >= threshold][:10]

        # Form label from top 3 core concepts
        label = " + ".join(core[:3]) if core else traj.get("intention_label", "unnamed")

        # Completeness: how many distinct angles are represented?
        completeness = len([a for a in angles if angles[a] > 0]) / max(len(ANGLE_PATTERNS), 1)

        # Materialization: check if any facet is status=VERIFIED_DONE or ANSWERED with high confidence
        materialized_count = sum(1 for m in members if m.get("status") in ("VERIFIED_DONE", "ACTUALLY_DONE"))
        answered_count = sum(1 for m in members if m.get("status") == "ANSWERED")

        proto_forms.append({
            "form_id": traj.get("trajectory_id", f"form-{hashlib.sha256(label.encode()).hexdigest()[:12]}"),
            "label": label,
            "core_concepts": core,
            "facet_count": len(members),
            "angle_distribution": dict(angles),
            "completeness": round(completeness, 3),
            "materialization": {
                "verified_done": materialized_count,
                "answered": answered_count,
                "total_facets": len(members),
                "materialization_rate": round(materialized_count / max(len(members), 1), 3),
            },
            "domains": dict(domains),
            "span": {
                "first": min(dates) if dates else None,
                "latest": max(dates) if dates else None,
                "months": len(set(d[:7] for d in dates)) if dates else 0,
            },
            "status": traj.get("status", "UNKNOWN"),
            "facet_ids": member_ids,
            "first_facet": members[0].get("content", "")[:300] if members else "",
            "latest_facet": members[-1].get("content", "")[:300] if members else "",
        })

        for mid in member_ids:
            assigned.add(mid)

    # Phase 2: Merge proto-forms that share core concepts
    # Two forms with 50%+ concept overlap are views of the same ideal object
    merged = []
    used = set()

    for i, form_a in enumerate(proto_forms):
        if i in used:
            continue
        group = [form_a]
        concepts_a = set(form_a["core_concepts"])

        for j, form_b in enumerate(proto_forms):
            if j <= i or j in used:
                continue
            concepts_b = set(form_b["core_concepts"])
            if not concepts_a or not concepts_b:
                continue
            overlap = len(concepts_a & concepts_b) / max(len(concepts_a | concepts_b), 1)
            if overlap >= 0.5:
                group.append(form_b)
                used.add(j)
                concepts_a |= concepts_b

        if len(group) > 1:
            # Merge into single form
            all_facets = []
            all_concepts = defaultdict(int)
            all_angles = defaultdict(int)
            all_domains = defaultdict(int)
            all_dates = []

            for g in group:
                all_facets.extend(g["facet_ids"])
                for c in g["core_concepts"]:
                    all_concepts[c] += 1
                for a, n in g["angle_distribution"].items():
                    all_angles[a] += n
                for d, n in g["domains"].items():
                    all_domains[d] += n
                if g["span"]["first"]:
                    all_dates.append(g["span"]["first"])
                if g["span"]["latest"]:
                    all_dates.append(g["span"]["latest"])

            merged_core = sorted(all_concepts, key=lambda c: -all_concepts[c])[:10]
            merged_label = " + ".join(merged_core[:3])
            completeness = len([a for a in all_angles if all_angles[a] > 0]) / max(len(ANGLE_PATTERNS), 1)

            merged.append({
                "form_id": f"form-merged-{hashlib.sha256(merged_label.encode()).hexdigest()[:12]}",
                "label": merged_label,
                "core_concepts": merged_core,
                "facet_count": len(set(all_facets)),
                "angle_distribution": dict(all_angles),
                "completeness": round(completeness, 3),
                "materialization": {
                    "verified_done": sum(g["materialization"]["verified_done"] for g in group),
                    "answered": sum(g["materialization"]["answered"] for g in group),
                    "total_facets": len(set(all_facets)),
                },
                "domains": dict(all_domains),
                "span": {
                    "first": min(all_dates) if all_dates else None,
                    "latest": max(all_dates) if all_dates else None,
                    "months": len(set(d[:7] for d in all_dates)),
                },
                "merged_from": [g["form_id"] for g in group],
                "facet_ids": list(set(all_facets)),
            })
        else:
            merged.append(form_a)

    # Sort by facet count descending
    merged.sort(key=lambda f: -f["facet_count"])

    # Phase 3: Write outputs
    print(f"\nWriting {len(merged)} ideal forms...")
    with open(OUTPUT_PATH, "w") as f:
        for form in merged:
            f.write(json.dumps(form, ensure_ascii=False) + "\n")

    # Phase 4: Generate markdown report
    lines = [
        "# Ideal Forms Report",
        "",
        "Each prompt is a facet of an ideal form — the same intention viewed from",
        "a different angle. This report maps the forms, their completeness, and",
        "their materialization in reality.",
        "",
        f"**{len(merged)} ideal forms** assembled from {len(atoms)} prompt facets.",
        f"**{len(assigned)} facets assigned** ({100*len(assigned)/max(len(atoms),1):.1f}% coverage).",
        f"**{len(atoms) - len(assigned)} orphan facets** (not yet assigned to any form).",
        "",
        "---",
        "",
    ]

    # Top forms
    lines.append("## Top 30 Ideal Forms by Facet Count")
    lines.append("")

    for i, form in enumerate(merged[:30], 1):
        angles_present = len([a for a in form["angle_distribution"] if form["angle_distribution"][a] > 0])
        lines.append(f"### {i}. {form['label']}")
        lines.append("")
        lines.append(f"- **Facets**: {form['facet_count']}")
        lines.append(f"- **Angles explored**: {angles_present}/{len(ANGLE_PATTERNS)} ({form['completeness']*100:.0f}% complete)")
        lines.append(f"- **Span**: {form['span'].get('first', '?')} → {form['span'].get('latest', '?')} ({form['span'].get('months', 0)} months)")
        lines.append(f"- **Core concepts**: {', '.join(form['core_concepts'][:7])}")

        # Angle breakdown
        angles = form["angle_distribution"]
        if angles:
            sorted_angles = sorted(angles.items(), key=lambda x: -x[1])
            angle_str = " | ".join(f"{a}: {n}" for a, n in sorted_angles if n > 0)
            lines.append(f"- **Angle distribution**: {angle_str}")

        mat = form.get("materialization", {})
        if mat:
            lines.append(f"- **Materialization**: {mat.get('verified_done', 0)} verified done, {mat.get('answered', 0)} answered, {mat.get('total_facets', 0)} total")

        # First and latest facets
        if form.get("first_facet"):
            lines.append(f"- **First facet**: {form['first_facet'][:150]}...")
        if form.get("latest_facet"):
            lines.append(f"- **Latest facet**: {form['latest_facet'][:150]}...")

        lines.append("")

    # Completeness analysis
    lines.append("---")
    lines.append("")
    lines.append("## Completeness Analysis")
    lines.append("")
    lines.append("| Completeness | Count | What it means |")
    lines.append("|---|---|---|")

    comp_buckets = defaultdict(int)
    for f in merged:
        c = f["completeness"]
        if c >= 0.75:
            comp_buckets["75-100%"] += 1
        elif c >= 0.5:
            comp_buckets["50-74%"] += 1
        elif c >= 0.25:
            comp_buckets["25-49%"] += 1
        else:
            comp_buckets["0-24%"] += 1

    lines.append(f"| 75-100% | {comp_buckets.get('75-100%', 0)} | Well-explored — most angles covered |")
    lines.append(f"| 50-74% | {comp_buckets.get('50-74%', 0)} | Partially explored — key angles missing |")
    lines.append(f"| 25-49% | {comp_buckets.get('25-49%', 0)} | Narrowly explored — few angles attempted |")
    lines.append(f"| 0-24% | {comp_buckets.get('0-24%', 0)} | Barely touched — single-angle view only |")
    lines.append("")

    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(lines))

    # Stats
    print(f"\n{'=' * 60}")
    print(f"IDEAL FORM ASSEMBLY RESULTS")
    print(f"{'=' * 60}")
    print(f"Total ideal forms: {len(merged)}")
    print(f"Facets assigned: {len(assigned)} / {len(atoms)} ({100*len(assigned)/max(len(atoms),1):.1f}%)")
    print(f"Orphan facets: {len(atoms) - len(assigned)}")
    print(f"\nCompleteness distribution:")
    for bucket, count in sorted(comp_buckets.items()):
        print(f"  {bucket}: {count}")
    print(f"\nTop 10 ideal forms:")
    for form in merged[:10]:
        angles = len([a for a in form["angle_distribution"] if form["angle_distribution"][a] > 0])
        print(f"  {form['facet_count']:4d} facets | {angles:2d} angles | {form['label'][:60]}")
    print(f"\nOutput: {OUTPUT_PATH}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
