#!/usr/bin/env bash
set -euo pipefail

# backup-configs.sh — Backup configuration files from the knowledge base
# Creates timestamped tarballs of config, scripts, and state files.
#
# Usage:
#   ./scripts/backup-configs.sh [--output <dir>] [--include-db]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

TIMESTAMP="$(date -u +%Y%m%d-%H%M%S)"
OUTPUT_DIR="${PROJECT_ROOT}/backups"
INCLUDE_DB=false
BACKUP_NAME="config-backup-${TIMESTAMP}"

# --- Argument parsing ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output)     OUTPUT_DIR="$2"; shift 2 ;;
    --include-db) INCLUDE_DB=true; shift ;;
    --help|-h)
      echo "Usage: $0 [--output <dir>] [--include-db]"
      echo ""
      echo "Creates a timestamped backup of configuration and state files."
      echo ""
      echo "Options:"
      echo "  --output <dir>   Backup output directory (default: ./backups)"
      echo "  --include-db     Include database files in backup"
      exit 0
      ;;
    *) shift ;;
  esac
done

mkdir -p "${OUTPUT_DIR}"

echo "=== Config Backup ==="
echo "  Project: ${PROJECT_ROOT}"
echo "  Output:  ${OUTPUT_DIR}/${BACKUP_NAME}.tar.gz"
echo ""

# Build file list
FILES_TO_BACKUP=()

# Configuration files
for f in config.yaml ecosystem.yaml seed.yaml network-map.yaml tsconfig.json \
         package.json vitest.config.ts docker-compose.yml Dockerfile fly.toml; do
  if [[ -f "${PROJECT_ROOT}/${f}" ]]; then
    FILES_TO_BACKUP+=("${f}")
  fi
done

# Config directory
if [[ -d "${PROJECT_ROOT}/config" ]]; then
  FILES_TO_BACKUP+=("config/")
fi

# State files
for f in orchestrator_state.json .orchestrator_state.json response.json; do
  if [[ -f "${PROJECT_ROOT}/${f}" ]]; then
    FILES_TO_BACKUP+=("${f}")
  fi
done

# Database (optional)
if [[ "$INCLUDE_DB" == true ]] && [[ -d "${PROJECT_ROOT}/db" ]]; then
  FILES_TO_BACKUP+=("db/")
fi

if [[ ${#FILES_TO_BACKUP[@]} -eq 0 ]]; then
  echo "WARNING: No files found to backup."
  exit 0
fi

echo "Files to backup:"
for f in "${FILES_TO_BACKUP[@]}"; do
  echo "  - ${f}"
done
echo ""

# Create tarball
cd "${PROJECT_ROOT}"
tar -czf "${OUTPUT_DIR}/${BACKUP_NAME}.tar.gz" "${FILES_TO_BACKUP[@]}"

# Verify
SIZE="$(du -h "${OUTPUT_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)"
echo "Backup created: ${OUTPUT_DIR}/${BACKUP_NAME}.tar.gz (${SIZE})"

# Cleanup old backups (keep last 10)
BACKUP_COUNT="$(find "${OUTPUT_DIR}" -name 'config-backup-*.tar.gz' | wc -l | tr -d ' ')"
if [[ "$BACKUP_COUNT" -gt 10 ]]; then
  echo "Cleaning up old backups (keeping last 10)..."
  find "${OUTPUT_DIR}" -name 'config-backup-*.tar.gz' -type f \
    | sort | head -n "$((BACKUP_COUNT - 10))" \
    | xargs rm -f
fi

echo "=== Backup complete ==="
