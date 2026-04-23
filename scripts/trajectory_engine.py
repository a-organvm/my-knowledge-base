#!/usr/bin/env python3
"""Prompt Trajectory Amalgamation Engine.

Clusters 11,980+ prompt atoms into INTENTION TRAJECTORIES — persistent
themes that recur across months. For each trajectory: first expression,
latest expression, delta, projected next, and status classification.

Usage: python3 scripts/trajectory_engine.py
"""

import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ATOMS_PATH = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/prompt-atoms.jsonl"
)
SHORT_PATH = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/prompt-atoms-short.jsonl"
)
OUTPUT_PATH = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/intention-trajectories.jsonl"
)

STOPWORDS = {
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
    "file", "files", "code", "tool", "can't", "don't", "it's", "i'm",
    "let's", "you're", "that's", "here's", "there's", "didn't", "doesn't",
    "wasn't", "aren't", "won't", "isn't", "haven't", "couldn't", "wouldn't",
}


# ── Union-Find ──────────────────────────────────────────────────────────────

class UnionFind:
    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1


# ── Helpers ─────────────────────────────────────────────────────────────────

def extract_phrases(text: str, max_chars: int = 2000) -> set:
    text = text[:max_chars]
    text = re.sub(r"[^a-z\s]", " ", text.lower())
    words = [w for w in text.split() if len(w) > 3 and w not in STOPWORDS]
    phrases = set()
    for n in [2, 3]:
        for i in range(len(words) - n + 1):
            phrases.add(" ".join(words[i : i + n]))
    return phrases


def parse_date(ts: str) -> str:
    if not ts or ts.startswith("1969"):
        return ""
    return ts[:10]


def compute_delta(first_content: str, latest_content: str) -> str:
    first_words = set(re.sub(r"[^a-z\s]", " ", first_content.lower()).split())
    latest_words = set(re.sub(r"[^a-z\s]", " ", latest_content.lower()).split())
    added = latest_words - first_words - STOPWORDS
    removed = first_words - latest_words - STOPWORDS
    significant_added = sorted(w for w in added if len(w) > 4)[:15]
    significant_removed = sorted(w for w in removed if len(w) > 4)[:10]
    parts = []
    if significant_added:
        parts.append(f"Added concepts: {', '.join(sorted(significant_added))}")
    if significant_removed:
        parts.append(f"Dropped concepts: {', '.join(sorted(significant_removed))}")
    if not parts:
        return "Minimal evolution — intent remains stable"
    return "; ".join(parts)


def project_next(members: list) -> str:
    if len(members) < 3:
        return "Insufficient data for projection"
    # Take the latest quartile of prompts
    sorted_m = sorted(members, key=lambda m: m["date"])
    quartile = sorted_m[-(len(sorted_m) // 4 + 1) :]
    # Extract trending concepts from latest quartile vs earlier
    early = sorted_m[: len(sorted_m) // 2]
    early_words = set()
    for m in early:
        early_words.update(re.sub(r"[^a-z\s]", " ", m["content"][:500].lower()).split())
    late_words = set()
    for m in quartile:
        late_words.update(re.sub(r"[^a-z\s]", " ", m["content"][:500].lower()).split())
    trending = {w for w in (late_words - early_words - STOPWORDS) if len(w) > 4}
    if trending:
        top = sorted(trending)[:10]
        return f"Trending toward: {', '.join(top)}"
    return "Trajectory stable — expect repetition of current expression"


def classify_status(members: list, now_str: str = "2026-04-23") -> str:
    dates = [m["date"] for m in members if m["date"]]
    if not dates:
        return "OPEN"
    latest = max(dates)
    # Dormant: no activity in 90+ days
    try:
        latest_dt = datetime.strptime(latest, "%Y-%m-%d")
        now_dt = datetime.strptime(now_str, "%Y-%m-%d")
        if (now_dt - latest_dt).days > 90:
            return "DORMANT"
    except ValueError:
        pass
    # Check for convergence: do the last 5 prompts use very similar language?
    sorted_m = sorted(members, key=lambda m: m["date"])
    if len(sorted_m) >= 5:
        last5 = [set(re.sub(r"[^a-z\s]", " ", m["content"][:200].lower()).split()) for m in sorted_m[-5:]]
        # Average pairwise overlap
        overlaps = []
        for i in range(len(last5)):
            for j in range(i + 1, len(last5)):
                union = last5[i] | last5[j]
                if union:
                    overlaps.append(len(last5[i] & last5[j]) / len(union))
        avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0
        if avg_overlap > 0.5:
            return "CRYSTALLIZED"
    # Check for evolution: significant word-set change first→latest
    first_words = set(re.sub(r"[^a-z\s]", " ", sorted_m[0]["content"][:500].lower()).split()) - STOPWORDS
    latest_words = set(re.sub(r"[^a-z\s]", " ", sorted_m[-1]["content"][:500].lower()).split()) - STOPWORDS
    if first_words and latest_words:
        overlap = len(first_words & latest_words) / max(len(first_words | latest_words), 1)
        if overlap < 0.3:
            return "EVOLVED"
    return "UNRESOLVED"


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    # Phase 1: Load atoms
    print("Phase 1: Loading atoms...")
    atoms = []
    for path in [ATOMS_PATH, SHORT_PATH]:
        if path.exists():
            with open(path) as f:
                for line in f:
                    if line.strip():
                        atoms.append(json.loads(line))
    print(f"  Loaded {len(atoms)} atoms")

    # Build lightweight records
    records = []
    for i, a in enumerate(atoms):
        ts = a.get("source", {}).get("timestamp", "") or ""
        date = parse_date(ts)
        phrases = extract_phrases(a.get("content", ""))
        records.append({
            "idx": i,
            "id": a["id"],
            "date": date,
            "domain": a.get("domain", "general"),
            "content": a.get("content", "")[:2000],
            "title": a.get("title", ""),
            "phrases": phrases,
        })

    # Phase 2: Build inverted index + cluster
    print("Phase 2: Building inverted index...")
    phrase_index = defaultdict(set)  # phrase -> set of record indices
    for r in records:
        for p in r["phrases"]:
            phrase_index[p].add(r["idx"])

    # Filter phrases that appear in 3+ atoms (too rare = noise, too common = useless)
    # Also cap at 500 to avoid universal phrases
    filtered_phrases = {
        p: idxs for p, idxs in phrase_index.items()
        if 3 <= len(idxs) <= 500
    }
    print(f"  {len(filtered_phrases)} significant phrases (from {len(phrase_index)} total)")

    # Phase 3: Union-Find clustering
    print("Phase 3: Clustering via union-find...")
    uf = UnionFind()

    # For each phrase, union all atoms that share it AND share domain
    for phrase, idxs in filtered_phrases.items():
        idx_list = list(idxs)
        # Group by domain within phrase co-occurrence
        by_domain = defaultdict(list)
        for idx in idx_list:
            by_domain[records[idx]["domain"]].append(idx)
        # Union within same domain
        for domain, domain_idxs in by_domain.items():
            if len(domain_idxs) < 3:
                continue
            # Only union if atoms share 3+ phrases with each other
            # (phrase_index gives us one shared phrase; check for more)
            for i in range(len(domain_idxs)):
                for j in range(i + 1, min(i + 20, len(domain_idxs))):  # limit comparisons
                    a_idx, b_idx = domain_idxs[i], domain_idxs[j]
                    shared = records[a_idx]["phrases"] & records[b_idx]["phrases"]
                    if len(shared) >= 3:
                        uf.union(a_idx, b_idx)

    # Collect clusters
    clusters = defaultdict(list)
    for r in records:
        root = uf.find(r["idx"])
        clusters[root].append(r)

    # Phase 4: Filter clusters
    print("Phase 4: Filtering and computing trajectories...")
    trajectories = []

    for root, members in clusters.items():
        if len(members) < 3:
            continue
        dates = [m["date"] for m in members if m["date"]]
        if not dates:
            continue
        months = set(d[:7] for d in dates)
        if len(months) < 2:
            continue

        sorted_members = sorted(members, key=lambda m: m["date"] if m["date"] else "9999")
        first = sorted_members[0]
        latest = sorted_members[-1]

        # Compute density
        density = defaultdict(int)
        for m in members:
            if m["date"]:
                density[m["date"][:7]] += 1

        # Top phrases in this cluster
        all_phrases = defaultdict(int)
        for m in members:
            for p in m["phrases"]:
                all_phrases[p] += 1
        top_phrases = sorted(all_phrases.items(), key=lambda x: -x[1])[:5]
        label = " / ".join(p[0] for p in top_phrases[:3])

        # Deterministic ID
        member_ids = sorted(m["id"] for m in members)
        traj_id = "traj-" + hashlib.sha256("|".join(member_ids).encode()).hexdigest()[:12]

        # Domain: most common
        domain_counts = defaultdict(int)
        for m in members:
            domain_counts[m["domain"]] += 1
        primary_domain = max(domain_counts, key=domain_counts.get)

        status = classify_status(members)
        delta = compute_delta(first["content"], latest["content"])
        projected = project_next(members)

        trajectories.append({
            "trajectory_id": traj_id,
            "intention_label": label,
            "status": status,
            "span": {
                "first": min(dates),
                "latest": max(dates),
                "months": len(months),
            },
            "count": len(members),
            "domain": primary_domain,
            "evolution": {
                "first_expression": {
                    "id": first["id"],
                    "content": first["content"][:300],
                    "date": first["date"],
                },
                "latest_expression": {
                    "id": latest["id"],
                    "content": latest["content"][:300],
                    "date": latest["date"],
                },
                "delta": delta,
                "projected_next": projected,
            },
            "top_phrases": [p[0] for p in top_phrases],
            "member_ids": member_ids,
            "density": dict(sorted(density.items())),
        })

    # Sort by count descending
    trajectories.sort(key=lambda t: -t["count"])

    # Phase 5: Output
    print(f"Phase 5: Writing {len(trajectories)} trajectories...")
    with open(OUTPUT_PATH, "w") as f:
        for t in trajectories:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    # Stats
    covered_ids = set()
    for t in trajectories:
        covered_ids.update(t["member_ids"])

    status_counts = defaultdict(int)
    for t in trajectories:
        status_counts[t["status"]] += 1

    domain_counts = defaultdict(int)
    for t in trajectories:
        domain_counts[t["domain"]] += 1

    print(f"\n{'=' * 70}")
    print(f"TRAJECTORY ENGINE RESULTS")
    print(f"{'=' * 70}")
    print(f"Total trajectories: {len(trajectories)}")
    print(f"Atoms covered: {len(covered_ids)} / {len(atoms)} ({100*len(covered_ids)/len(atoms):.1f}%)")
    print(f"\nBy status:")
    for s, c in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"  {s:15s}: {c}")
    print(f"\nBy domain:")
    for d, c in sorted(domain_counts.items(), key=lambda x: -x[1]):
        print(f"  {d:15s}: {c}")
    print(f"\nTop 15 trajectories by size:")
    for t in trajectories[:15]:
        print(f"  [{t['status']:12s}] {t['count']:4d} atoms | {t['span']['months']:2d} months | {t['intention_label'][:60]}")
    print(f"\nOutput: {OUTPUT_PATH}")
    print(f"Size: {OUTPUT_PATH.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
