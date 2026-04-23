#!/usr/bin/env python3
"""Update case/atom status in the knowledge base.

Reads atoms from the database, applies status transitions based on
evidence (file existence, completion markers, age), and writes results.

Usage:
    python scripts/update_case_status.py [--dry-run] [--status OPEN]
    python scripts/update_case_status.py --atom-id <id> --new-status CLOSED --reason "Resolved"
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("ukp.case-status")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = PROJECT_ROOT / "orchestrator_state.json"
DB_DIR = PROJECT_ROOT / "db"

VALID_STATUSES = {"OPEN", "ANSWERED", "DEFERRED", "CLOSED", "FAILED", "IN_PROGRESS"}
VALID_TRANSITIONS = {
    "OPEN": {"IN_PROGRESS", "ANSWERED", "DEFERRED", "CLOSED", "FAILED"},
    "IN_PROGRESS": {"ANSWERED", "DEFERRED", "CLOSED", "FAILED"},
    "ANSWERED": {"CLOSED", "OPEN"},
    "DEFERRED": {"OPEN", "CLOSED"},
    "FAILED": {"OPEN", "CLOSED"},
    "CLOSED": {"OPEN"},
}


def load_state() -> dict[str, Any]:
    """Load orchestrator state."""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"atoms": {"by_status": {}}}


def save_state(state: dict[str, Any]) -> None:
    """Persist orchestrator state."""
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    logger.info("State saved to %s", STATE_FILE)


def validate_transition(current: str, target: str) -> bool:
    """Check if a status transition is valid."""
    if current not in VALID_TRANSITIONS:
        logger.warning("Unknown current status: %s", current)
        return False
    return target in VALID_TRANSITIONS[current]


def update_single(
    atom_id: str,
    new_status: str,
    reason: str = "",
    dry_run: bool = False,
) -> bool:
    """Update a single atom's status."""
    # Search atomized directory for the atom
    atomized_dir = PROJECT_ROOT / "atomized"
    if not atomized_dir.exists():
        logger.error("atomized/ directory not found")
        return False

    found = False
    for jsonl_file in atomized_dir.rglob("*.jsonl"):
        lines = jsonl_file.read_text(encoding="utf-8").splitlines()
        updated_lines = []
        for line in lines:
            if not line.strip():
                updated_lines.append(line)
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                updated_lines.append(line)
                continue

            if record.get("atom_id") == atom_id or record.get("id") == atom_id:
                current = record.get("status", "OPEN")
                if not validate_transition(current, new_status):
                    logger.error(
                        "Invalid transition: %s -> %s for atom %s",
                        current, new_status, atom_id,
                    )
                    return False

                logger.info(
                    "Updating atom %s: %s -> %s (reason: %s)",
                    atom_id, current, new_status, reason or "none",
                )
                if not dry_run:
                    record["status"] = new_status
                    record["status_reason"] = reason
                    record["status_updated_at"] = datetime.now(timezone.utc).isoformat()
                found = True

            updated_lines.append(json.dumps(record, ensure_ascii=False))

        if found and not dry_run:
            jsonl_file.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
            break

    if not found:
        logger.warning("Atom %s not found in atomized/", atom_id)
    return found


def bulk_update(
    current_status: str,
    new_status: str,
    reason: str = "",
    dry_run: bool = False,
) -> int:
    """Bulk-update all atoms matching a status."""
    atomized_dir = PROJECT_ROOT / "atomized"
    if not atomized_dir.exists():
        logger.error("atomized/ directory not found")
        return 0

    count = 0
    for jsonl_file in sorted(atomized_dir.rglob("*.jsonl")):
        lines = jsonl_file.read_text(encoding="utf-8").splitlines()
        updated_lines = []
        file_modified = False

        for line in lines:
            if not line.strip():
                updated_lines.append(line)
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                updated_lines.append(line)
                continue

            if record.get("status") == current_status:
                if dry_run:
                    logger.info("  [dry-run] Would update %s", record.get("atom_id", "unknown"))
                else:
                    record["status"] = new_status
                    record["status_reason"] = reason
                    record["status_updated_at"] = datetime.now(timezone.utc).isoformat()
                    file_modified = True
                count += 1

            updated_lines.append(json.dumps(record, ensure_ascii=False))

        if file_modified and not dry_run:
            jsonl_file.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")

    logger.info("Updated %d atoms from %s to %s", count, current_status, new_status)
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="Update atom/case status")
    parser.add_argument("--atom-id", help="Specific atom ID to update")
    parser.add_argument("--new-status", choices=sorted(VALID_STATUSES), help="Target status")
    parser.add_argument("--status", help="Filter: current status to bulk-update from")
    parser.add_argument("--reason", default="", help="Reason for status change")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    if args.atom_id and args.new_status:
        success = update_single(args.atom_id, args.new_status, args.reason, args.dry_run)
        return 0 if success else 1
    elif args.status and args.new_status:
        count = bulk_update(args.status, args.new_status, args.reason, args.dry_run)
        return 0 if count > 0 else 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
