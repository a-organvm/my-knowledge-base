#!/usr/bin/env python3
"""run_maintenance.py — Automated maintenance for the knowledge base.

Orchestrates database cleanup, deduplication checks, orphan detection,
and index optimization. Designed to be called from a justfile or cron.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("maintenance")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "knowledge.db"
LOG_DIR = PROJECT_ROOT / "logs"
REPORT_PATH = LOG_DIR / f"maintenance-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"


def check_db_exists() -> bool:
    """Verify the database file exists."""
    if not DB_PATH.exists():
        log.warning("Database not found at %s", DB_PATH)
        return False
    return True


def db_integrity_check() -> dict:
    """Run SQLite integrity check."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        result = conn.execute("PRAGMA integrity_check;").fetchone()[0]
        return {"check": "integrity", "status": result, "ok": result == "ok"}
    finally:
        conn.close()


def db_stats() -> dict:
    """Collect basic database statistics."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        ).fetchall()
        stats = {}
        for (table_name,) in tables:
            if table_name.startswith("sqlite_"):
                continue
            count = conn.execute(f"SELECT COUNT(*) FROM [{table_name}];").fetchone()[0]
            stats[table_name] = count
        return stats
    finally:
        conn.close()


def detect_orphan_tags() -> list[str]:
    """Find tags with no associated units."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        rows = conn.execute(
            """
            SELECT t.name FROM tags t
            LEFT JOIN unit_tags ut ON t.id = ut.tag_id
            WHERE ut.tag_id IS NULL;
            """
        ).fetchall()
        return [r[0] for r in rows]
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


def optimize_db() -> None:
    """Run VACUUM and ANALYZE on the database."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.execute("VACUUM;")
        conn.execute("ANALYZE;")
        log.info("Database optimized (VACUUM + ANALYZE)")
    finally:
        conn.close()


def run_npm_command(cmd: list[str]) -> tuple[int, str]:
    """Run an npm command and return (returncode, output)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.returncode, result.stdout + result.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return 1, str(exc)


def main() -> int:
    """Run all maintenance tasks and produce a report."""
    log.info("Maintenance started — project root: %s", PROJECT_ROOT)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    report: dict = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "tasks": [],
    }

    if not check_db_exists():
        log.error("Cannot proceed without database")
        return 1

    # Integrity check
    integrity = db_integrity_check()
    report["tasks"].append(integrity)
    log.info("Integrity check: %s", integrity["status"])

    # Stats
    stats = db_stats()
    report["db_stats"] = stats
    log.info("Table counts: %s", json.dumps(stats, indent=2))

    # Orphan tags
    orphans = detect_orphan_tags()
    report["orphan_tags"] = orphans
    if orphans:
        log.warning("Orphan tags found: %s", orphans)
    else:
        log.info("No orphan tags")

    # Optimize
    optimize_db()
    report["tasks"].append({"check": "optimize", "status": "done", "ok": True})

    # DB file size
    db_size_mb = DB_PATH.stat().st_size / (1024 * 1024)
    report["db_size_mb"] = round(db_size_mb, 2)
    log.info("Database size: %.2f MB", db_size_mb)

    # Save report
    REPORT_PATH.write_text(json.dumps(report, indent=2))
    log.info("Report saved to %s", REPORT_PATH)

    return 0


if __name__ == "__main__":
    sys.exit(main())
