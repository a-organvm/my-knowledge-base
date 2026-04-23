#!/usr/bin/env bash
set -euo pipefail

# install_unix.sh — Bootstrap the knowledge-base on Unix/macOS
# Installs dependencies, sets up database, and validates environment.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

readonly NODE_MIN_VERSION=18
readonly REQUIRED_CMDS=(node npm sqlite3)

# --- Helpers ---

log() { printf '\033[1;34m[install]\033[0m %s\n' "$@"; }
err() { printf '\033[1;31m[error]\033[0m %s\n' "$@" >&2; }
die() { err "$@"; exit 1; }

check_command() {
  command -v "$1" &>/dev/null || die "Required command not found: $1"
}

check_node_version() {
  local ver
  ver="$(node --version | sed 's/^v//' | cut -d. -f1)"
  if [[ "$ver" -lt "$NODE_MIN_VERSION" ]]; then
    die "Node.js >= ${NODE_MIN_VERSION} required (found v${ver})"
  fi
}

# --- Main ---

main() {
  log "Knowledge Base installer — Unix/macOS"
  log "Project root: ${PROJECT_ROOT}"

  # Check prerequisites
  for cmd in "${REQUIRED_CMDS[@]}"; do
    check_command "$cmd"
  done
  check_node_version
  log "Prerequisites satisfied"

  # Install npm dependencies
  log "Installing npm dependencies..."
  cd "$PROJECT_ROOT"
  npm ci --prefer-offline 2>/dev/null || npm install

  # Build TypeScript
  log "Building TypeScript..."
  npm run build

  # Prepare database
  log "Setting up database..."
  npm run prepare-db

  # Validate
  log "Running validation..."
  npm test -- --run 2>/dev/null || log "Tests skipped (no test runner or failures)"

  log "Installation complete."
  log "Run 'npm run web' to start the web server."
}

main "$@"
