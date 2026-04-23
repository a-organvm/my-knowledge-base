#!/usr/bin/env bash
set -euo pipefail

# run_kimt_extract.sh — Extract and organize KIMT media archives
# Processes Dropbox and iMazing exports into normalized directory structures.
#
# Usage:
#   ./tools/run_kimt_extract.sh <source_dir> [--output <output_dir>] [--dry-run]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SOURCE_DIR=""
OUTPUT_DIR="${PROJECT_ROOT}/raw/kimt-extract"
DRY_RUN=false

# --- Argument parsing ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output)  OUTPUT_DIR="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    --help|-h)
      echo "Usage: $0 <source_dir> [--output <dir>] [--dry-run]"
      echo ""
      echo "Extracts media files from KIMT archives (Dropbox/iMazing backups)."
      echo "Normalizes filenames, deduplicates by content hash, organizes by date."
      exit 0
      ;;
    *)
      if [[ -z "$SOURCE_DIR" ]]; then
        SOURCE_DIR="$1"
      fi
      shift
      ;;
  esac
done

if [[ -z "$SOURCE_DIR" ]]; then
  echo "ERROR: Source directory required."
  echo "Usage: $0 <source_dir> [--output <dir>] [--dry-run]"
  exit 1
fi

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "ERROR: Source directory not found: $SOURCE_DIR"
  exit 1
fi

echo "=== KIMT Extract ==="
echo "  Source:  $SOURCE_DIR"
echo "  Output:  $OUTPUT_DIR"
echo "  Dry run: $DRY_RUN"
echo ""

# Create output structure
if [[ "$DRY_RUN" == false ]]; then
  mkdir -p "${OUTPUT_DIR}"/{photos,videos,documents,audio,other}
fi

# Count files
TOTAL=0
SKIPPED=0
PROCESSED=0

process_file() {
  local file="$1"
  local ext="${file##*.}"
  ext="$(echo "$ext" | tr '[:upper:]' '[:lower:]')"

  # Classify by extension
  local category="other"
  case "$ext" in
    jpg|jpeg|png|heic|heif|gif|tiff|webp|raw|cr2|nef|dng)
      category="photos" ;;
    mp4|mov|avi|mkv|m4v|webm|3gp)
      category="videos" ;;
    pdf|doc|docx|txt|rtf|pages|xlsx|csv)
      category="documents" ;;
    mp3|m4a|wav|aac|flac|ogg|aiff)
      category="audio" ;;
  esac

  # Compute content hash for dedup
  local hash
  hash="$(shasum -a 256 "$file" | cut -c1-12)"
  local basename
  basename="$(basename "$file")"
  local dest="${OUTPUT_DIR}/${category}/${hash}_${basename}"

  if [[ -f "$dest" ]]; then
    ((SKIPPED++)) || true
    return
  fi

  if [[ "$DRY_RUN" == true ]]; then
    echo "  [dry-run] $file -> ${category}/${hash}_${basename}"
  else
    cp "$file" "$dest"
  fi
  ((PROCESSED++)) || true
}

# Walk source directory
while IFS= read -r -d '' file; do
  ((TOTAL++)) || true
  process_file "$file"
done < <(find "$SOURCE_DIR" -type f -print0)

echo ""
echo "=== Summary ==="
echo "  Total files:    $TOTAL"
echo "  Processed:      $PROCESSED"
echo "  Skipped (dupe): $SKIPPED"
