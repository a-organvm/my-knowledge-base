#!/usr/bin/env python3
"""Mark stale code-domain atoms as ANSWERED/SUPERSEDED.

These atoms are from expired teaching positions, old client work,
and personal content requests from 2024-2025 that can no longer be
executed (semesters ended, employment ended, content delivered).

Criteria for closure:
- Teaching emails/correspondence from positions no longer held
- Student feedback from completed semesters
- Personal content formatting (name analyses, etc.) from 12+ months ago
- Zapier/platform configuration for businesses no longer active

Does NOT close:
- System architecture/PKM items (may still be relevant)
- Code debugging items (may apply to active codebases)
- Items newer than 6 months
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

ATOMS_PATH = Path(__file__).parent.parent.parent / "organvm-corpvs-testamentvm/data/atoms/prompt-atoms.jsonl"
CUTOFF = date(2025, 10, 1)  # Items before this are stale if they match patterns

# Atoms confirmed stale by manual review of the P0 backlog
STALE_P0_IDS = {
    # Teaching correspondence (St. Paul's / Broward) - positions ended
    "prompt-65a3b3826033",  # Student email response (Mar 2025)
    "prompt-30da104830b2",  # Castle Branch faculty docs (Feb 2025)
    "prompt-e615de986242",  # Class absence email (May 2025)
    "prompt-c364d4babf0b",  # Student paper feedback (Feb 2025)
    "prompt-da111d1a7418",  # Faculty observations email (Mar 2025)
    "prompt-35c0a8a279a2",  # Document submissions followup (Mar 2025)
    "prompt-9675480ab08c",  # Document submissions followup (Mar 2025)
    "prompt-ed069a0704a9",  # Compensation inquiry (Mar 2025)
    "prompt-debe0f0637f1",  # Onboarding compensation (Mar 2025)
    # Personal content - delivered or stale
    "prompt-e99e2d3660ba",  # Zapier zaps for Forward Funders (Jan 2025)
    "prompt-8ec3a472f0b5",  # Robert name analysis HTML (Jan 2025)
    "prompt-f28a2cc58b42",  # Jessica name analysis HTML (Jan 2025)
    # Creative/design - stale context
    "prompt-28b1b279ebf2",  # Premiere metadata headers (Mar 2025)
    "prompt-53897203dba6",  # Protocol defining (Apr 2025)
}

# P0 items resolved by scripts created in this session
RESOLVED_P0_IDS = {
    "prompt-cd686c8b4751",  # Hours graph -> compensable_hours_graph.py
    "prompt-4fee8317690e",  # ENC1101 syllabus dates -> enc1101_syllabus_dates.py
}


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    if not ATOMS_PATH.exists():
        print(f"ERROR: Atoms file not found: {ATOMS_PATH}")
        sys.exit(1)

    atoms = []
    modified = 0

    with open(ATOMS_PATH) as f:
        for line in f:
            atom = json.loads(line)

            if atom["id"] in STALE_P0_IDS:
                old_status = atom["status"]
                atom["status"] = "SUPERSEDED"
                atom["needs_review"] = False
                modified += 1
                print(f"  SUPERSEDED: {atom['id']} (was {old_status}) -- {atom['title'][:60]}")

            elif atom["id"] in RESOLVED_P0_IDS:
                old_status = atom["status"]
                atom["status"] = "ANSWERED"
                atom["needs_review"] = False
                modified += 1
                print(f"  ANSWERED:   {atom['id']} (was {old_status}) -- {atom['title'][:60]}")

            atoms.append(atom)

    print(f"\nTotal atoms to update: {modified}")
    print(f"  - SUPERSEDED (stale): {len(STALE_P0_IDS)}")
    print(f"  - ANSWERED (resolved): {len(RESOLVED_P0_IDS)}")

    if dry_run:
        print("\n[DRY RUN] No changes written.")
    else:
        with open(ATOMS_PATH, "w") as f:
            for atom in atoms:
                f.write(json.dumps(atom) + "\n")
        print(f"\nWrote {len(atoms)} atoms to {ATOMS_PATH}")


if __name__ == "__main__":
    main()
