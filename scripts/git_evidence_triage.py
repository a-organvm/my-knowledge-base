#!/usr/bin/env python3
"""Git evidence triage for ANSWERED prompt atoms.

Loads prompt-atoms.jsonl, filters for status=ANSWERED, then cross-references
against git history and filesystem to verify which prompts have concrete evidence
of completion. Marks verified prompts as VERIFIED_DONE in review-results.db.

Strategy:
  1. Build a git commit index ONCE across all repos in ~/Workspace/
  2. For each ANSWERED prompt, extract keywords from the content
  3. Match prompt keywords against commit message keywords
  4. Require 3+ keyword overlap (conservative)
  5. Also check filesystem for file-creation prompts
  6. Write results to review-results.db

Usage: python3 scripts/git_evidence_triage.py [--dry-run] [--min-overlap N]
"""

import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

# --- Configuration ---

WORKSPACE = Path.home() / "Workspace"
ATOMS_PATH = (
    WORKSPACE / "organvm" / "organvm-corpvs-testamentvm"
    / "data" / "atoms" / "prompt-atoms.jsonl"
)
REVIEW_DB_PATH = (
    WORKSPACE / "organvm" / "my-knowledge-base" / "db" / "review-results.db"
)
MIN_KEYWORD_OVERLAP = 3
GIT_SINCE = "2022-12-01"

# Words too common to be meaningful in matching
STOP_WORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "must",
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us",
    "my", "your", "his", "its", "our", "their",
    "this", "that", "these", "those", "what", "which", "who", "whom",
    "and", "or", "but", "if", "then", "else", "when", "where", "how", "why",
    "not", "no", "nor", "so", "too", "very", "just", "also", "only",
    "all", "each", "every", "both", "few", "more", "most", "some", "any",
    "of", "in", "to", "for", "with", "on", "at", "by", "from", "as",
    "into", "about", "between", "through", "after", "before", "above",
    "below", "up", "down", "out", "off", "over", "under",
    "here", "there", "now", "then", "once", "already", "still",
    "make", "made", "get", "got", "set", "let", "put", "take", "give",
    "go", "come", "see", "look", "find", "know", "think", "say", "tell",
    "use", "used", "using", "try", "want", "like", "new", "one", "two",
    "first", "last", "next", "code", "file", "run", "add", "change",
    "please", "help", "sure", "thanks", "yes", "okay",
    "write", "create", "update", "fix", "check", "test",  # too generic alone
})

# File-creation verb patterns
FILE_CREATE_RE = re.compile(
    r"(?:create|write|add|generate|make|build|implement)\s+"
    r"(?:a\s+|the\s+|an\s+)?(?:new\s+)?"
    r"(?:file|script|module|component|class|function|test|page|template|config)"
    r"(?:\s+(?:called|named|at|in))?\s+"
    r"[`'\"]?([^\s`'\",:]+)[`'\"]?",
    re.IGNORECASE,
)

# Path-like patterns in prompt content
PATH_RE = re.compile(
    r"(?:~/|/|\./)?(?:[\w.-]+/)+[\w.-]+\.[\w]+",
)


def extract_keywords(text: str) -> set[str]:
    """Extract meaningful keywords from text, lowercased and filtered."""
    # Tokenize: split on non-alphanumeric, keep tokens 3+ chars
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower())
    return {t for t in tokens if t not in STOP_WORDS and len(t) >= 3}


def extract_file_targets(content: str) -> list[str]:
    """Extract filenames/paths that prompts reference for creation/modification."""
    targets = []

    # Match explicit file creation patterns
    for m in FILE_CREATE_RE.finditer(content):
        targets.append(m.group(1))

    # Match path-like strings
    for m in PATH_RE.finditer(content):
        targets.append(m.group(0))

    # Match backtick-quoted filenames
    for m in re.finditer(r"`([^`]+\.\w{1,6})`", content):
        targets.append(m.group(1))

    return targets


def discover_repos() -> list[Path]:
    """Find all git repos under ~/Workspace at depth 1-3."""
    repos = []
    for git_dir in WORKSPACE.rglob(".git"):
        # Only go 3 levels deep from workspace root
        rel = git_dir.relative_to(WORKSPACE)
        if len(rel.parts) <= 4:  # e.g., organvm/repo/.git = 3 parts
            repo_path = git_dir.parent
            repos.append(repo_path)
    return sorted(set(repos))


def build_git_index(repos: list[Path]) -> list[dict]:
    """Run git log in each repo ONCE and build a searchable commit index.

    Returns a list of dicts: {repo, hash, message, keywords}
    """
    index = []
    failed = 0
    total_commits = 0

    print(f"Scanning {len(repos)} repos for git history since {GIT_SINCE}...")
    t0 = time.monotonic()

    for repo in repos:
        try:
            result = subprocess.run(
                [
                    "git", "log", "--oneline", "--all",
                    f"--since={GIT_SINCE}",
                    "--format=%h %s",
                ],
                cwd=str(repo),
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                failed += 1
                continue

            repo_name = str(repo.relative_to(WORKSPACE))
            for line in result.stdout.strip().splitlines():
                if not line.strip():
                    continue
                parts = line.split(" ", 1)
                if len(parts) < 2:
                    continue
                commit_hash = parts[0]
                message = parts[1]
                keywords = extract_keywords(message)
                if keywords:
                    index.append({
                        "repo": repo_name,
                        "hash": commit_hash,
                        "message": message,
                        "keywords": keywords,
                    })
                    total_commits += 1

        except subprocess.TimeoutExpired:
            failed += 1
        except Exception:
            failed += 1

    elapsed = time.monotonic() - t0
    print(
        f"  Indexed {total_commits} commits from {len(repos) - failed} repos "
        f"in {elapsed:.1f}s ({failed} repos failed/skipped)"
    )
    return index


def match_prompt_to_commits(
    prompt_keywords: set[str],
    commit_index: list[dict],
    min_overlap: int,
) -> list[dict]:
    """Find commits whose keywords overlap with the prompt by >= min_overlap."""
    matches = []
    for commit in commit_index:
        overlap = prompt_keywords & commit["keywords"]
        if len(overlap) >= min_overlap:
            matches.append({
                "repo": commit["repo"],
                "hash": commit["hash"],
                "message": commit["message"],
                "overlap": sorted(overlap),
                "overlap_count": len(overlap),
            })
    # Sort by overlap count descending, take top 5
    matches.sort(key=lambda x: x["overlap_count"], reverse=True)
    return matches[:5]


def check_file_existence(targets: list[str]) -> list[str]:
    """Check if referenced files exist on the filesystem."""
    found = []
    for target in targets:
        # Try various path resolutions
        candidates = [
            Path(target),
            Path.home() / target.lstrip("~/"),
            WORKSPACE / target,
        ]
        # Also check common locations
        if not target.startswith("/") and not target.startswith("~"):
            candidates.extend([
                WORKSPACE / "organvm" / target,
                WORKSPACE / "meta-organvm" / target,
                WORKSPACE / "4444J99" / target,
            ])

        for candidate in candidates:
            try:
                if candidate.exists():
                    found.append(str(candidate))
                    break
            except (OSError, ValueError):
                continue
    return found


def load_answered_atoms() -> list[dict]:
    """Load all ANSWERED prompt atoms from the JSONL file."""
    atoms = []
    with open(ATOMS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            atom = json.loads(line)
            if atom.get("status") == "ANSWERED":
                atoms.append(atom)
    return atoms


def init_review_db() -> sqlite3.Connection:
    """Initialize the review results database, adding columns if needed."""
    conn = sqlite3.connect(str(REVIEW_DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            prompt_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            notes TEXT DEFAULT '',
            reviewed_at TEXT NOT NULL
        )
    """)
    # Add evidence columns if they don't exist
    try:
        conn.execute("ALTER TABLE reviews ADD COLUMN evidence_type TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass  # column already exists
    try:
        conn.execute("ALTER TABLE reviews ADD COLUMN evidence_detail TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE reviews ADD COLUMN keyword_overlap INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    return conn


def save_verified(
    conn: sqlite3.Connection,
    prompt_id: str,
    evidence_type: str,
    evidence_detail: str,
    keyword_overlap: int,
    dry_run: bool = False,
) -> None:
    """Save a VERIFIED_DONE result to the review database."""
    if dry_run:
        return
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT OR REPLACE INTO reviews
            (prompt_id, status, notes, reviewed_at, evidence_type, evidence_detail, keyword_overlap)
        VALUES (?, 'VERIFIED_DONE', ?, ?, ?, ?, ?)
        """,
        (
            prompt_id,
            f"auto-verified via git evidence triage",
            now,
            evidence_type,
            evidence_detail,
            keyword_overlap,
        ),
    )


def main():
    dry_run = "--dry-run" in sys.argv
    min_overlap = MIN_KEYWORD_OVERLAP

    for i, arg in enumerate(sys.argv):
        if arg == "--min-overlap" and i + 1 < len(sys.argv):
            min_overlap = int(sys.argv[i + 1])

    if not ATOMS_PATH.exists():
        print(f"ERROR: prompt-atoms.jsonl not found at {ATOMS_PATH}", file=sys.stderr)
        sys.exit(1)

    print("=" * 72)
    print("GIT EVIDENCE TRIAGE")
    print(f"  Source: {ATOMS_PATH}")
    print(f"  Output: {REVIEW_DB_PATH}")
    print(f"  Min keyword overlap: {min_overlap}")
    print(f"  Dry run: {dry_run}")
    print("=" * 72)

    # Step 1: Load ANSWERED atoms
    print("\n[1/5] Loading ANSWERED prompt atoms...")
    atoms = load_answered_atoms()
    print(f"  Loaded {len(atoms)} ANSWERED atoms")

    # Step 2: Discover repos and build git index
    print("\n[2/5] Building git commit index...")
    repos = discover_repos()
    commit_index = build_git_index(repos)
    print(f"  Total searchable commits: {len(commit_index)}")

    # Step 3: Check existing reviews to skip already-processed
    conn = init_review_db()
    existing = set()
    for row in conn.execute("SELECT prompt_id FROM reviews"):
        existing.add(row[0])
    print(f"\n[3/5] Skipping {len(existing)} already-reviewed atoms")

    # Filter out already-reviewed
    to_process = [a for a in atoms if a["id"] not in existing]
    print(f"  Remaining to process: {len(to_process)}")

    # Step 4: Match prompts against git history and filesystem
    print(f"\n[4/5] Matching {len(to_process)} prompts against evidence...")
    t0 = time.monotonic()

    verified_git = 0
    verified_file = 0
    verified_both = 0
    unverified = 0

    # Pre-extract keywords for all prompts
    prompt_data = []
    for atom in to_process:
        content = atom.get("content", "")
        title = atom.get("title", "")
        combined = f"{title} {content}"
        keywords = extract_keywords(combined)
        file_targets = extract_file_targets(content)
        prompt_data.append({
            "atom": atom,
            "keywords": keywords,
            "file_targets": file_targets,
        })

    batch_size = 1000
    for batch_start in range(0, len(prompt_data), batch_size):
        batch_end = min(batch_start + batch_size, len(prompt_data))
        batch = prompt_data[batch_start:batch_end]

        for pd in batch:
            atom = pd["atom"]
            keywords = pd["keywords"]
            file_targets = pd["file_targets"]

            git_matches = []
            files_found = []
            evidence_type = ""
            evidence_detail = ""
            overlap_count = 0

            # Git history matching
            if len(keywords) >= min_overlap:
                git_matches = match_prompt_to_commits(
                    keywords, commit_index, min_overlap
                )

            # Filesystem checks for file-creation prompts
            if file_targets:
                files_found = check_file_existence(file_targets)

            # Classify evidence
            has_git = len(git_matches) > 0
            has_file = len(files_found) > 0

            if has_git and has_file:
                evidence_type = "git+filesystem"
                best = git_matches[0]
                evidence_detail = json.dumps({
                    "top_commit": f"{best['repo']}:{best['hash']} {best['message']}",
                    "overlap": best["overlap"],
                    "files_found": files_found[:3],
                })
                overlap_count = best["overlap_count"]
                verified_both += 1
                save_verified(
                    conn, atom["id"], evidence_type,
                    evidence_detail, overlap_count, dry_run,
                )
            elif has_git:
                evidence_type = "git_history"
                best = git_matches[0]
                evidence_detail = json.dumps({
                    "top_commit": f"{best['repo']}:{best['hash']} {best['message']}",
                    "overlap": best["overlap"],
                    "match_count": len(git_matches),
                })
                overlap_count = best["overlap_count"]
                verified_git += 1
                save_verified(
                    conn, atom["id"], evidence_type,
                    evidence_detail, overlap_count, dry_run,
                )
            elif has_file:
                evidence_type = "filesystem"
                evidence_detail = json.dumps({"files_found": files_found[:5]})
                overlap_count = 0
                verified_file += 1
                save_verified(
                    conn, atom["id"], evidence_type,
                    evidence_detail, overlap_count, dry_run,
                )
            else:
                unverified += 1

        # Progress checkpoint
        if not dry_run and batch_end % batch_size == 0:
            conn.commit()
            elapsed = time.monotonic() - t0
            pct = batch_end / len(prompt_data) * 100
            print(
                f"  Progress: {batch_end}/{len(prompt_data)} ({pct:.0f}%) "
                f"- {elapsed:.1f}s elapsed"
            )

    # Final commit
    if not dry_run:
        conn.commit()

    elapsed = time.monotonic() - t0
    total_verified = verified_git + verified_file + verified_both

    # Step 5: Summary
    print(f"\n[5/5] Results (completed in {elapsed:.1f}s)")
    print("=" * 72)
    print(f"  ANSWERED atoms processed:  {len(to_process)}")
    print(f"  Previously reviewed:       {len(existing)}")
    print()
    print(f"  VERIFIED_DONE (total):     {total_verified}")
    print(f"    - git history only:      {verified_git}")
    print(f"    - filesystem only:       {verified_file}")
    print(f"    - git + filesystem:      {verified_both}")
    print()
    print(f"  STILL NEED REVIEW:         {unverified}")
    print()
    print(f"  Verification rate:         ", end="")
    if len(to_process) > 0:
        pct = total_verified / len(to_process) * 100
        print(f"{pct:.1f}%")
    else:
        print("N/A (nothing to process)")
    print("=" * 72)

    # Show top repos contributing evidence
    if not dry_run and total_verified > 0:
        repo_counts = defaultdict(int)
        for row in conn.execute(
            "SELECT evidence_detail FROM reviews WHERE status='VERIFIED_DONE'"
        ):
            detail = row[0]
            if detail:
                try:
                    d = json.loads(detail)
                    tc = d.get("top_commit", "")
                    if ":" in tc:
                        repo = tc.split(":")[0]
                        repo_counts[repo] += 1
                except (json.JSONDecodeError, AttributeError):
                    pass

        if repo_counts:
            print("\nTop repos providing evidence:")
            for repo, count in sorted(
                repo_counts.items(), key=lambda x: -x[1]
            )[:15]:
                print(f"  {count:5d}  {repo}")

    # Show sample verified prompts
    if not dry_run:
        print("\nSample verified prompts:")
        cursor = conn.execute(
            """
            SELECT prompt_id, evidence_type, evidence_detail, keyword_overlap
            FROM reviews
            WHERE status = 'VERIFIED_DONE'
            ORDER BY keyword_overlap DESC
            LIMIT 10
            """
        )
        for row in cursor:
            pid, etype, detail, overlap = row
            detail_short = detail[:120] if detail else ""
            print(f"  [{overlap} kw] {pid} ({etype}): {detail_short}")

    conn.close()

    # Final counts across all review statuses
    conn2 = sqlite3.connect(str(REVIEW_DB_PATH))
    print("\nFull review-results.db status breakdown:")
    for row in conn2.execute(
        "SELECT status, count(*) FROM reviews GROUP BY status ORDER BY count(*) DESC"
    ):
        print(f"  {row[0]:20s}: {row[1]:>6d}")
    total_reviews = conn2.execute("SELECT count(*) FROM reviews").fetchone()[0]
    remaining = len(atoms) - total_reviews
    print(f"  {'REMAINING':20s}: {remaining:>6d}  (ANSWERED atoms not yet in reviews)")
    conn2.close()


if __name__ == "__main__":
    main()
