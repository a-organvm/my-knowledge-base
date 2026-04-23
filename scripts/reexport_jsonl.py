#!/usr/bin/env python3
"""Re-export atomic_units from knowledge.db to monthly-partitioned JSONL files.

Replaces stale JSONL files that still contain deleted garbage entries.

Usage: python3 scripts/reexport_jsonl.py
"""

import json
import sqlite3
from collections import defaultdict
from pathlib import Path

DB_PATH = Path.home() / "Workspace/organvm/my-knowledge-base/db/knowledge.db"
OUTPUT_DIR = Path.home() / "Workspace/organvm/my-knowledge-base/atomized/jsonl"
MAX_LINES_PER_FILE = 4000


def main():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as c FROM atomic_units")
    total = cursor.fetchone()["c"]
    print(f"Exporting {total} atomic units...")

    cursor.execute("""
        SELECT id, type, title, content, context, tags, category,
               timestamp, conversation_id, document_id, source_type, priority
        FROM atomic_units
        ORDER BY timestamp, id
    """)

    # Group by month
    by_month = defaultdict(list)
    for row in cursor:
        ts = row["timestamp"] or ""
        if len(ts) >= 7:
            month = ts[:7]  # YYYY-MM
        else:
            month = "unknown"

        record = {
            "id": row["id"],
            "type": row["type"],
            "title": row["title"],
            "content": row["content"],
            "context": row["context"],
            "tags": json.loads(row["tags"]) if row["tags"] else [],
            "category": row["category"],
            "timestamp": row["timestamp"],
            "conversationId": row["conversation_id"],
            "documentId": row["document_id"],
            "sourceType": row["source_type"],
            "priority": row["priority"],
        }
        by_month[month].append(record)

    conn.close()

    # Clear existing files
    existing = list(OUTPUT_DIR.glob("atoms-*.jsonl"))
    for f in existing:
        f.unlink()
    print(f"  Cleared {len(existing)} stale files")

    # Write new files
    total_written = 0
    file_count = 0

    for month in sorted(by_month.keys()):
        records = by_month[month]

        if len(records) <= MAX_LINES_PER_FILE:
            path = OUTPUT_DIR / f"atoms-{month}.jsonl"
            with open(path, "w") as f:
                for r in records:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            file_count += 1
        else:
            # Split into parts
            for part_idx in range(0, len(records), MAX_LINES_PER_FILE):
                part_num = part_idx // MAX_LINES_PER_FILE + 1
                path = OUTPUT_DIR / f"atoms-{month}-part{part_num:02d}.jsonl"
                chunk = records[part_idx : part_idx + MAX_LINES_PER_FILE]
                with open(path, "w") as f:
                    for r in chunk:
                        f.write(json.dumps(r, ensure_ascii=False) + "\n")
                file_count += 1

        total_written += len(records)

    print(f"\nDone: {total_written} records → {file_count} files")
    print(f"  Output: {OUTPUT_DIR}")

    # Verify
    verify_count = 0
    for f in OUTPUT_DIR.glob("atoms-*.jsonl"):
        with open(f) as fh:
            verify_count += sum(1 for _ in fh)
    print(f"  Verification: {verify_count} lines (expected {total})")
    if verify_count == total:
        print("  MATCH")
    else:
        print(f"  MISMATCH: {verify_count} vs {total}")


if __name__ == "__main__":
    main()
