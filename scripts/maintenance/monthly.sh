#!/usr/bin/env bash
set -euo pipefail

# monthly.sh — Monthly deep maintenance for the knowledge base
# Full VACUUM, embedding reindex check, backup verification.
# Intended for on-demand invocation: `./scripts/maintenance/monthly.sh`

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

log() { printf '\033[1;34m[monthly]\033[0m %s\n' "$@"; }
err() { printf '\033[1;31m[error]\033[0m %s\n' "$@" >&2; }

log "Starting monthly maintenance — $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# 1. Run daily maintenance first
log "Running daily maintenance pass..."
bash "$SCRIPT_DIR/daily.sh"

# 2. Full VACUUM (reclaims disk space)
log "Running full VACUUM..."
if [[ -f "$PROJECT_ROOT/db/knowledge.db" ]]; then
  db_size_before=$(stat -f%z "$PROJECT_ROOT/db/knowledge.db" 2>/dev/null || stat --printf=%s "$PROJECT_ROOT/db/knowledge.db" 2>/dev/null || echo "?")
  sqlite3 "$PROJECT_ROOT/db/knowledge.db" "VACUUM;" 2>/dev/null || err "VACUUM failed"
  db_size_after=$(stat -f%z "$PROJECT_ROOT/db/knowledge.db" 2>/dev/null || stat --printf=%s "$PROJECT_ROOT/db/knowledge.db" 2>/dev/null || echo "?")
  log "Database size: ${db_size_before} -> ${db_size_after} bytes"
fi

# 3. Check embedding coverage
log "Checking embedding coverage..."
if [[ -f "$PROJECT_ROOT/db/knowledge.db" ]]; then
  total=$(sqlite3 "$PROJECT_ROOT/db/knowledge.db" "SELECT COUNT(*) FROM atomic_units;" 2>/dev/null || echo "0")
  with_embedding=$(sqlite3 "$PROJECT_ROOT/db/knowledge.db" "SELECT COUNT(*) FROM atomic_units WHERE embedding IS NOT NULL;" 2>/dev/null || echo "0")
  if [[ "$total" -gt 0 ]]; then
    pct=$((with_embedding * 100 / total))
    log "Embedding coverage: ${with_embedding}/${total} (${pct}%)"
    if [[ "$pct" -lt 80 ]]; then
      log "WARNING: Embedding coverage below 80% — run 'npm run generate-embeddings -- --yes'"
    fi
  fi
fi

# 4. FTS index rebuild
log "Rebuilding FTS index..."
if [[ -f "$PROJECT_ROOT/db/knowledge.db" ]]; then
  sqlite3 "$PROJECT_ROOT/db/knowledge.db" "INSERT INTO units_fts(units_fts) VALUES('rebuild');" 2>/dev/null || log "FTS rebuild skipped (table may not exist)"
fi

# 5. Orphan detection
log "Checking for orphaned tags..."
if [[ -f "$PROJECT_ROOT/db/knowledge.db" ]]; then
  orphans=$(sqlite3 "$PROJECT_ROOT/db/knowledge.db" "SELECT COUNT(*) FROM tags t WHERE NOT EXISTS (SELECT 1 FROM unit_tags ut WHERE ut.tag_id = t.id);" 2>/dev/null || echo "?")
  log "Orphaned tags: ${orphans}"
fi

# 6. Backup verification
log "Checking backup freshness..."
latest_backup=$(find "$PROJECT_ROOT/backups" -name "*.db" -o -name "*.sql" 2>/dev/null | sort -r | head -1)
if [[ -n "$latest_backup" ]]; then
  log "Latest backup: $latest_backup"
else
  log "WARNING: No backups found in backups/ — run backup before next maintenance"
fi

log "Monthly maintenance complete — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
