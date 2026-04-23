#!/usr/bin/env python3
"""Export review decisions back into the prompt-atoms JSONL store.

Reads human review verdicts from review-results.db and applies them to each
atom's `status` and `needs_review` fields in prompt-atoms.jsonl. This closes
the loop: human triage -> atom store update.

The original file is backed up before any write. Atoms without a review
decision are left untouched.

Usage:
    python3 scripts/export_reviews.py              # dry-run (default)
    python3 scripts/export_reviews.py --apply       # write changes
    python3 scripts/export_reviews.py --apply --backup-dir /tmp/atoms-backup
"""

import argparse
import json
import shutil
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# -- Paths -----------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
KB_DIR = SCRIPT_DIR.parent
REVIEW_DB = KB_DIR / "db" / "review-results.db"
ATOMS_PATH = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/prompt-atoms.jsonl"
)

# Valid statuses written by prompt-review-server.py
VALID_STATUSES = frozenset({
    "ACTUALLY_DONE",
    "STILL_OPEN",
    "ABANDONED",
    "SUPERSEDED",
    "NEEDS_DECOMPOSITION",
})


# -- DB access --------------------------------------------------------------

def load_reviews() -> dict[str, dict]:
    """Return {prompt_id: {status, notes, reviewed_at}} from review-results.db."""
    if not REVIEW_DB.exists():
        print(f"ERROR: review database not found at {REVIEW_DB}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(str(REVIEW_DB))
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT prompt_id, status, notes, reviewed_at FROM reviews")
    reviews = {}
    invalid_count = 0
    for row in cursor:
        pid = row["prompt_id"]
        st = row["status"]
        if st not in VALID_STATUSES:
            invalid_count += 1
            print(f"  WARNING: skipping invalid status '{st}' for {pid}", file=sys.stderr)
            continue
        reviews[pid] = {
            "status": st,
            "notes": row["notes"] or "",
            "reviewed_at": row["reviewed_at"],
        }
    conn.close()

    if invalid_count:
        print(f"  {invalid_count} rows skipped due to invalid status values", file=sys.stderr)

    return reviews


# -- Status mapping ----------------------------------------------------------

# Map review verdicts to the atom status vocabulary used in the JSONL store.
# The atom store uses uppercase single-word statuses (DONE, OPEN, etc.)
# while the review UI uses more descriptive names.
REVIEW_TO_ATOM_STATUS = {
    "ACTUALLY_DONE": "DONE",
    "STILL_OPEN": "OPEN",
    "ABANDONED": "ABANDONED",
    "SUPERSEDED": "SUPERSEDED",
    "NEEDS_DECOMPOSITION": "NEEDS_DECOMPOSITION",
}


def map_status(review_status: str) -> str:
    """Convert a review verdict to the atom-store status vocabulary."""
    return REVIEW_TO_ATOM_STATUS.get(review_status, review_status)


# -- JSONL processing -------------------------------------------------------

def load_atoms(path: Path) -> list[dict]:
    """Load all atoms from the JSONL file, preserving order."""
    if not path.exists():
        print(f"ERROR: atoms file not found at {path}", file=sys.stderr)
        sys.exit(1)

    atoms = []
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                atoms.append(json.loads(stripped))
            except json.JSONDecodeError as e:
                print(f"  WARNING: skipping malformed JSON at line {lineno}: {e}", file=sys.stderr)
    return atoms


def apply_reviews(atoms: list[dict], reviews: dict[str, dict]) -> tuple[list[dict], Counter]:
    """Apply review decisions to atoms. Returns (updated_atoms, status_counter).

    Only atoms whose id appears in the reviews dict are modified.
    Each modified atom gets:
      - status  -> mapped from the review verdict
      - needs_review -> False
      - review_notes -> notes from reviewer (if non-empty)
      - reviewed_at  -> ISO timestamp of the review
    """
    stats = Counter()
    updated = []

    for atom in atoms:
        aid = atom.get("id", "")
        if aid in reviews:
            review = reviews[aid]
            new_status = map_status(review["status"])
            atom["status"] = new_status
            atom["needs_review"] = False
            if review["notes"]:
                atom["review_notes"] = review["notes"]
            atom["reviewed_at"] = review["reviewed_at"]
            stats[review["status"]] += 1
        updated.append(atom)

    return updated, stats


def write_atoms(atoms: list[dict], path: Path) -> int:
    """Write atoms back to JSONL. Returns line count written."""
    with open(path, "w") as f:
        for atom in atoms:
            f.write(json.dumps(atom, ensure_ascii=False) + "\n")
    return len(atoms)


def backup_file(src: Path, backup_dir: Path | None) -> Path:
    """Create a timestamped backup of the atoms file. Returns backup path."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if backup_dir is None:
        backup_dir = src.parent
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{src.stem}.backup-{ts}{src.suffix}"
    shutil.copy2(src, backup_path)
    return backup_path


# -- Main --------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Export review decisions back into prompt-atoms.jsonl"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write changes (default is dry-run)",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=None,
        help="Directory for backup file (default: same directory as atoms file)",
    )
    args = parser.parse_args()

    # 1. Load reviews from SQLite
    print(f"Loading reviews from {REVIEW_DB}")
    reviews = load_reviews()
    if not reviews:
        print("No reviews found in database. Nothing to export.")
        sys.exit(0)
    print(f"  {len(reviews)} review decisions loaded")

    # 2. Load atoms from JSONL
    print(f"Loading atoms from {ATOMS_PATH}")
    atoms = load_atoms(ATOMS_PATH)
    print(f"  {len(atoms)} atoms loaded")

    # 3. Match reviews to atoms
    atom_ids = {a.get("id", "") for a in atoms}
    matched = sum(1 for pid in reviews if pid in atom_ids)
    orphaned = sum(1 for pid in reviews if pid not in atom_ids)
    if orphaned:
        print(f"  WARNING: {orphaned} reviews reference atoms not in {ATOMS_PATH.name}")

    # 4. Apply review decisions
    updated_atoms, status_counts = apply_reviews(atoms, reviews)

    # 5. Print stats
    total_reviewed = sum(status_counts.values())
    total_atoms = len(atoms)
    pct = (total_reviewed / total_atoms * 100) if total_atoms else 0

    print(f"\n--- Review Export Summary ---")
    print(f"Total atoms:      {total_atoms}")
    print(f"Reviewed:         {total_reviewed} ({pct:.1f}%)")
    print(f"Unreviewed:       {total_atoms - total_reviewed}")
    if orphaned:
        print(f"Orphaned reviews: {orphaned} (review exists, atom missing)")
    print(f"\nStatus distribution:")
    for status in sorted(status_counts, key=lambda s: -status_counts[s]):
        mapped = map_status(status)
        count = status_counts[status]
        bar = "#" * min(count, 60)
        label = f"{status} -> {mapped}" if status != mapped else status
        print(f"  {label:30s} {count:6d}  {bar}")

    # 6. Write or dry-run
    if args.apply:
        backup_path = backup_file(ATOMS_PATH, args.backup_dir)
        print(f"\nBackup written to {backup_path}")

        written = write_atoms(updated_atoms, ATOMS_PATH)
        print(f"Updated {ATOMS_PATH}")
        print(f"  {written} atoms written ({total_reviewed} modified)")

        # Verify round-trip integrity
        verify = load_atoms(ATOMS_PATH)
        if len(verify) != len(atoms):
            print(f"  VERIFICATION FAILED: wrote {len(verify)}, expected {len(atoms)}", file=sys.stderr)
            sys.exit(1)
        print(f"  Verification: {len(verify)} atoms (OK)")
    else:
        print(f"\nDry run -- no files modified. Use --apply to write changes.")


if __name__ == "__main__":
    main()
