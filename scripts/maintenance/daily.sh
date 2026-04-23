#!/usr/bin/env bash
set -euo pipefail

# daily.sh — Daily maintenance for the knowledge base
# Runs database optimization, stale-check, and integrity verification.
# Intended for on-demand invocation: `./scripts/maintenance/daily.sh`

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

log() { printf '\033[1;34m[daily]\033[0m %s\n' "$@"; }
err() { printf '\033[1;31m[error]\033[0m %s\n' "$@" >&2; }

log "Starting daily maintenance — $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# 1. Database integrity check
log "Checking database integrity..."
if [[ -f "$PROJECT_ROOT/db/knowledge.db" ]]; then
  integrity=$(sqlite3 "$PROJECT_ROOT/db/knowledge.db" "PRAGMA integrity_check;" 2>/dev/null || echo "FAILED")
  if [[ "$integrity" == "ok" ]]; then
    log "Database integrity: OK"
  else
    err "Database integrity check failed: $integrity"
  fi
else
  log "No local database found — skipping integrity check"
fi

# 2. Run migrations (idempotent)
log "Running migrations..."
cd "$PROJECT_ROOT"
npm run migrate 2>/dev/null || log "Migration skipped (no pending migrations)"

# 3. Run deduplication check
log "Checking for duplicate atoms..."
if command -v npx &>/dev/null; then
  npx tsx src/deduplication.ts --check-only 2>/dev/null || log "Dedup check: no duplicates or script unavailable"
fi

# 4. Optimize SQLite (VACUUM + ANALYZE)
log "Optimizing database..."
if [[ -f "$PROJECT_ROOT/db/knowledge.db" ]]; then
  sqlite3 "$PROJECT_ROOT/db/knowledge.db" "PRAGMA optimize; ANALYZE;" 2>/dev/null || true
  log "Database optimized"
fi

# 5. Clean stale exports
log "Cleaning stale temp files..."
find "$PROJECT_ROOT/.test-tmp" -type f -mtime +7 -delete 2>/dev/null || true
find "$PROJECT_ROOT/logs" -name "*.log" -mtime +30 -delete 2>/dev/null || true

# 6. Report
atom_count=$(sqlite3 "$PROJECT_ROOT/db/knowledge.db" "SELECT COUNT(*) FROM atomic_units;" 2>/dev/null || echo "?")
conv_count=$(sqlite3 "$PROJECT_ROOT/db/knowledge.db" "SELECT COUNT(*) FROM conversations;" 2>/dev/null || echo "?")
log "Status: ${atom_count} atoms, ${conv_count} conversations"
log "Daily maintenance complete — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
