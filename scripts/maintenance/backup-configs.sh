#!/usr/bin/env bash
set -euo pipefail

# backup-configs.sh — Back up configuration files and database
# Creates timestamped snapshots in backups/ for disaster recovery.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/backups"
TIMESTAMP="$(date -u +%Y%m%d-%H%M%S)"

log() { printf '\033[1;34m[backup]\033[0m %s\n' "$@"; }
err() { printf '\033[1;31m[error]\033[0m %s\n' "$@" >&2; }

mkdir -p "$BACKUP_DIR"

log "Starting config backup — $TIMESTAMP"

# 1. Database backup (SQLite online backup)
if [[ -f "$PROJECT_ROOT/db/knowledge.db" ]]; then
  db_backup="$BACKUP_DIR/knowledge-${TIMESTAMP}.db"
  sqlite3 "$PROJECT_ROOT/db/knowledge.db" ".backup '$db_backup'" 2>/dev/null
  log "Database backed up: $db_backup ($(du -h "$db_backup" | cut -f1))"
else
  log "No database to back up"
fi

# 2. Configuration files
config_backup="$BACKUP_DIR/configs-${TIMESTAMP}.tar.gz"
config_files=()
[[ -f "$PROJECT_ROOT/config.yaml" ]] && config_files+=("config.yaml")
[[ -f "$PROJECT_ROOT/ecosystem.yaml" ]] && config_files+=("ecosystem.yaml")
[[ -f "$PROJECT_ROOT/fly.toml" ]] && config_files+=("fly.toml")
[[ -f "$PROJECT_ROOT/docker-compose.yml" ]] && config_files+=("docker-compose.yml")
[[ -f "$PROJECT_ROOT/tsconfig.json" ]] && config_files+=("tsconfig.json")
[[ -f "$PROJECT_ROOT/package.json" ]] && config_files+=("package.json")
[[ -f "$PROJECT_ROOT/.env" ]] && log "WARNING: .env found but NOT backed up (contains secrets)"

if [[ ${#config_files[@]} -gt 0 ]]; then
  (cd "$PROJECT_ROOT" && tar czf "$config_backup" "${config_files[@]}")
  log "Configs backed up: $config_backup (${#config_files[@]} files)"
else
  log "No config files found to back up"
fi

# 3. Prune old backups (keep last 10)
log "Pruning old backups (keeping last 10)..."
for pattern in "knowledge-*.db" "configs-*.tar.gz"; do
  count=$(find "$BACKUP_DIR" -name "$pattern" 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$count" -gt 10 ]]; then
    find "$BACKUP_DIR" -name "$pattern" -print0 | sort -z | head -z -n "$((count - 10))" | xargs -0 rm -f
    log "Pruned $((count - 10)) old $pattern backups"
  fi
done

log "Backup complete — $TIMESTAMP"
