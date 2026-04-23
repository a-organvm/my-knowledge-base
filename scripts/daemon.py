#!/usr/bin/env python3
"""Knowledge base background daemon.

Watches for new files in intake/, processes them through the pipeline,
and updates orchestrator state. Designed for on-demand invocation, not
as a persistent service (per operational constraints: no LaunchAgents).

Usage:
    python scripts/daemon.py --once          # Single pass
    python scripts/daemon.py --watch         # Watch mode (poll-based)
    python scripts/daemon.py --status        # Show daemon state
"""

from __future__ import annotations

import argparse
import json
import logging
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("ukp.daemon")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INTAKE_DIR = PROJECT_ROOT / "intake"
RAW_DIR = PROJECT_ROOT / "raw"
STATE_FILE = PROJECT_ROOT / "orchestrator_state.json"
LOCK_FILE = PROJECT_ROOT / ".daemon.lock"

POLL_INTERVAL_SECONDS = 30
SHUTDOWN_REQUESTED = False


def handle_signal(sig: int, _frame: Any) -> None:
    """Graceful shutdown handler."""
    global SHUTDOWN_REQUESTED
    logger.info("Received signal %d — shutting down gracefully", sig)
    SHUTDOWN_REQUESTED = True


signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


def acquire_lock() -> bool:
    """Acquire process lock (advisory, not enforced)."""
    if LOCK_FILE.exists():
        try:
            pid = int(LOCK_FILE.read_text().strip())
            # Check if process is still running
            import os
            os.kill(pid, 0)
            logger.error("Daemon already running (PID %d)", pid)
            return False
        except (ProcessLookupError, ValueError):
            logger.warning("Stale lock file found — removing")
            LOCK_FILE.unlink()

    import os
    LOCK_FILE.write_text(str(os.getpid()))
    return True


def release_lock() -> None:
    """Release process lock."""
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()


def load_state() -> dict[str, Any]:
    """Load orchestrator state."""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {
        "version": "1.0.0",
        "pipeline": {"status": "idle"},
        "sources": {"total": 0},
        "atoms": {"total": 0},
        "jobs": {"running": [], "completed": []},
    }


def save_state(state: dict[str, Any]) -> None:
    """Persist orchestrator state."""
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def scan_intake() -> list[Path]:
    """Find unprocessed files in intake/."""
    if not INTAKE_DIR.exists():
        return []
    return sorted(
        f for f in INTAKE_DIR.rglob("*")
        if f.is_file()
        and not f.name.startswith(".")
        and not f.name.endswith(".processed")
    )


def process_file(path: Path, state: dict[str, Any]) -> bool:
    """Process a single intake file."""
    logger.info("Processing: %s", path.relative_to(PROJECT_ROOT))

    try:
        # Delegate to ingest.py if available
        ingest_script = PROJECT_ROOT / "tools" / "ingest.py"
        if ingest_script.exists():
            import subprocess
            result = subprocess.run(
                [sys.executable, str(ingest_script), "--source", str(path)],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                logger.error("Ingest failed for %s: %s", path.name, result.stderr)
                return False
        else:
            # Minimal fallback: copy to raw/
            RAW_DIR.mkdir(parents=True, exist_ok=True)
            dest = RAW_DIR / path.name
            if not dest.exists():
                import shutil
                shutil.copy2(path, dest)

        # Mark as processed
        processed_marker = path.with_suffix(path.suffix + ".processed")
        processed_marker.touch()

        # Update state
        state.setdefault("sources", {})
        state["sources"]["total"] = state["sources"].get("total", 0) + 1
        state["sources"]["last_ingest"] = datetime.now(timezone.utc).isoformat()

        return True

    except Exception as e:
        logger.error("Error processing %s: %s", path.name, e)
        return False


def run_once() -> int:
    """Single processing pass."""
    state = load_state()
    files = scan_intake()

    if not files:
        logger.info("No files pending in intake/")
        return 0

    logger.info("Found %d files to process", len(files))
    state["pipeline"]["status"] = "running"
    save_state(state)

    success = 0
    for path in files:
        if process_file(path, state):
            success += 1

    state["pipeline"]["status"] = "idle"
    save_state(state)

    logger.info("Processed %d/%d files", success, len(files))
    return 0


def run_watch() -> int:
    """Poll-based watch mode."""
    logger.info("Starting watch mode (poll every %ds)", POLL_INTERVAL_SECONDS)

    if not acquire_lock():
        return 1

    try:
        while not SHUTDOWN_REQUESTED:
            run_once()
            for _ in range(POLL_INTERVAL_SECONDS):
                if SHUTDOWN_REQUESTED:
                    break
                time.sleep(1)
    finally:
        release_lock()
        logger.info("Daemon stopped")

    return 0


def show_status() -> int:
    """Display current daemon and pipeline status."""
    state = load_state()
    print(json.dumps(state, indent=2))

    if LOCK_FILE.exists():
        pid = LOCK_FILE.read_text().strip()
        print(f"\nDaemon lock: active (PID {pid})")
    else:
        print("\nDaemon lock: none")

    files = scan_intake()
    print(f"Pending intake files: {len(files)}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Knowledge base pipeline daemon")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--once", action="store_true", help="Single processing pass")
    group.add_argument("--watch", action="store_true", help="Poll-based watch mode")
    group.add_argument("--status", action="store_true", help="Show daemon state")
    args = parser.parse_args()

    if args.once:
        return run_once()
    elif args.watch:
        return run_watch()
    elif args.status:
        return show_status()
    return 1


if __name__ == "__main__":
    sys.exit(main())
