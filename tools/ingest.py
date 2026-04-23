#!/usr/bin/env python3
"""Unified Knowledge Pipeline (UKP) — Ingest module.

Handles intake of knowledge artifacts from multiple sources into the
pipeline's staging area. Supports JSON, JSONL, Markdown, and plain text.

Usage:
    python tools/ingest.py --source <path_or_glob> [--format auto] [--dry-run]
    python tools/ingest.py --provider chatgpt --file export.json
    python tools/ingest.py --scan-intake
"""

from __future__ import annotations

import argparse
import hashlib
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
logger = logging.getLogger("ukp.ingest")

# --- Constants ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INTAKE_DIR = PROJECT_ROOT / "intake"
RAW_DIR = PROJECT_ROOT / "raw"
DB_DIR = PROJECT_ROOT / "db"
STATE_FILE = PROJECT_ROOT / "orchestrator_state.json"

SUPPORTED_FORMATS = {"json", "jsonl", "md", "txt", "csv"}
KNOWN_PROVIDERS = {"chatgpt", "claude", "gemini", "grok", "copilot", "perplexity"}


def compute_content_hash(content: str) -> str:
    """SHA-256 content hash for deduplication."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def detect_format(path: Path) -> str:
    """Auto-detect file format from extension."""
    suffix = path.suffix.lstrip(".").lower()
    if suffix in SUPPORTED_FORMATS:
        return suffix
    if suffix in ("yaml", "yml"):
        return "yaml"
    return "unknown"


def parse_json_export(path: Path) -> list[dict[str, Any]]:
    """Parse a JSON export file (ChatGPT, Claude, etc.)."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # Common shapes: {"conversations": [...]}, {"data": [...]}
        for key in ("conversations", "data", "messages", "items", "prompts"):
            if key in data and isinstance(data[key], list):
                return data[key]
        return [data]
    return []


def parse_jsonl_export(path: Path) -> list[dict[str, Any]]:
    """Parse a JSONL file (one JSON object per line)."""
    records: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                logger.warning("Skipping malformed JSON at line %d in %s", line_num, path)
    return records


def parse_markdown(path: Path) -> list[dict[str, Any]]:
    """Parse a markdown file as a single knowledge artifact."""
    content = path.read_text(encoding="utf-8")
    return [{
        "type": "markdown",
        "title": path.stem,
        "content": content,
        "content_hash": compute_content_hash(content),
    }]


def ingest_file(
    path: Path,
    provider: str | None = None,
    fmt: str = "auto",
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Ingest a single file and return normalized records."""
    if not path.exists():
        logger.error("File not found: %s", path)
        return []

    if fmt == "auto":
        fmt = detect_format(path)

    logger.info("Ingesting %s (format=%s, provider=%s)", path.name, fmt, provider or "unknown")

    # Parse based on format
    if fmt == "json":
        records = parse_json_export(path)
    elif fmt == "jsonl":
        records = parse_jsonl_export(path)
    elif fmt in ("md", "txt"):
        records = parse_markdown(path)
    else:
        logger.warning("Unsupported format '%s' for %s — skipping", fmt, path)
        return []

    # Enrich records with metadata
    now = datetime.now(timezone.utc).isoformat()
    for i, record in enumerate(records):
        record.setdefault("_ingest_source", str(path))
        record.setdefault("_ingest_provider", provider or "unknown")
        record.setdefault("_ingest_timestamp", now)
        record.setdefault("_ingest_index", i)
        if "content" in record and "content_hash" not in record:
            record["content_hash"] = compute_content_hash(str(record["content"]))

    if dry_run:
        logger.info("  [dry-run] Would ingest %d records from %s", len(records), path.name)
    else:
        logger.info("  Ingested %d records from %s", len(records), path.name)

    return records


def scan_intake_directory() -> list[Path]:
    """Discover files in the intake directory waiting for processing."""
    if not INTAKE_DIR.exists():
        logger.warning("Intake directory does not exist: %s", INTAKE_DIR)
        return []
    files = sorted(
        f for f in INTAKE_DIR.rglob("*")
        if f.is_file() and not f.name.startswith(".")
    )
    logger.info("Found %d files in intake/", len(files))
    return files


def write_output(records: list[dict[str, Any]], output_path: Path) -> None:
    """Write ingested records to JSONL output."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "a", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    logger.info("Wrote %d records to %s", len(records), output_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="UKP Ingest — Import knowledge artifacts into the pipeline"
    )
    parser.add_argument("--source", type=Path, help="File or directory to ingest")
    parser.add_argument("--provider", choices=sorted(KNOWN_PROVIDERS), help="Source provider")
    parser.add_argument("--format", dest="fmt", default="auto", help="File format (auto-detected)")
    parser.add_argument("--output", type=Path, help="Output JSONL path")
    parser.add_argument("--scan-intake", action="store_true", help="Process all files in intake/")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    if not args.source and not args.scan_intake:
        parser.print_help()
        return 1

    all_records: list[dict[str, Any]] = []

    if args.scan_intake:
        for path in scan_intake_directory():
            records = ingest_file(path, provider=args.provider, dry_run=args.dry_run)
            all_records.extend(records)
    elif args.source:
        if args.source.is_dir():
            for path in sorted(args.source.rglob("*")):
                if path.is_file() and not path.name.startswith("."):
                    records = ingest_file(path, provider=args.provider, fmt=args.fmt, dry_run=args.dry_run)
                    all_records.extend(records)
        else:
            all_records = ingest_file(args.source, provider=args.provider, fmt=args.fmt, dry_run=args.dry_run)

    logger.info("Total records ingested: %d", len(all_records))

    if all_records and not args.dry_run:
        output = args.output or (RAW_DIR / f"ingest-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.jsonl")
        write_output(all_records, output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
