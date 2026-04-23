#!/usr/bin/env bash
set -euo pipefail

# weekly.sh — Weekly governance and maintenance tasks
# Checks system health, runs audits, and generates status reports.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
cd "$PROJECT_ROOT"

readonly LOG_DIR="logs"
readonly TIMESTAMP="$(date +%Y-%m-%d_%H%M%S)"
readonly LOG_FILE="${LOG_DIR}/weekly-${TIMESTAMP}.log"

log() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$@" | tee -a "$LOG_FILE"; }

mkdir -p "$LOG_DIR"

log "=== Weekly governance check started ==="

# 1. Database health
log "Checking database health..."
if [[ -f db/knowledge.db ]]; then
  size="$(du -h db/knowledge.db | cut -f1)"
  log "Database size: ${size}"

  if command -v sqlite3 &>/dev/null; then
    unit_count="$(sqlite3 db/knowledge.db "SELECT COUNT(*) FROM atomic_units;" 2>/dev/null || echo "N/A")"
    log "Atomic units: ${unit_count}"
  fi
fi

# 2. Check for untagged units
log "Checking for untagged units..."
if command -v sqlite3 &>/dev/null && [[ -f db/knowledge.db ]]; then
  untagged="$(sqlite3 db/knowledge.db "SELECT COUNT(*) FROM atomic_units WHERE id NOT IN (SELECT unit_id FROM unit_tags);" 2>/dev/null || echo "N/A")"
  log "Untagged units: ${untagged}"
fi

# 3. Git status check
log "Checking git status..."
if git rev-parse --is-inside-work-tree &>/dev/null; then
  uncommitted="$(git status --porcelain | wc -l | tr -d ' ')"
  log "Uncommitted changes: ${uncommitted}"

  branch="$(git branch --show-current 2>/dev/null || echo "detached")"
  log "Current branch: ${branch}"
fi

# 4. Dependency security audit
log "Running npm audit..."
npm audit --omit=dev 2>/dev/null | tail -5 | tee -a "$LOG_FILE" || log "npm audit skipped"

# 5. Disk usage summary
log "Disk usage summary:"
du -sh db/ backups/ logs/ 2>/dev/null | tee -a "$LOG_FILE" || true

# 6. Build check
log "Verifying build..."
if npm run build --silent 2>/dev/null; then
  log "Build: OK"
else
  log "WARNING: Build failed"
fi

log "=== Weekly governance check complete ==="
log "Log: ${LOG_FILE}"
