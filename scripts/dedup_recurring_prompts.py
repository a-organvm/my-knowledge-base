#!/usr/bin/env python3
"""Deduplicate recurring prompt atoms by content similarity within domains.

3.5 years of prompts contain massive recurrence clusters — "social media" 94 times,
"digital marketing" 99 times. This script groups near-identical prompts (>85%
similarity on first 200 chars), keeps the LATEST as canonical, and marks all
earlier versions SUPERSEDED in review-results.db.

Uses inverted index on domain+keywords to avoid O(n^2) comparisons.

stdlib only.

Usage:
    python3 scripts/dedup_recurring_prompts.py [--threshold 0.85] [--dry-run]
"""

import json
import re
import sqlite3
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ATOMS_PATH = (
    PROJECT_ROOT.parent / "organvm-corpvs-testamentvm" / "data" / "atoms" / "prompt-atoms.jsonl"
)
DB_PATH = PROJECT_ROOT / "db" / "review-results.db"

# --- Config ---
DEFAULT_THRESHOLD = 0.85
SNIPPET_LEN = 200
# Number of top keywords to extract per atom for the inverted index
KEYWORD_COUNT = 6
# Minimum keyword length to be indexed
MIN_KEYWORD_LEN = 4

# Common stopwords to exclude from keyword extraction
STOPWORDS = frozenset({
    "this", "that", "with", "from", "will", "have", "been", "were", "they",
    "them", "their", "what", "when", "where", "which", "while", "about",
    "into", "than", "then", "each", "make", "like", "just", "over", "also",
    "some", "such", "your", "more", "need", "want", "here", "there", "these",
    "those", "very", "would", "could", "should", "does", "done", "only",
    "most", "much", "many", "well", "back", "even", "also", "come", "both",
    "between", "being", "after", "before", "other", "using", "used", "please",
    "following", "help", "based", "good", "create", "write", "code",
})


def extract_keywords(text: str) -> list[str]:
    """Extract top keywords from text for inverted index bucketing."""
    words = re.findall(r"[a-z]{4,}", text.lower())
    freq: dict[str, int] = {}
    for w in words:
        if w not in STOPWORDS:
            freq[w] = freq.get(w, 0) + 1
    # Sort by frequency descending, then alphabetically for stability
    ranked = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    return [w for w, _ in ranked[:KEYWORD_COUNT]]


def load_atoms(path: Path) -> list[dict]:
    """Load all prompt atoms from JSONL."""
    atoms = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                atoms.append(json.loads(line))
    return atoms


def parse_timestamp(atom: dict) -> str:
    """Extract a comparable timestamp string from an atom."""
    src = atom.get("source", {})
    ts = src.get("timestamp") or ""
    return ts


def build_inverted_index(atoms: list[dict]) -> dict[str, list[int]]:
    """Build inverted index: domain+keyword -> list of atom indices.

    This avoids O(n^2) by only comparing atoms that share at least one
    domain+keyword bucket.
    """
    index: dict[str, list[int]] = defaultdict(list)
    for i, atom in enumerate(atoms):
        domain = atom.get("domain", "general")
        snippet = atom.get("content", "")[:SNIPPET_LEN].lower()
        keywords = extract_keywords(snippet)
        for kw in keywords:
            bucket_key = f"{domain}::{kw}"
            index[bucket_key].append(i)
    return index


def find_clusters(
    atoms: list[dict],
    threshold: float,
) -> list[list[int]]:
    """Find recurrence clusters using inverted index + SequenceMatcher.

    Strategy:
    1. Build inverted index on domain+keywords (first 200 chars)
    2. For each bucket, compare pairs within the bucket
    3. Union-find to merge overlapping matches into clusters
    """
    n = len(atoms)

    # --- Union-Find ---
    parent = list(range(n))
    rank = [0] * n

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]  # path compression
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1

    # --- Build inverted index ---
    print("Building inverted index...")
    t0 = time.monotonic()
    inv_index = build_inverted_index(atoms)
    print(f"  {len(inv_index)} buckets built in {time.monotonic() - t0:.2f}s")

    # Precompute snippets
    snippets = [a.get("content", "")[:SNIPPET_LEN] for a in atoms]
    domains = [a.get("domain", "general") for a in atoms]

    # --- Compare within buckets ---
    print("Comparing within buckets...")
    t0 = time.monotonic()
    comparisons = 0
    matches = 0
    # Track which pairs we already compared to avoid redundant work
    seen_pairs: set[tuple[int, int]] = set()

    for bucket_key, indices in inv_index.items():
        if len(indices) < 2:
            continue
        # Cap bucket size to prevent worst-case blowup on very common keywords
        bucket = indices[:500]
        for x in range(len(bucket)):
            for y in range(x + 1, len(bucket)):
                i, j = bucket[x], bucket[y]
                if i > j:
                    i, j = j, i
                if (i, j) in seen_pairs:
                    continue
                seen_pairs.add((i, j))

                # Must be same domain
                if domains[i] != domains[j]:
                    continue

                comparisons += 1
                ratio = SequenceMatcher(None, snippets[i], snippets[j]).ratio()
                if ratio >= threshold:
                    union(i, j)
                    matches += 1

    elapsed = time.monotonic() - t0
    print(f"  {comparisons} comparisons, {matches} matches in {elapsed:.2f}s")

    # --- Extract clusters (size >= 2) ---
    cluster_map: dict[int, list[int]] = defaultdict(list)
    for i in range(n):
        root = find(i)
        cluster_map[root].append(i)

    clusters = [members for members in cluster_map.values() if len(members) >= 2]
    return clusters


def write_superseded(
    db_path: Path,
    decisions: list[dict],
) -> None:
    """Write SUPERSEDED decisions to review-results.db."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    now = datetime.now(timezone.utc).isoformat()

    for d in decisions:
        cursor.execute(
            """INSERT OR REPLACE INTO reviews (prompt_id, status, notes, reviewed_at)
               VALUES (?, ?, ?, ?)""",
            (d["prompt_id"], "SUPERSEDED", d["notes"], now),
        )

    conn.commit()
    conn.close()


def main() -> None:
    # --- Parse args ---
    threshold = DEFAULT_THRESHOLD
    dry_run = False
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--threshold" and i + 1 < len(args):
            threshold = float(args[i + 1])
            i += 2
        elif args[i] == "--dry-run":
            dry_run = True
            i += 1
        else:
            print(f"Unknown arg: {args[i]}", file=sys.stderr)
            sys.exit(1)

    # --- Validate paths ---
    if not ATOMS_PATH.exists():
        print(f"ERROR: prompt-atoms.jsonl not found at {ATOMS_PATH}", file=sys.stderr)
        sys.exit(1)
    if not DB_PATH.exists():
        print(f"ERROR: review-results.db not found at {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    # --- Load ---
    print(f"Loading atoms from {ATOMS_PATH}...")
    atoms = load_atoms(ATOMS_PATH)
    print(f"  Loaded {len(atoms)} atoms")

    # --- Domain stats ---
    domain_counts: dict[str, int] = defaultdict(int)
    for a in atoms:
        domain_counts[a.get("domain", "general")] += 1
    print(f"\nDomain distribution:")
    for d, c in sorted(domain_counts.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")

    # --- Find clusters ---
    print(f"\nFinding recurrence clusters (threshold={threshold})...")
    clusters = find_clusters(atoms, threshold)

    if not clusters:
        print("\nNo recurrence clusters found.")
        return

    # --- Sort clusters by size descending ---
    clusters.sort(key=len, reverse=True)

    # --- Determine canonical (latest) and superseded ---
    total_superseded = 0
    decisions: list[dict] = []
    cluster_stats: list[dict] = []

    for cluster_num, members in enumerate(clusters, 1):
        # Find the latest atom by timestamp
        member_atoms = [(idx, atoms[idx]) for idx in members]
        member_atoms.sort(key=lambda x: parse_timestamp(x[1]), reverse=True)

        canonical_idx, canonical_atom = member_atoms[0]
        superseded = member_atoms[1:]

        domain = canonical_atom.get("domain", "general")
        total_superseded += len(superseded)

        for _, sup_atom in superseded:
            decisions.append({
                "prompt_id": sup_atom["id"],
                "notes": f"auto-dedup: cluster-{cluster_num}",
            })

        cluster_stats.append({
            "cluster": cluster_num,
            "size": len(members),
            "domain": domain,
            "canonical_id": canonical_atom["id"],
            "canonical_title": canonical_atom.get("title", "")[:80],
            "canonical_ts": parse_timestamp(canonical_atom),
        })

    # --- Write to DB ---
    if dry_run:
        print(f"\n[DRY RUN] Would write {len(decisions)} SUPERSEDED decisions to {DB_PATH}")
    else:
        print(f"\nWriting {len(decisions)} SUPERSEDED decisions to {DB_PATH}...")
        write_superseded(DB_PATH, decisions)
        print("  Done.")

    # --- Report ---
    print("\n" + "=" * 72)
    print("DEDUPLICATION REPORT")
    print("=" * 72)
    print(f"  Total atoms loaded:       {len(atoms)}")
    print(f"  Similarity threshold:     {threshold:.0%}")
    print(f"  Recurrence clusters:      {len(clusters)}")
    print(f"  Prompts superseded:       {total_superseded}")
    print(f"  Canonical prompts kept:   {len(clusters)}")
    print(f"  Unique (no cluster):      {len(atoms) - total_superseded - len(clusters)}")
    print(f"  Review workload reduction: {total_superseded}/{len(atoms)} = {total_superseded / len(atoms) * 100:.1f}%")
    if dry_run:
        print(f"  Mode:                     DRY RUN (no writes)")
    else:
        print(f"  DB:                       {DB_PATH}")
    print()

    # --- Top clusters ---
    print("TOP 25 RECURRENCE CLUSTERS:")
    print("-" * 72)
    for cs in cluster_stats[:25]:
        print(
            f"  cluster-{cs['cluster']:>4d}  "
            f"size={cs['size']:>3d}  "
            f"domain={cs['domain']:<14s}  "
            f"{cs['canonical_title'][:50]}"
        )

    # --- Domain breakdown ---
    domain_superseded: dict[str, int] = defaultdict(int)
    domain_clusters: dict[str, int] = defaultdict(int)
    for cs in cluster_stats:
        domain_superseded[cs["domain"]] += cs["size"] - 1
        domain_clusters[cs["domain"]] += 1

    print(f"\nDOMAIN BREAKDOWN:")
    print("-" * 72)
    print(f"  {'Domain':<16s} {'Clusters':>8s} {'Superseded':>10s} {'Original':>8s} {'Reduction':>10s}")
    for d in sorted(domain_superseded, key=lambda x: -domain_superseded[x]):
        orig = domain_counts[d]
        sup = domain_superseded[d]
        ncl = domain_clusters[d]
        pct = sup / orig * 100 if orig else 0
        print(f"  {d:<16s} {ncl:>8d} {sup:>10d} {orig:>8d} {pct:>9.1f}%")


if __name__ == "__main__":
    main()
