#!/usr/bin/env bash
set -euo pipefail

# monthly.sh — Monthly maintenance tasks for the knowledge base
# Run manually at month end. Performs deep analysis, archival, and reporting.
#
# Usage:
#   ./scripts/monthly.sh [--verbose]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

VERBOSE=false
[[ "${1:-}" == "--verbose" ]] && VERBOSE=true

MONTH="$(date -u +%Y-%m)"
LOG_FILE="${PROJECT_ROOT}/logs/monthly-${MONTH}.log"
mkdir -p "${PROJECT_ROOT}/logs"

log() {
  local msg="[$(date -u +%H:%M:%S)] $*"
  echo "$msg"
  echo "$msg" >> "$LOG_FILE"
}

log "=== Monthly Maintenance: ${MONTH} ==="
log ""

# 1. Full backup
log "[1/6] Creating full backup..."
if [[ -f "${PROJECT_ROOT}/scripts/backup-configs.sh" ]]; then
  bash "${PROJECT_ROOT}/scripts/backup-configs.sh" --include-db 2>&1 | tee -a "$LOG_FILE"
fi

# 2. Atom statistics
log ""
log "[2/6] Generating atom statistics..."
TOTAL_ATOMS=0
TOTAL_FILES=0
if [[ -d "${PROJECT_ROOT}/atomized" ]]; then
  TOTAL_FILES="$(find "${PROJECT_ROOT}/atomized" -name '*.jsonl' -type f | wc -l | tr -d ' ')"
  TOTAL_ATOMS="$(find "${PROJECT_ROOT}/atomized" -name '*.jsonl' -exec cat {} \; | wc -l | tr -d ' ')"
fi
log "  Atom files: ${TOTAL_FILES}"
log "  Total atoms: ${TOTAL_ATOMS}"

# 3. Disk usage report
log ""
log "[3/6] Disk usage report..."
for dir in intake raw atomized db logs backups node_modules; do
  if [[ -d "${PROJECT_ROOT}/${dir}" ]]; then
    SIZE="$(du -sh "${PROJECT_ROOT}/${dir}" 2>/dev/null | cut -f1)"
    log "  ${dir}/: ${SIZE}"
  fi
done
TOTAL_SIZE="$(du -sh "${PROJECT_ROOT}" 2>/dev/null | cut -f1)"
log "  TOTAL: ${TOTAL_SIZE}"

# 4. Archive old logs
log ""
log "[4/6] Archiving old logs..."
ARCHIVE_DIR="${PROJECT_ROOT}/logs/archive/${MONTH}"
mkdir -p "${ARCHIVE_DIR}"
OLD_LOGS="$(find "${PROJECT_ROOT}/logs" -maxdepth 1 -name 'daily-*.log' -mtime +30 2>/dev/null | wc -l | tr -d ' ')"
if [[ "$OLD_LOGS" -gt 0 ]]; then
  find "${PROJECT_ROOT}/logs" -maxdepth 1 -name 'daily-*.log' -mtime +30 \
    -exec mv {} "${ARCHIVE_DIR}/" \;
  log "  Archived ${OLD_LOGS} daily logs to ${ARCHIVE_DIR}/"
else
  log "  No old logs to archive"
fi

# 5. Stale atom detection
log ""
log "[5/6] Detecting stale atoms..."
if [[ -f "${PROJECT_ROOT}/scripts/close_stale_code_atoms.py" ]]; then
  python3 "${PROJECT_ROOT}/scripts/close_stale_code_atoms.py" --dry-run 2>&1 | tail -5 | tee -a "$LOG_FILE"
else
  log "  Stale atom script not found"
fi

# 6. Summary
log ""
log "[6/6] Monthly summary..."
log "  Month: ${MONTH}"
log "  Atoms: ${TOTAL_ATOMS}"
log "  Disk: ${TOTAL_SIZE}"
log "  Logs archived: ${OLD_LOGS}"

BACKUP_COUNT="$(find "${PROJECT_ROOT}/backups" -name '*.tar.gz' -type f 2>/dev/null | wc -l | tr -d ' ')"
log "  Backups: ${BACKUP_COUNT}"

log ""
log "=== Monthly maintenance complete ==="
log "  Report: ${LOG_FILE}"
