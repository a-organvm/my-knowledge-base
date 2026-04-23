#!/usr/bin/env python3
"""Auto-classify OBVIOUS prompt atoms to reduce the 11,980 manual review burden.

Conservative pre-classification for high-confidence cases only (>90%).
Writes decisions to review-results.db with auditable notes.

Rules applied:
  1. ABANDONED  — references to tools/services no longer in the user's stack
  2. SUPERSEDED — high content overlap (>90%) with a later prompt in the same thread
  3. ACTUALLY_DONE (git ops)  — git push/commit prompts where assistant confirms success
  4. ACTUALLY_DONE (file ops) — file creation prompts where assistant confirms creation

Usage: python3 scripts/auto_classify_prompts.py [--dry-run]
"""

import json
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
KB_DIR = SCRIPT_DIR.parent
KNOWLEDGE_DB = KB_DIR / "db" / "knowledge.db"
REVIEW_DB = KB_DIR / "db" / "review-results.db"
ATOMS_PATH = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/prompt-atoms.jsonl"
)

DRY_RUN = "--dry-run" in sys.argv

# ---------------------------------------------------------------------------
# Rule 1: ABANDONED — defunct tools/services/contexts
# ---------------------------------------------------------------------------
# Docker was uninstalled 2026-04-18. Prompts about Docker infrastructure
# (not Docker as a concept in a cover letter or job description) are abandoned.
ABANDONED_TOOL_PATTERNS = [
    # Docker infrastructure (not mentions in resumes/cover letters)
    (
        re.compile(
            r"\b(?:docker(?:file|[-\s]compose|[-\s]container|[-\s]image|[-\s]build|[-\s]run"
            r"|[-\s]push|[-\s]pull|[-\s]network|[-\s]volume|\.io))\b",
            re.IGNORECASE,
        ),
        "docker (uninstalled 2026-04-18)",
        # Exclude if the prompt is about job applications / cover letters / resumes
        re.compile(
            r"\b(?:cover\s*letter|resume|job\s*(?:description|posting|listing)"
            r"|application|portfolio|interview)\b",
            re.IGNORECASE,
        ),
    ),
]

# Expired course references — specific courses that ended
ABANDONED_CONTEXT_PATTERNS = [
    (
        re.compile(r"\bENC\s*1101\b", re.IGNORECASE),
        "ENC1101 course (ended)",
        # Only if the timestamp is old enough (before 2025)
        None,
    ),
]


def check_abandoned(atom: dict) -> tuple[bool, str]:
    """Return (is_abandoned, reason) for rule 1.

    Conservative: requires that Docker is the PRIMARY subject of the prompt,
    not just mentioned in passing within a large document. Uses word-density
    as a proxy -- a 5000-word doc that mentions Docker once is not about Docker.
    """
    content = atom.get("content", "")
    title = atom.get("title", "")
    text = f"{title} {content}"
    ts_str = atom.get("source", {}).get("timestamp", "")
    word_count = len(text.split())

    for pattern, reason, exclude_pattern in ABANDONED_TOOL_PATTERNS:
        matches = pattern.findall(text)
        if not matches:
            continue
        # Exclusion: skip if this is about job apps, not actual Docker usage
        if exclude_pattern and exclude_pattern.search(text):
            continue
        # Density guard: Docker mentions must be >0.3% of word count.
        # A 100-word prompt with 1 Docker mention = 1% (OK).
        # A 4000-word doc with 4 mentions = 0.1% (passing reference, skip).
        density = len(matches) / max(word_count, 1) * 100
        if density < 0.3:
            continue
        # Extra guard: only classify as abandoned if the prompt is about
        # DOING something with Docker (build, deploy, configure), not
        # merely mentioning it in passing
        docker_action_words = re.compile(
            r"\b(?:build|deploy|run|start|stop|install|configure|setup|set\s*up"
            r"|create|remove|delete|push|pull|compose|migrate|container"
            r"|dockerfile|docker-compose|docker\s+build|docker\s+run)\b",
            re.IGNORECASE,
        )
        if not docker_action_words.search(text):
            continue
        return True, reason

    for pattern, reason, _exclude in ABANDONED_CONTEXT_PATTERNS:
        if pattern.search(text):
            # Only abandon old ENC1101 stuff — check timestamp
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    if ts.year < 2025:
                        return True, reason
                except (ValueError, TypeError):
                    pass
    return False, ""


# ---------------------------------------------------------------------------
# Rule 2: SUPERSEDED — >90% content overlap with a later prompt in same thread
# ---------------------------------------------------------------------------
def trigram_set(text: str) -> set[str]:
    """Character trigrams for fast similarity estimation."""
    text = re.sub(r"\s+", " ", text.lower().strip())
    if len(text) < 3:
        return set()
    return {text[i : i + 3] for i in range(len(text) - 2)}


def trigram_similarity(a: str, b: str) -> float:
    """Jaccard similarity on character trigrams. 0.0 to 1.0."""
    sa, sb = trigram_set(a), trigram_set(b)
    if not sa or not sb:
        return 0.0
    intersection = len(sa & sb)
    union = len(sa | sb)
    return intersection / union if union else 0.0


def find_superseded(thread_atoms: list[dict]) -> list[tuple[str, str, float]]:
    """Return list of (atom_id, superseded_by_id, similarity) for atoms with
    >90% overlap with a later prompt in the same thread.

    Threshold is 0.90 for >90% classification confidence.
    At 0.80-0.90 there are edge cases like "step one" vs "step two" that
    look similar on trigrams but ask fundamentally different things.

    Only compares atoms with content long enough to be meaningful (>40 chars).
    The earlier atom is the one marked superseded.
    """
    results = []
    # Sort by turn_index ascending
    sorted_atoms = sorted(
        thread_atoms,
        key=lambda a: a.get("source", {}).get("turn_index", 0),
    )

    for i, earlier in enumerate(sorted_atoms):
        earlier_content = earlier.get("content", "")
        if len(earlier_content) < 40:
            continue
        for later in sorted_atoms[i + 1 :]:
            later_content = later.get("content", "")
            if len(later_content) < 40:
                continue
            sim = trigram_similarity(earlier_content, later_content)
            if sim > 0.90:
                results.append((earlier["id"], later["id"], sim))
                break  # One supersession per atom is enough
    return results


# ---------------------------------------------------------------------------
# Rule 3: ACTUALLY_DONE — git operations confirmed by assistant
# ---------------------------------------------------------------------------
GIT_PROMPT_PATTERN = re.compile(
    r"\b(?:push\s+(?:all\s+)?commit|commit\s+and\s+push|git\s+push|push\s+to\s+"
    r"(?:remote|origin|main|master|production|github)|deploy\s+to\s+production"
    r"|merge\s+and\s+push|push\s+(?:this|these|the)\s+(?:changes?|commits?|branch))\b",
    re.IGNORECASE,
)

GIT_SUCCESS_SIGNALS = [
    re.compile(r"(?:->|→)\s*(?:main|master|origin)", re.IGNORECASE),
    re.compile(r"\b(?:pushed|deployed|merged)\s+(?:successfully|to)\b", re.IGNORECASE),
    re.compile(r"\b(?:git\s+push.*\n.*(?:->|→))", re.IGNORECASE),
    re.compile(r"(?:Writing objects|Total \d+|remote:.*resolving)", re.IGNORECASE),
    re.compile(r"\b(?:\d+\s+files?\s+changed|insertions?\(\+\)|deletions?\(-\))\b", re.IGNORECASE),
    re.compile(r"\bcommitted\b.*\b(?:push|deploy)\b", re.IGNORECASE),
    re.compile(r"\b(?:successfully\s+(?:pushed|deployed|committed))\b", re.IGNORECASE),
]


def check_git_done(atom: dict, response: str | None) -> bool:
    """Return True if the prompt is a git operation and the response confirms success."""
    content = atom.get("content", "")
    if not GIT_PROMPT_PATTERN.search(content):
        return False
    if not response:
        return False
    # Check first 2000 chars of response for success signals
    resp_check = response[:2000]
    return any(sig.search(resp_check) for sig in GIT_SUCCESS_SIGNALS)


# ---------------------------------------------------------------------------
# Rule 4: ACTUALLY_DONE — file operations confirmed by assistant
# ---------------------------------------------------------------------------
FILE_PROMPT_PATTERN = re.compile(
    r"\b(?:create\s+(?:a\s+)?(?:file|script|module|component|page|template|config)"
    r"|write\s+(?:a\s+)?(?:file|script|module|component|function|class)"
    r"|make\s+(?:a\s+)?(?:file|script|new\s+file)"
    r"|save\s+(?:this|that|it)\s+(?:to|as|in)\s+)"
    r"\b",
    re.IGNORECASE,
)

FILE_SUCCESS_SIGNALS = [
    re.compile(r"\b(?:file\s+created|created\s+(?:the\s+)?file)\b", re.IGNORECASE),
    re.compile(r"\b(?:written\s+to|saved\s+to|wrote\s+to)\b", re.IGNORECASE),
    re.compile(r"\b(?:here(?:'s| is)\s+the\s+(?:file|script|code))\b", re.IGNORECASE),
    re.compile(r"\b(?:i'?ve\s+(?:created|written|saved|generated))\b", re.IGNORECASE),
    # Code blocks in response = likely produced the file
    re.compile(r"```\w+\n", re.IGNORECASE),
]


def check_file_done(atom: dict, response: str | None) -> bool:
    """Return True if the prompt is a file operation and the response confirms creation."""
    content = atom.get("content", "")
    if not FILE_PROMPT_PATTERN.search(content):
        return False
    if not response:
        return False
    resp_check = response[:3000]
    # Require at least one success signal
    return any(sig.search(resp_check) for sig in FILE_SUCCESS_SIGNALS)


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------
def get_assistant_response(db_conn: sqlite3.Connection, thread_id: str, turn_index: int) -> str | None:
    """Get the next assistant response after a given turn in a thread."""
    cursor = db_conn.execute(
        """SELECT content FROM chat_turns
           WHERE thread_id = ? AND turn_index > ? AND role = 'assistant'
           ORDER BY turn_index ASC LIMIT 1""",
        (thread_id, turn_index),
    )
    row = cursor.fetchone()
    return row[0] if row else None


def get_review_statuses(review_conn: sqlite3.Connection) -> dict[str, str]:
    """Return dict of prompt_id -> status for all reviewed atoms."""
    cursor = review_conn.execute("SELECT prompt_id, status FROM reviews")
    return {row[0]: row[1] for row in cursor}


def save_review(review_conn: sqlite3.Connection, prompt_id: str, status: str, notes: str) -> None:
    """Write a review decision."""
    now = datetime.now(timezone.utc).isoformat()
    review_conn.execute(
        """INSERT OR REPLACE INTO reviews (prompt_id, status, notes, reviewed_at)
           VALUES (?, ?, ?, ?)""",
        (prompt_id, status, notes, now),
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    if not ATOMS_PATH.exists():
        print(f"ERROR: prompt-atoms.jsonl not found at {ATOMS_PATH}", file=sys.stderr)
        sys.exit(1)

    # Load all atoms
    print(f"Loading atoms from {ATOMS_PATH} ...")
    atoms: list[dict] = []
    with open(ATOMS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    atoms.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    print(f"  Loaded {len(atoms)} atoms")

    # Open DBs
    if KNOWLEDGE_DB.exists():
        kb_conn = sqlite3.connect(f"file:{KNOWLEDGE_DB}?mode=ro", uri=True)
        print(f"  Connected to knowledge.db (read-only)")
    else:
        kb_conn = None
        print(f"  WARNING: knowledge.db not found, rules 3+4 (response checks) disabled")

    review_conn = sqlite3.connect(str(REVIEW_DB))
    # Ensure table exists
    review_conn.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            prompt_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            notes TEXT DEFAULT '',
            reviewed_at TEXT NOT NULL
        )
    """)
    review_conn.execute("""
        CREATE TABLE IF NOT EXISTS undo_stack (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_id TEXT NOT NULL,
            old_status TEXT,
            new_status TEXT NOT NULL,
            undone_at TEXT
        )
    """)
    review_conn.commit()

    review_statuses = get_review_statuses(review_conn)
    # Classify which atoms are candidates for our rules:
    # - Atoms with no review at all (unreviewed)
    # - Atoms with status NEEDS_REVIEW (prior auto-ops couldn't classify)
    # We do NOT re-classify atoms already marked VERIFIED_DONE, DORMANT,
    # or TRANSFORMED unless they match our ABANDONED/SUPERSEDED rules.
    terminal_statuses = {"VERIFIED_DONE", "DORMANT", "TRANSFORMED"}
    needs_work_ids = set()
    for atom in atoms:
        aid = atom["id"]
        current_status = review_statuses.get(aid)
        if current_status is None or current_status == "NEEDS_REVIEW":
            needs_work_ids.add(aid)

    status_dist = defaultdict(int)
    for s in review_statuses.values():
        status_dist[s] += 1
    print(f"  Existing reviews: {len(review_statuses)}")
    for s, c in sorted(status_dist.items(), key=lambda x: -x[1]):
        print(f"    {s}: {c}")
    print(f"  Targetable (unreviewed + NEEDS_REVIEW): {len(needs_work_ids)}")

    # Index atoms by thread for rule 2
    threads: dict[str, list[dict]] = defaultdict(list)
    atoms_by_id: dict[str, dict] = {}
    for atom in atoms:
        atoms_by_id[atom["id"]] = atom
        tid = atom.get("source", {}).get("thread_id", "")
        if tid:
            threads[tid].append(atom)

    # ---------------------------------------------------------------------------
    # Apply rules
    # ---------------------------------------------------------------------------
    classifications: dict[str, tuple[str, str]] = {}  # id -> (status, notes)

    # Counters
    counts = {
        "abandoned": 0,
        "superseded": 0,
        "done_git": 0,
        "done_file": 0,
    }

    # Rule 1: ABANDONED
    print("\nRule 1: Scanning for ABANDONED (defunct tools/services) ...")
    for atom in atoms:
        if atom["id"] not in needs_work_ids:
            continue
        is_abandoned, reason = check_abandoned(atom)
        if is_abandoned:
            classifications[atom["id"]] = (
                "ABANDONED",
                f"auto-classified: abandoned — {reason}",
            )
            counts["abandoned"] += 1

    # Rule 2: SUPERSEDED
    # For superseded detection, we check ALL atoms in a thread (not just
    # needs_work), because a NEEDS_REVIEW atom might be superseded by a
    # VERIFIED_DONE atom. But we only CLASSIFY the needs_work atom.
    print("Rule 2: Scanning for SUPERSEDED (>90% overlap in same thread) ...")
    for tid, thread_atoms in threads.items():
        if len(thread_atoms) < 2:
            continue
        # Check all atoms in thread for overlap, but only mark needs_work ones
        superseded = find_superseded(thread_atoms)
        for earlier_id, later_id, sim_score in superseded:
            if earlier_id in needs_work_ids and earlier_id not in classifications:
                classifications[earlier_id] = (
                    "SUPERSEDED",
                    f"auto-classified: superseded by {later_id} (similarity={sim_score:.2f} in same thread)",
                )
                counts["superseded"] += 1

    # Rules 3 & 4: ACTUALLY_DONE (require knowledge.db)
    if kb_conn:
        print("Rule 3: Scanning for ACTUALLY_DONE (git operations) ...")
        print("Rule 4: Scanning for ACTUALLY_DONE (file operations) ...")

        # Only check atoms still targetable and not already classified
        remaining = [
            a for a in atoms
            if a["id"] in needs_work_ids and a["id"] not in classifications
        ]

        # Batch by thread to reduce DB queries
        remaining_by_thread: dict[str, list[dict]] = defaultdict(list)
        for a in remaining:
            tid = a.get("source", {}).get("thread_id", "")
            if tid:
                remaining_by_thread[tid].append(a)

        response_cache: dict[tuple[str, int], str | None] = {}
        for tid, tatoms in remaining_by_thread.items():
            for atom in tatoms:
                turn_idx = atom.get("source", {}).get("turn_index")
                if turn_idx is None:
                    continue

                cache_key = (tid, turn_idx)
                if cache_key not in response_cache:
                    response_cache[cache_key] = get_assistant_response(kb_conn, tid, turn_idx)
                response = response_cache[cache_key]

                # Rule 3: git ops
                if check_git_done(atom, response):
                    classifications[atom["id"]] = (
                        "ACTUALLY_DONE",
                        "auto-classified: done_git — git operation confirmed by assistant response",
                    )
                    counts["done_git"] += 1
                    continue

                # Rule 4: file ops
                if check_file_done(atom, response):
                    classifications[atom["id"]] = (
                        "ACTUALLY_DONE",
                        "auto-classified: done_file — file operation confirmed by assistant response",
                    )
                    counts["done_file"] += 1

    # ---------------------------------------------------------------------------
    # Write results
    # ---------------------------------------------------------------------------
    total_classified = len(classifications)
    print(f"\n{'=' * 60}")
    print(f"AUTO-CLASSIFICATION RESULTS")
    print(f"{'=' * 60}")
    print(f"Total atoms:            {len(atoms)}")
    print(f"Already terminal:       {len(atoms) - len(needs_work_ids)}")
    print(f"Targetable:             {len(needs_work_ids)}")
    print(f"Auto-classified:        {total_classified}")
    print(f"{'=' * 60}")
    print(f"  ABANDONED:            {counts['abandoned']}")
    print(f"  SUPERSEDED:           {counts['superseded']}")
    print(f"  ACTUALLY_DONE (git):  {counts['done_git']}")
    print(f"  ACTUALLY_DONE (file): {counts['done_file']}")
    print(f"{'=' * 60}")
    remaining_after = len(needs_work_ids) - total_classified
    pct = (total_classified / len(needs_work_ids) * 100) if needs_work_ids else 0
    print(f"Reduction:              {pct:.1f}% of targetable atoms pre-classified")
    print(f"Remaining manual:       {remaining_after}")
    print()

    if DRY_RUN:
        print("[DRY RUN] No changes written to review-results.db")
        # Show samples from each category
        for status_filter in ["ABANDONED", "SUPERSEDED", "ACTUALLY_DONE"]:
            samples = [
                (aid, s, n) for aid, (s, n) in classifications.items() if s == status_filter
            ][:3]
            if samples:
                print(f"\n  Sample {status_filter}:")
                for aid, _s, note in samples:
                    atom = atoms_by_id.get(aid, {})
                    print(f"    {aid}: \"{atom.get('content', '')[:80]}\"")
                    print(f"      -> {note}")
    else:
        print("Writing to review-results.db ...")
        written = 0
        for atom_id, (status, notes) in classifications.items():
            save_review(review_conn, atom_id, status, notes)
            written += 1
        review_conn.commit()
        print(f"  Wrote {written} review decisions")

    # Cleanup
    if kb_conn:
        kb_conn.close()
    review_conn.close()

    print("\nDone.")


if __name__ == "__main__":
    main()
