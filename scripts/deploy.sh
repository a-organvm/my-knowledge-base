#!/usr/bin/env bash
set -euo pipefail

# deploy.sh — Deploy knowledge-base to Fly.io
# Runs pre-flight checks, builds, and deploys.
# Usage: ./scripts/deploy.sh [--dry-run]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

log() { printf '\033[1;34m[deploy]\033[0m %s\n' "$@"; }
err() { printf '\033[1;31m[error]\033[0m %s\n' "$@" >&2; }
die() { err "$@"; exit 1; }

cd "$PROJECT_ROOT"

# --- Pre-flight ---

log "Running pre-flight checks..."

command -v fly &>/dev/null || die "flyctl not installed — brew install flyctl"
command -v node &>/dev/null || die "node not installed"
command -v npm &>/dev/null || die "npm not installed"

[[ -f "fly.toml" ]] || die "fly.toml not found — are you in the right directory?"

# Check git state
if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
  log "WARNING: Uncommitted changes detected"
  git status --short
fi

# --- Build ---

log "Building TypeScript..."
npm run build

log "Running tests..."
npm test -- --reporter=dot 2>/dev/null || {
  err "Tests failed — aborting deploy"
  exit 1
}

# --- Deploy ---

if [[ "$DRY_RUN" == "true" ]]; then
  log "DRY RUN — would deploy to Fly.io"
  fly deploy --config fly.toml --dry-run 2>/dev/null || log "fly deploy --dry-run not supported; skipping"
  exit 0
fi

log "Deploying to Fly.io..."
fly deploy --config fly.toml

log "Verifying deployment health..."
sleep 5
app_url=$(fly info --json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('Hostname',''))" 2>/dev/null || echo "")
if [[ -n "$app_url" ]]; then
  status=$(curl -s -o /dev/null -w "%{http_code}" "https://${app_url}/api/health" 2>/dev/null || echo "000")
  if [[ "$status" == "200" ]]; then
    log "Health check passed (HTTP $status)"
  else
    err "Health check returned HTTP $status — investigate at https://${app_url}"
  fi
fi

log "Deploy complete — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
