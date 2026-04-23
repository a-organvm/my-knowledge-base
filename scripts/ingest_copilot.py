#!/usr/bin/env python3
"""Ingest Copilot JSONL session files into knowledge.db.

Copilot's session-state files are event streams (one JSON object per line)
with types like session.start, user.message, assistant.message, etc.
This script extracts user and assistant messages, creates chat threads
and turns, and inserts them into the same schema used by other providers.

Usage:
    python3 scripts/ingest_copilot.py [--dry-run]
"""

import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "knowledge.db"
SOURCE_DIR = (
    Path(__file__).resolve().parent.parent
    / "intake"
    / "canonical"
    / "sources"
    / "curated-sources"
    / "copilot"
    / "session-state"
)
# source_path stored relative to the intake directory
SOURCE_PATH_PREFIX = "canonical/sources/curated-sources/copilot/session-state"
PROVIDER_REF_ID = "provider-copilot"


def parse_jsonl_file(filepath: Path) -> dict:
    """Stream a JSONL file and extract session metadata + user/assistant messages."""
    session_id = filepath.stem  # UUID filename
    title = None
    messages = []

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            event_type = event.get("type", "")
            data = event.get("data", {})
            timestamp = event.get("timestamp")

            if event_type == "session.start":
                session_id = data.get("sessionId", session_id)

            elif event_type == "user.message":
                content = data.get("content", "")
                if not content or not content.strip():
                    continue
                if title is None:
                    title = content.strip()[:80]
                messages.append({
                    "role": "user",
                    "content": content.strip(),
                    "timestamp": timestamp,
                })

            elif event_type == "assistant.message":
                content = data.get("content", "")
                if not content or not content.strip():
                    continue
                messages.append({
                    "role": "assistant",
                    "content": content.strip(),
                    "timestamp": timestamp,
                })

    return {
        "session_id": session_id,
        "title": title or f"Copilot Session {session_id[:8]}",
        "messages": messages,
    }


def ingest(dry_run: bool = False) -> None:
    if not DB_PATH.exists():
        print(f"ERROR: database not found at {DB_PATH}", file=sys.stderr)
        sys.exit(1)
    if not SOURCE_DIR.exists():
        print(f"ERROR: source directory not found at {SOURCE_DIR}", file=sys.stderr)
        sys.exit(1)

    jsonl_files = sorted(SOURCE_DIR.glob("*.jsonl"))
    if not jsonl_files:
        print("No .jsonl files found in source directory.")
        return

    print(f"Found {len(jsonl_files)} JSONL files to process")

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    cursor = conn.cursor()

    # Check for existing copilot threads to avoid duplicates
    cursor.execute(
        "SELECT source_path FROM chat_threads WHERE provider_ref_id = ?",
        (PROVIDER_REF_ID,),
    )
    existing_paths = {row[0] for row in cursor.fetchall()}

    now = datetime.now(timezone.utc).isoformat()
    total_threads = 0
    total_turns = 0
    skipped = 0

    for filepath in jsonl_files:
        source_path = f"{SOURCE_PATH_PREFIX}/{filepath.name}"

        if source_path in existing_paths:
            print(f"  SKIP (already imported): {filepath.name}")
            skipped += 1
            continue

        print(f"  Processing: {filepath.name} ({filepath.stat().st_size / 1024:.0f} KB)...")
        parsed = parse_jsonl_file(filepath)

        if not parsed["messages"]:
            print(f"    No user/assistant messages found, skipping")
            continue

        thread_id = str(uuid.uuid4())

        if not dry_run:
            cursor.execute(
                """INSERT INTO chat_threads
                   (id, provider_ref_id, external_thread_id, title, source_path, created_at, updated_at, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    thread_id,
                    PROVIDER_REF_ID,
                    parsed["session_id"],
                    parsed["title"],
                    source_path,
                    now,
                    now,
                    json.dumps({"importer": "ingest_copilot.py"}),
                ),
            )

        for idx, msg in enumerate(parsed["messages"]):
            turn_id = str(uuid.uuid4())
            if not dry_run:
                cursor.execute(
                    """INSERT INTO chat_turns
                       (id, thread_id, turn_index, role, content, timestamp, metadata, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        turn_id,
                        thread_id,
                        idx,
                        msg["role"],
                        msg["content"],
                        msg["timestamp"],
                        json.dumps({"importer": "copilot"}),
                        now,
                    ),
                )

        total_threads += 1
        total_turns += len(parsed["messages"])
        print(f"    -> {len(parsed['messages'])} turns ({parsed['title'][:50]})")

    if not dry_run:
        # Update provider timestamp
        cursor.execute(
            "UPDATE providers SET updated_at = ? WHERE id = ?",
            (now, PROVIDER_REF_ID),
        )
        conn.commit()

    conn.close()

    print(f"\nDone: {total_threads} threads, {total_turns} turns inserted")
    if skipped:
        print(f"  Skipped {skipped} already-imported files")
    if dry_run:
        print("  (DRY RUN — no data written)")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    ingest(dry_run=dry_run)
