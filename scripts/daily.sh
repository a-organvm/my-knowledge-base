#!/usr/bin/env bash
set -euo pipefail

# daily.sh — Daily maintenance tasks for the knowledge base
# Run manually or via cron. Performs intake processing, dedup, and health checks.
#
# Usage:
#   ./scripts/daily.sh [--quick] [--verbose]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

QUICK=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --quick)   QUICK=true; shift ;;
    --verbose) VERBOSE=true; shift ;;
    --help|-h)
      echo "Usage: $0 [--quick] [--verbose]"
      echo ""
      echo "Daily maintenance: intake processing, dedup, health checks."
      echo ""
      echo "Options:"
      echo "  --quick    Skip slow operations (dedup, full reindex)"
      echo "  --verbose  Show detailed output"
      exit 0
      ;;
    *) shift ;;
  esac
done

TIMESTAMP="$(date -u +%Y-%m-%d)"
LOG_FILE="${PROJECT_ROOT}/logs/daily-${TIMESTAMP}.log"
mkdir -p "${PROJECT_ROOT}/logs"

log() {
  local msg="[$(date -u +%H:%M:%S)] $*"
  echo "$msg"
  echo "$msg" >> "$LOG_FILE"
}

log "=== Daily Maintenance: ${TIMESTAMP} ==="
log ""

# 1. Process intake
log "[1/5] Processing intake directory..."
INTAKE_COUNT="$(find "${PROJECT_ROOT}/intake" -type f ! -name '.*' ! -name '*.processed' 2>/dev/null | wc -l | tr -d ' ')"
log "  Pending intake files: ${INTAKE_COUNT}"

if [[ "$INTAKE_COUNT" -gt 0 ]]; then
  if [[ -f "${PROJECT_ROOT}/tools/ingest.py" ]]; then
    python3 "${PROJECT_ROOT}/tools/ingest.py" --scan-intake 2>&1 | tee -a "$LOG_FILE"
  else
    log "  WARNING: tools/ingest.py not found — skipping intake processing"
  fi
else
  log "  No new files to process."
fi

# 2. Run dedup (skip in quick mode)
if [[ "$QUICK" == false ]]; then
  log ""
  log "[2/5] Running deduplication..."
  if [[ -f "${PROJECT_ROOT}/scripts/dedup_recurring_prompts.py" ]]; then
    python3 "${PROJECT_ROOT}/scripts/dedup_recurring_prompts.py" 2>&1 | tee -a "$LOG_FILE"
  else
    log "  Dedup script not found — skipping"
  fi
else
  log ""
  log "[2/5] Deduplication: SKIPPED (quick mode)"
fi

# 3. Config backup
log ""
log "[3/5] Backing up configuration..."
if [[ -f "${PROJECT_ROOT}/scripts/backup-configs.sh" ]]; then
  bash "${PROJECT_ROOT}/scripts/backup-configs.sh" 2>&1 | tee -a "$LOG_FILE"
else
  log "  Backup script not found — skipping"
fi

# 4. Health check
log ""
log "[4/5] Health check..."

# Check disk usage
DISK_USAGE="$(du -sh "${PROJECT_ROOT}" 2>/dev/null | cut -f1)"
log "  Project size: ${DISK_USAGE}"

# Count key artifacts
ATOM_COUNT="$(find "${PROJECT_ROOT}/atomized" -name '*.jsonl' -type f 2>/dev/null | wc -l | tr -d ' ')"
RAW_COUNT="$(find "${PROJECT_ROOT}/raw" -type f 2>/dev/null | wc -l | tr -d ' ')"
log "  Atom files: ${ATOM_COUNT}"
log "  Raw files: ${RAW_COUNT}"

# Check state file
if [[ -f "${PROJECT_ROOT}/orchestrator_state.json" ]]; then
  PIPELINE_STATUS="$(python3 -c "import json; print(json.load(open('${PROJECT_ROOT}/orchestrator_state.json')).get('pipeline',{}).get('status','unknown'))" 2>/dev/null || echo 'error')"
  log "  Pipeline status: ${PIPELINE_STATUS}"
else
  log "  WARNING: orchestrator_state.json missing"
fi

# 5. Log rotation
log ""
log "[5/5] Log rotation..."
OLD_LOGS="$(find "${PROJECT_ROOT}/logs" -name 'daily-*.log' -mtime +30 2>/dev/null | wc -l | tr -d ' ')"
if [[ "$OLD_LOGS" -gt 0 ]]; then
  find "${PROJECT_ROOT}/logs" -name 'daily-*.log' -mtime +30 -delete
  log "  Removed ${OLD_LOGS} logs older than 30 days"
else
  log "  No old logs to rotate"
fi

log ""
log "=== Daily maintenance complete ==="
