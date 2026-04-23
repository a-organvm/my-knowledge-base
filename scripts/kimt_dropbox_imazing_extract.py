#!/usr/bin/env python3
"""KIMT Dropbox/iMazing media extraction tool.

Extracts, deduplicates, and normalizes media files from Dropbox sync
folders and iMazing iOS backup exports. Organizes output by media type
and date.

Usage:
    python scripts/kimt_dropbox_imazing_extract.py --source ~/Dropbox/KIMT --output ./raw/kimt
    python scripts/kimt_dropbox_imazing_extract.py --source /path/to/iMazing/export --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("kimt.extract")

# Media type classification by extension
MEDIA_CATEGORIES: dict[str, list[str]] = {
    "photos": ["jpg", "jpeg", "png", "heic", "heif", "gif", "tiff", "webp",
               "raw", "cr2", "nef", "dng", "arw", "bmp"],
    "videos": ["mp4", "mov", "avi", "mkv", "m4v", "webm", "3gp", "wmv",
               "flv", "mpg", "mpeg"],
    "audio": ["mp3", "m4a", "wav", "aac", "flac", "ogg", "aiff", "wma",
              "opus"],
    "documents": ["pdf", "doc", "docx", "txt", "rtf", "pages", "xlsx",
                   "xls", "csv", "pptx", "ppt", "key", "numbers"],
}

# Reverse lookup: extension -> category
EXT_TO_CATEGORY: dict[str, str] = {}
for cat, exts in MEDIA_CATEGORIES.items():
    for ext in exts:
        EXT_TO_CATEGORY[ext] = cat


def file_hash(path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA-256 hash of file content (first 1MB for speed)."""
    h = hashlib.sha256()
    bytes_read = 0
    max_bytes = 1024 * 1024  # 1MB sample for large files
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
            bytes_read += len(chunk)
            if bytes_read >= max_bytes:
                break
    return h.hexdigest()[:16]


def classify_file(path: Path) -> str:
    """Classify a file into a media category."""
    ext = path.suffix.lstrip(".").lower()
    return EXT_TO_CATEGORY.get(ext, "other")


def extract_date(path: Path) -> str:
    """Extract date from file metadata or name, fallback to mtime."""
    # Try to parse date from filename patterns like IMG_20231225, 2023-12-25
    name = path.stem
    import re
    # Pattern: YYYYMMDD or YYYY-MM-DD or YYYY_MM_DD
    match = re.search(r"(20\d{2})[-_]?(\d{2})[-_]?(\d{2})", name)
    if match:
        return f"{match.group(1)}-{match.group(2)}"

    # Fallback to file modification time
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return mtime.strftime("%Y-%m")


def run_extraction(
    source: Path,
    output: Path,
    dry_run: bool = False,
    skip_duplicates: bool = True,
) -> dict[str, Any]:
    """Main extraction loop."""
    stats = {
        "total_scanned": 0,
        "extracted": 0,
        "duplicates_skipped": 0,
        "errors": 0,
        "by_category": {},
    }

    seen_hashes: set[str] = set()

    # Pre-scan existing output for dedup
    if skip_duplicates and output.exists():
        logger.info("Pre-scanning output directory for existing files...")
        for existing in output.rglob("*"):
            if existing.is_file():
                seen_hashes.add(file_hash(existing))
        logger.info("Found %d existing files in output", len(seen_hashes))

    # Walk source
    source_files = sorted(
        f for f in source.rglob("*")
        if f.is_file() and not f.name.startswith(".")
    )
    logger.info("Found %d files in source: %s", len(source_files), source)

    for path in source_files:
        stats["total_scanned"] += 1

        # Compute hash
        try:
            fhash = file_hash(path)
        except OSError as e:
            logger.warning("Cannot read %s: %s", path, e)
            stats["errors"] += 1
            continue

        # Dedup check
        if skip_duplicates and fhash in seen_hashes:
            stats["duplicates_skipped"] += 1
            continue
        seen_hashes.add(fhash)

        # Classify and extract date
        category = classify_file(path)
        date_folder = extract_date(path)
        dest_dir = output / category / date_folder
        dest_file = dest_dir / f"{fhash}_{path.name}"

        # Track stats
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

        if dry_run:
            logger.debug("  [dry-run] %s -> %s/%s/%s", path.name, category, date_folder, dest_file.name)
        else:
            dest_dir.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(path, dest_file)
            except OSError as e:
                logger.error("Copy failed for %s: %s", path.name, e)
                stats["errors"] += 1
                continue

        stats["extracted"] += 1

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract and organize KIMT media from Dropbox/iMazing exports"
    )
    parser.add_argument("--source", type=Path, required=True, help="Source directory")
    parser.add_argument("--output", type=Path, default=Path("raw/kimt"), help="Output directory")
    parser.add_argument("--no-dedup", action="store_true", help="Disable duplicate detection")
    parser.add_argument("--dry-run", action="store_true", help="Preview without copying")
    args = parser.parse_args()

    if not args.source.exists():
        logger.error("Source directory not found: %s", args.source)
        return 1

    logger.info("=== KIMT Extract ===")
    logger.info("  Source: %s", args.source)
    logger.info("  Output: %s", args.output)
    logger.info("  Dedup:  %s", "disabled" if args.no_dedup else "enabled")
    logger.info("  Mode:   %s", "dry-run" if args.dry_run else "live")

    stats = run_extraction(
        source=args.source,
        output=args.output,
        dry_run=args.dry_run,
        skip_duplicates=not args.no_dedup,
    )

    logger.info("")
    logger.info("=== Results ===")
    logger.info("  Scanned:    %d", stats["total_scanned"])
    logger.info("  Extracted:  %d", stats["extracted"])
    logger.info("  Duplicates: %d", stats["duplicates_skipped"])
    logger.info("  Errors:     %d", stats["errors"])
    for cat, count in sorted(stats["by_category"].items()):
        logger.info("  %s: %d", cat, count)

    return 0


if __name__ == "__main__":
    sys.exit(main())
