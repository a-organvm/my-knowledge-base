#!/usr/bin/env python3
"""Trajectory Deep Analysis — Second Pass.

Recovers atoms missed by the first-pass trajectory engine (bigram-only matching).
Uses looser keyword clustering, partition-aware grouping, and produces detailed
evolution reports for all trajectories (existing + newly discovered).

First pass: 113 trajectories, 2,441 atoms covered (16.8% of 14,537).
Target: 50%+ coverage by relaxing to single-keyword matching within partitions.

Usage: python3 scripts/trajectory_deep_analysis.py
"""

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────

DATA_DIR = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms"
)
ATOMS_PATH = DATA_DIR / "prompt-atoms.jsonl"
SHORT_PATH = DATA_DIR / "prompt-atoms-short.jsonl"
EXISTING_TRAJ_PATH = DATA_DIR / "intention-trajectories.jsonl"
OUTPUT_PATH = DATA_DIR / "trajectory-deep-analysis.jsonl"

# ── Extended stopwords ─────────────────────────────────────────────────────────
# Broader than first pass — includes common short prompts and filler

STOPWORDS = {
    # Function words
    "this", "that", "with", "from", "have", "been", "will", "would", "could",
    "should", "what", "when", "where", "which", "while", "about", "their",
    "them", "they", "there", "here", "some", "than", "then", "also", "into",
    "more", "very", "just", "like", "make", "need", "want", "know", "each",
    "please", "help", "using", "used", "does", "done", "based", "take",
    "sure", "look", "give", "well", "back", "good", "your", "these",
    "those", "being", "such", "after", "before", "between", "because",
    "through", "during", "above", "below", "other", "only", "same",
    "still", "most", "over", "under", "again", "once", "many", "much",
    "every", "both", "even", "were", "came", "come", "going", "told",
    "think", "keep", "following", "first", "last", "next", "current",
    "file", "files", "code", "tool", "show", "list", "work", "right",
    # Contractions
    "can't", "don't", "it's", "i'm", "let's", "you're", "that's",
    "here's", "there's", "didn't", "doesn't", "wasn't", "aren't",
    "won't", "isn't", "haven't", "couldn't", "wouldn't",
    # Common AI prompt filler
    "write", "create", "generate", "explain", "describe", "provide",
    "given", "example", "output", "input", "result", "value",
    "function", "return", "class", "method", "object", "array",
    "string", "number", "boolean", "variable", "parameter",
    "error", "issue", "problem", "solution", "answer", "question",
    "update", "change", "modify", "check", "build", "setup",
    "start", "stop", "enable", "disable", "something", "anything",
    "everything", "nothing", "things", "stuff", "point", "really",
    "actually", "basically", "simply", "already", "instead", "always",
    "never", "might", "maybe", "seems", "since", "until", "without",
    "within", "across", "along", "among", "around", "toward",
    "shall", "must", "shall", "whole", "whose", "either", "neither",
    "whether", "however", "whatever", "whenever", "wherever",
    "rather", "quite", "fairly", "pretty", "almost", "enough",
    "below", "above", "beside", "behind", "beyond", "except",
    # Common tech generics (too broad for clustering)
    "https", "http", "data", "type", "name", "line", "text",
    "test", "true", "false", "null", "none", "path", "command",
    "server", "client", "local", "global", "state", "config",
}


# ── Union-Find ─────────────────────────────────────────────────────────────────

class UnionFind:
    """Weighted union-find with path compression."""

    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1


# ── Text processing ───────────────────────────────────────────────────────────

def extract_keywords(text: str, min_len: int = 5) -> set:
    """Extract significant single keywords (length > min_len, not stopwords)."""
    text = re.sub(r"[^a-z\s]", " ", text.lower()[:2000])
    return {w for w in text.split() if len(w) >= min_len and w not in STOPWORDS}


def extract_all_words(text: str) -> list:
    """Extract all meaningful words from text for analysis."""
    text = re.sub(r"[^a-z\s]", " ", text.lower()[:3000])
    return [w for w in text.split() if len(w) >= 3 and w not in STOPWORDS]


def parse_date(ts: str) -> str:
    if not ts or ts.startswith("1969"):
        return ""
    return ts[:10]


def avg_word_length(text: str) -> float:
    """Average word length as rough sophistication proxy."""
    words = re.sub(r"[^a-z\s]", " ", text.lower()).split()
    words = [w for w in words if len(w) >= 2]
    return sum(len(w) for w in words) / max(len(words), 1)


def jargon_density(text: str) -> float:
    """Fraction of words with length >= 8 (domain-specific / technical terms)."""
    words = re.sub(r"[^a-z\s]", " ", text.lower()).split()
    words = [w for w in words if len(w) >= 2]
    if not words:
        return 0.0
    return sum(1 for w in words if len(w) >= 8) / len(words)


# ── Evolution analysis ─────────────────────────────────────────────────────────

def compute_evolution_report(members: list) -> dict:
    """Compute detailed evolution report for a trajectory's member atoms."""
    sorted_m = sorted(members, key=lambda m: m["date"] if m["date"] else "9999")
    first = sorted_m[0]
    latest = sorted_m[-1]

    first_content = first["content"][:500]
    latest_content = latest["content"][:500]

    # Word-level diff
    first_words = set(extract_all_words(first["content"]))
    latest_words = set(extract_all_words(latest["content"]))
    concepts_added = sorted(w for w in (latest_words - first_words) if len(w) >= 5)[:20]
    concepts_dropped = sorted(w for w in (first_words - latest_words) if len(w) >= 5)[:15]

    # Sophistication delta
    first_awl = avg_word_length(first["content"])
    latest_awl = avg_word_length(latest["content"])
    first_jd = jargon_density(first["content"])
    latest_jd = jargon_density(latest["content"])

    # Periodicity classification
    dates = sorted(d for m in members for d in [m["date"]] if d)
    periodicity = classify_periodicity(dates)

    # Predicted next prompt (trending concepts in latest 25%)
    predicted = compute_prediction(sorted_m)

    return {
        "first_full": first_content,
        "first_date": first["date"],
        "first_id": first["id"],
        "latest_full": latest_content,
        "latest_date": latest["date"],
        "latest_id": latest["id"],
        "concepts_added": concepts_added,
        "concepts_dropped": concepts_dropped,
        "sophistication_delta": {
            "avg_word_length_first": round(first_awl, 2),
            "avg_word_length_latest": round(latest_awl, 2),
            "awl_change": round(latest_awl - first_awl, 2),
            "jargon_density_first": round(first_jd, 3),
            "jargon_density_latest": round(latest_jd, 3),
            "jd_change": round(latest_jd - first_jd, 3),
        },
        "periodicity": periodicity,
        "predicted_next_prompt": predicted,
    }


def classify_periodicity(dates: list) -> str:
    """Classify temporal pattern of the trajectory's activity."""
    if len(dates) < 2:
        return "insufficient_data"

    try:
        dts = [datetime.strptime(d, "%Y-%m-%d") for d in dates if d]
    except ValueError:
        return "unknown"

    if len(dts) < 2:
        return "insufficient_data"

    dts.sort()
    span_days = (dts[-1] - dts[0]).days
    if span_days == 0:
        return "single_burst"

    # Compute gaps between consecutive activities
    gaps = [(dts[i + 1] - dts[i]).days for i in range(len(dts) - 1)]
    avg_gap = sum(gaps) / len(gaps)
    gap_std = math.sqrt(sum((g - avg_gap) ** 2 for g in gaps) / len(gaps)) if len(gaps) > 1 else 0

    # Dormancy check: latest activity > 90 days ago
    now = datetime(2026, 4, 23)
    days_since_last = (now - dts[-1]).days
    if days_since_last > 90:
        return "dormant"

    # Regularity coefficient (CV = std/mean)
    cv = gap_std / avg_gap if avg_gap > 0 else 0

    if avg_gap <= 10 and cv < 0.8:
        return "weekly"
    elif avg_gap <= 14 and cv < 1.0:
        return "biweekly"
    elif avg_gap <= 45 and cv < 1.2:
        return "monthly_burst"
    elif cv > 2.0:
        return "sporadic"
    elif span_days > 180 and cv < 1.5:
        return "steady"
    elif span_days > 90:
        return "seasonal"
    else:
        return "steady"


def compute_prediction(sorted_members: list) -> str:
    """Predict next prompt direction from trending concepts in latest quartile."""
    if len(sorted_members) < 3:
        return "Insufficient data for projection"

    quartile_size = max(len(sorted_members) // 4, 1)
    late = sorted_members[-quartile_size:]
    early = sorted_members[: len(sorted_members) // 2]

    early_words = Counter()
    for m in early:
        for w in extract_all_words(m["content"]):
            early_words[w] += 1

    late_words = Counter()
    for m in late:
        for w in extract_all_words(m["content"]):
            late_words[w] += 1

    # Words appearing in late but not early, or significantly more frequent
    trending = {}
    for w, count in late_words.items():
        if len(w) < 5:
            continue
        early_count = early_words.get(w, 0)
        if early_count == 0:
            trending[w] = count
        elif count / max(len(late), 1) > 2 * early_count / max(len(early), 1):
            trending[w] = count

    if trending:
        top = sorted(trending, key=trending.get, reverse=True)[:12]
        return f"Trending toward: {', '.join(top)}"
    return "Trajectory stable — expect repetition of current expression"


def classify_status(members: list) -> str:
    """Classify trajectory status: DORMANT, CRYSTALLIZED, EVOLVED, UNRESOLVED, OPEN."""
    dates = [m["date"] for m in members if m["date"]]
    if not dates:
        return "OPEN"
    latest = max(dates)

    try:
        latest_dt = datetime.strptime(latest, "%Y-%m-%d")
        now_dt = datetime(2026, 4, 23)
        if (now_dt - latest_dt).days > 90:
            return "DORMANT"
    except ValueError:
        pass

    sorted_m = sorted(members, key=lambda m: m["date"] if m["date"] else "9999")
    if len(sorted_m) >= 5:
        last5 = [
            set(re.sub(r"[^a-z\s]", " ", m["content"][:200].lower()).split())
            for m in sorted_m[-5:]
        ]
        overlaps = []
        for i in range(len(last5)):
            for j in range(i + 1, len(last5)):
                union = last5[i] | last5[j]
                if union:
                    overlaps.append(len(last5[i] & last5[j]) / len(union))
        avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0
        if avg_overlap > 0.5:
            return "CRYSTALLIZED"

    first_words = (
        set(re.sub(r"[^a-z\s]", " ", sorted_m[0]["content"][:500].lower()).split())
        - STOPWORDS
    )
    latest_words = (
        set(re.sub(r"[^a-z\s]", " ", sorted_m[-1]["content"][:500].lower()).split())
        - STOPWORDS
    )
    if first_words and latest_words:
        overlap = len(first_words & latest_words) / max(len(first_words | latest_words), 1)
        if overlap < 0.3:
            return "EVOLVED"

    return "UNRESOLVED"


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("TRAJECTORY DEEP ANALYSIS — SECOND PASS")
    print("=" * 72)

    # ── Phase 1: Load all data ──────────────────────────────────────────────

    print("\nPhase 1: Loading data...")

    # Load all atoms
    atoms_by_id = {}
    for path in [ATOMS_PATH, SHORT_PATH]:
        if path.exists():
            with open(path) as f:
                for line in f:
                    if line.strip():
                        a = json.loads(line)
                        atoms_by_id[a["id"]] = a
    total_atoms = len(atoms_by_id)
    print(f"  Loaded {total_atoms} unique atoms")

    # Load existing trajectories
    existing_trajectories = []
    covered_ids = set()
    if EXISTING_TRAJ_PATH.exists():
        with open(EXISTING_TRAJ_PATH) as f:
            for line in f:
                if line.strip():
                    t = json.loads(line)
                    existing_trajectories.append(t)
                    covered_ids.update(t.get("member_ids", []))
    print(f"  Loaded {len(existing_trajectories)} existing trajectories covering {len(covered_ids)} atoms")

    uncovered_ids = set(atoms_by_id.keys()) - covered_ids
    print(f"  Uncovered atoms: {len(uncovered_ids)}")

    # ── Phase 2: Build records for uncovered atoms ──────────────────────────

    print("\nPhase 2: Building keyword index for uncovered atoms...")

    records = []
    idx_map = {}  # atom_id -> record index
    for i, aid in enumerate(sorted(uncovered_ids)):
        a = atoms_by_id[aid]
        ts = a.get("source", {}).get("timestamp", "") or ""
        date = parse_date(ts)
        keywords = extract_keywords(a.get("content", ""))
        domain = a.get("domain", "general")
        ptype = a.get("prompt_type", "unknown")
        partition = f"{domain}|{ptype}"

        records.append({
            "idx": i,
            "id": aid,
            "date": date,
            "domain": domain,
            "prompt_type": ptype,
            "partition": partition,
            "content": a.get("content", "")[:2000],
            "title": a.get("title", ""),
            "keywords": keywords,
        })
        idx_map[aid] = i

    # ── Phase 3: Inverted keyword index within partitions ───────────────────

    print("\nPhase 3: Building partitioned keyword index...")

    # Structure: (partition, keyword) -> set of record indices
    kw_index = defaultdict(set)
    for r in records:
        for kw in r["keywords"]:
            kw_index[(r["partition"], kw)].add(r["idx"])

    # Filter: keyword must appear in 2+ atoms within partition, but not 60%+ of partition
    partition_sizes = Counter(r["partition"] for r in records)
    filtered_kw = {}
    for key, idxs in kw_index.items():
        partition, kw = key
        psize = partition_sizes[partition]
        max_freq = max(int(psize * 0.6), 200)
        if 2 <= len(idxs) <= max_freq:
            filtered_kw[key] = idxs

    total_kw_entries = len(kw_index)
    filtered_count = len(filtered_kw)
    print(f"  Total (partition, keyword) pairs: {total_kw_entries}")
    print(f"  After frequency filter: {filtered_count}")

    # ── Phase 4: Union-Find clustering ──────────────────────────────────────

    print("\nPhase 4: Clustering via union-find (2+ shared keywords in partition)...")

    uf = UnionFind()

    # For each (partition, keyword), union atoms that share 2+ keywords
    # within the same partition
    # Group keywords by partition for cross-checking
    partition_kws = defaultdict(list)  # partition -> list of (keyword, idx_set)
    for (partition, kw), idxs in filtered_kw.items():
        partition_kws[partition].append((kw, idxs))

    cluster_unions = 0
    for partition, kw_list in partition_kws.items():
        if len(kw_list) < 2:
            continue

        # For each pair of atoms that co-occur in any keyword,
        # check if they share 2+ keywords total.
        # Build per-atom keyword sets within this partition.
        atom_kws_in_partition = defaultdict(set)
        for kw, idxs in kw_list:
            for idx in idxs:
                atom_kws_in_partition[idx].add(kw)

        # Sort atoms by number of keywords (process richest first for efficiency)
        atoms_sorted = sorted(atom_kws_in_partition.keys(),
                              key=lambda x: len(atom_kws_in_partition[x]),
                              reverse=True)

        # For each keyword, union pairs of atoms sharing 2+ keywords
        for kw, idxs in kw_list:
            idx_list = sorted(idxs)
            if len(idx_list) > 150:
                # For high-frequency keywords, sample to avoid O(n^2) blowup
                idx_list = idx_list[:150]
            for i in range(len(idx_list)):
                a_idx = idx_list[i]
                a_kws = atom_kws_in_partition[a_idx]
                if len(a_kws) < 2:
                    continue
                for j in range(i + 1, min(i + 50, len(idx_list))):
                    b_idx = idx_list[j]
                    b_kws = atom_kws_in_partition[b_idx]
                    shared = a_kws & b_kws
                    if len(shared) >= 2:
                        uf.union(a_idx, b_idx)
                        cluster_unions += 1

    print(f"  Union operations: {cluster_unions}")

    # Collect clusters
    new_clusters = defaultdict(list)
    for r in records:
        root = uf.find(r["idx"])
        new_clusters[root].append(r)

    # Filter: need 2+ members with at least 1 date
    valid_new_clusters = {}
    for root, members in new_clusters.items():
        if len(members) < 2:
            continue
        dates = [m["date"] for m in members if m["date"]]
        if not dates:
            continue
        valid_new_clusters[root] = members

    # Also include singletons in same-partition with identical keyword overlap
    # (catch very short prompts that share exact wording)
    singleton_count = sum(1 for members in new_clusters.values() if len(members) == 1)
    print(f"  Raw clusters: {len(new_clusters)} (incl. {singleton_count} singletons)")
    print(f"  Valid clusters (2+ members, has dates): {len(valid_new_clusters)}")

    # ── Phase 5: Build new trajectories ─────────────────────────────────────

    print("\nPhase 5: Building new trajectories...")

    new_trajectories = []
    new_covered = set()

    for root, members in valid_new_clusters.items():
        dates = [m["date"] for m in members if m["date"]]
        months = set(d[:7] for d in dates)

        sorted_members = sorted(members, key=lambda m: m["date"] if m["date"] else "9999")
        first = sorted_members[0]
        latest = sorted_members[-1]

        # Density
        density = defaultdict(int)
        for m in members:
            if m["date"]:
                density[m["date"][:7]] += 1

        # Top keywords
        all_kws = Counter()
        for m in members:
            for kw in m["keywords"]:
                all_kws[kw] += 1
        top_kws = all_kws.most_common(8)
        label = " / ".join(kw for kw, _ in top_kws[:3])
        if not label:
            label = f"{members[0]['domain']}:{members[0]['prompt_type']}"

        # Deterministic ID
        member_ids = sorted(m["id"] for m in members)
        traj_id = "traj-deep-" + hashlib.sha256("|".join(member_ids).encode()).hexdigest()[:12]

        # Domain (majority)
        domain_counts = Counter(m["domain"] for m in members)
        primary_domain = domain_counts.most_common(1)[0][0]

        # Prompt type (majority)
        ptype_counts = Counter(m["prompt_type"] for m in members)
        primary_ptype = ptype_counts.most_common(1)[0][0]

        status = classify_status(members)

        # Evolution report
        evolution = compute_evolution_report(members)

        new_trajectories.append({
            "trajectory_id": traj_id,
            "intention_label": label,
            "pass": "deep_analysis_v2",
            "status": status,
            "span": {
                "first": min(dates) if dates else "",
                "latest": max(dates) if dates else "",
                "months": len(months),
            },
            "count": len(members),
            "domain": primary_domain,
            "prompt_type": primary_ptype,
            "evolution_report": evolution,
            "top_keywords": [kw for kw, _ in top_kws],
            "member_ids": member_ids,
            "density": dict(sorted(density.items())),
        })
        new_covered.update(member_ids)

    new_trajectories.sort(key=lambda t: -t["count"])
    print(f"  New trajectories: {len(new_trajectories)}")
    print(f"  Atoms in new trajectories: {len(new_covered)}")

    # ── Phase 6: Evolution reports for EXISTING trajectories ────────────────

    print("\nPhase 6: Computing evolution reports for existing trajectories...")

    existing_reports = []
    for t in existing_trajectories:
        # Reconstruct member data from atoms_by_id
        members = []
        for mid in t.get("member_ids", []):
            if mid in atoms_by_id:
                a = atoms_by_id[mid]
                ts = a.get("source", {}).get("timestamp", "") or ""
                members.append({
                    "id": mid,
                    "date": parse_date(ts),
                    "content": a.get("content", "")[:2000],
                    "domain": a.get("domain", "general"),
                    "prompt_type": a.get("prompt_type", "unknown"),
                })

        if len(members) < 2:
            continue

        evolution = compute_evolution_report(members)

        existing_reports.append({
            "trajectory_id": t["trajectory_id"],
            "intention_label": t.get("intention_label", ""),
            "pass": "evolution_report_v2",
            "status": t.get("status", "UNKNOWN"),
            "span": t.get("span", {}),
            "count": t.get("count", len(members)),
            "domain": t.get("domain", ""),
            "evolution_report": evolution,
            "top_keywords": list(
                dict.fromkeys(  # deduplicate preserving order
                    kw for m in members for kw in extract_keywords(m["content"])
                )
            )[:10],
        })

    print(f"  Existing trajectories with evolution reports: {len(existing_reports)}")

    # ── Phase 7: Write output ──────────────────────────────────────────────

    print("\nPhase 7: Writing combined output...")

    all_output = existing_reports + new_trajectories
    with open(OUTPUT_PATH, "w") as f:
        for entry in all_output:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    output_size = OUTPUT_PATH.stat().st_size

    # ── Phase 8: Comprehensive stats ───────────────────────────────────────

    total_covered = len(covered_ids | new_covered)
    total_coverage = 100 * total_covered / total_atoms if total_atoms else 0

    new_status_counts = Counter(t["status"] for t in new_trajectories)
    new_domain_counts = Counter(t["domain"] for t in new_trajectories)
    new_ptype_counts = Counter(t["prompt_type"] for t in new_trajectories)

    # Periodicity distribution
    periodicity_counts = Counter()
    for t in new_trajectories:
        p = t.get("evolution_report", {}).get("periodicity", "unknown")
        periodicity_counts[p] += 1
    for r in existing_reports:
        p = r.get("evolution_report", {}).get("periodicity", "unknown")
        periodicity_counts[p] += 1

    # Sophistication stats
    awl_changes = []
    jd_changes = []
    for entry in all_output:
        er = entry.get("evolution_report", {})
        sd = er.get("sophistication_delta", {})
        if sd:
            awl_changes.append(sd.get("awl_change", 0))
            jd_changes.append(sd.get("jd_change", 0))

    print(f"\n{'=' * 72}")
    print(f"TRAJECTORY DEEP ANALYSIS — RESULTS")
    print(f"{'=' * 72}")

    print(f"\n── Coverage ────────────────────────────────────────────────────────")
    print(f"  Total atoms:                     {total_atoms:,}")
    print(f"  First-pass coverage:             {len(covered_ids):,} ({100*len(covered_ids)/total_atoms:.1f}%)")
    print(f"  Second-pass new coverage:        {len(new_covered):,} ({100*len(new_covered)/total_atoms:.1f}%)")
    print(f"  COMBINED coverage:               {total_covered:,} ({total_coverage:.1f}%)")
    print(f"  Still uncovered:                 {total_atoms - total_covered:,} ({100*(total_atoms - total_covered)/total_atoms:.1f}%)")

    print(f"\n── Trajectory counts ───────────────────────────────────────────────")
    print(f"  Existing (first pass):           {len(existing_trajectories)}")
    print(f"  New (second pass):               {len(new_trajectories)}")
    print(f"  Evolution reports (existing):    {len(existing_reports)}")
    print(f"  Total output entries:            {len(all_output)}")

    print(f"\n── New trajectories by status ──────────────────────────────────────")
    for s, c in new_status_counts.most_common():
        print(f"  {s:20s}: {c:5d}")

    print(f"\n── New trajectories by domain ──────────────────────────────────────")
    for d, c in new_domain_counts.most_common():
        print(f"  {d:20s}: {c:5d}")

    print(f"\n── New trajectories by prompt_type ─────────────────────────────────")
    for p, c in new_ptype_counts.most_common():
        print(f"  {p:20s}: {c:5d}")

    print(f"\n── Periodicity (all trajectories) ──────────────────────────────────")
    for p, c in periodicity_counts.most_common():
        print(f"  {p:20s}: {c:5d}")

    print(f"\n── Sophistication delta (all trajectories) ─────────────────────────")
    if awl_changes:
        print(f"  Avg word length Δ:  mean={sum(awl_changes)/len(awl_changes):.3f}, "
              f"min={min(awl_changes):.3f}, max={max(awl_changes):.3f}")
    if jd_changes:
        print(f"  Jargon density Δ:   mean={sum(jd_changes)/len(jd_changes):.4f}, "
              f"min={min(jd_changes):.4f}, max={max(jd_changes):.4f}")

    print(f"\n── Top 20 new trajectories by size ─────────────────────────────────")
    for t in new_trajectories[:20]:
        per = t.get("evolution_report", {}).get("periodicity", "?")
        print(f"  [{t['status']:12s}] {t['count']:4d} atoms | "
              f"{t['span'].get('months', 0):2d}mo | {per:16s} | "
              f"{t['intention_label'][:50]}")

    print(f"\n── Cluster size distribution (new) ─────────────────────────────────")
    size_buckets = Counter()
    for t in new_trajectories:
        c = t["count"]
        if c >= 100:
            size_buckets["100+"] += 1
        elif c >= 50:
            size_buckets["50-99"] += 1
        elif c >= 20:
            size_buckets["20-49"] += 1
        elif c >= 10:
            size_buckets["10-19"] += 1
        elif c >= 5:
            size_buckets["5-9"] += 1
        else:
            size_buckets["2-4"] += 1
    for bucket in ["100+", "50-99", "20-49", "10-19", "5-9", "2-4"]:
        print(f"  {bucket:10s}: {size_buckets.get(bucket, 0):5d} trajectories")

    print(f"\n── Output ──────────────────────────────────────────────────────────")
    print(f"  File: {OUTPUT_PATH}")
    print(f"  Size: {output_size / 1024:.0f} KB ({output_size / (1024*1024):.1f} MB)")
    print(f"  Lines: {len(all_output)}")

    # ── Phase 9: Sample predictions ────────────────────────────────────────

    print(f"\n── Sample predictions (5 largest new trajectories) ─────────────────")
    for t in new_trajectories[:5]:
        er = t.get("evolution_report", {})
        print(f"\n  [{t['trajectory_id']}] {t['intention_label'][:60]}")
        print(f"    Count: {t['count']} | Domain: {t['domain']} | Status: {t['status']}")
        print(f"    Span: {t['span'].get('first','')} → {t['span'].get('latest','')}")
        print(f"    Periodicity: {er.get('periodicity', '?')}")
        print(f"    Sophistication Δ: AWL {er.get('sophistication_delta',{}).get('awl_change', 0):+.2f}, "
              f"JD {er.get('sophistication_delta',{}).get('jd_change', 0):+.3f}")
        pred = er.get("predicted_next_prompt", "")
        if len(pred) > 100:
            pred = pred[:100] + "..."
        print(f"    Prediction: {pred}")
        added = er.get("concepts_added", [])[:8]
        if added:
            print(f"    Concepts added: {', '.join(added)}")

    print(f"\n{'=' * 72}")
    print(f"DONE. Combined coverage: {total_coverage:.1f}%")
    print(f"{'=' * 72}")


if __name__ == "__main__":
    main()
