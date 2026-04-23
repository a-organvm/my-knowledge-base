#!/usr/bin/env bash
set -euo pipefail

# monthly.sh — Monthly maintenance tasks for the knowledge base
# Run via cron or manually: ./monthly.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

readonly LOG_DIR="logs"
readonly TIMESTAMP="$(date +%Y-%m-%d_%H%M%S)"
readonly LOG_FILE="${LOG_DIR}/monthly-${TIMESTAMP}.log"

log() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$@" | tee -a "$LOG_FILE"; }

mkdir -p "$LOG_DIR"

log "=== Monthly maintenance started ==="

# 1. Database backup
log "Creating database backup..."
if [[ -f db/knowledge.db ]]; then
  mkdir -p backups
  cp db/knowledge.db "backups/knowledge-${TIMESTAMP}.db"
  log "Backup created: backups/knowledge-${TIMESTAMP}.db"
else
  log "No database found at db/knowledge.db — skipping backup"
fi

# 2. Prune old backups (keep last 6 months)
log "Pruning backups older than 180 days..."
find backups/ -name "knowledge-*.db" -mtime +180 -delete 2>/dev/null || true

# 3. Prune old logs (keep last 90 days)
log "Pruning logs older than 90 days..."
find logs/ -name "*.log" -mtime +90 -delete 2>/dev/null || true

# 4. Database integrity check
log "Running database integrity check..."
if command -v sqlite3 &>/dev/null && [[ -f db/knowledge.db ]]; then
  result="$(sqlite3 db/knowledge.db "PRAGMA integrity_check;" 2>&1)"
  if [[ "$result" == "ok" ]]; then
    log "Database integrity: OK"
  else
    log "WARNING: Database integrity check returned: ${result}"
  fi
fi

# 5. Database optimization
log "Optimizing database..."
if command -v sqlite3 &>/dev/null && [[ -f db/knowledge.db ]]; then
  sqlite3 db/knowledge.db "VACUUM; ANALYZE;" 2>/dev/null
  log "Database optimized (VACUUM + ANALYZE)"
fi

# 6. Dependency audit
log "Checking for outdated dependencies..."
npm outdated 2>/dev/null | tee -a "$LOG_FILE" || true

# 7. Disk usage report
log "Disk usage report:"
du -sh db/ backups/ logs/ node_modules/ 2>/dev/null | tee -a "$LOG_FILE" || true

log "=== Monthly maintenance complete ==="
log "Log saved to: ${LOG_FILE}"
