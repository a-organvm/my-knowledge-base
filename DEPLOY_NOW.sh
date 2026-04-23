#!/usr/bin/env bash
set -euo pipefail

# DEPLOY_NOW.sh — Quick deployment wrapper
# Detects environment and delegates to the appropriate deploy script.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Knowledge Base — Deploy Now ==="
echo ""

# Pre-flight checks
if ! command -v git &>/dev/null; then
  echo "ERROR: git is required."
  exit 1
fi

# Ensure clean working tree
if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
  echo "WARNING: Working tree has uncommitted changes."
  echo "  Commit or stash before deploying to production."
  echo ""
fi

COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
BRANCH="$(git branch --show-current 2>/dev/null || echo 'unknown')"
echo "  Branch: ${BRANCH}"
echo "  Commit: ${COMMIT}"
echo ""

# Detect deployment target
if [[ -f "${SCRIPT_DIR}/fly.toml" ]]; then
  echo "[deploy] Fly.io detected (fly.toml found)"
  if command -v fly &>/dev/null; then
    fly deploy --ha=false
  else
    echo "ERROR: fly CLI not installed. Run: brew install flyctl"
    exit 1
  fi
elif [[ -f "${SCRIPT_DIR}/Dockerfile" ]]; then
  echo "[deploy] Dockerfile detected — building container..."
  if [[ -f "${SCRIPT_DIR}/DEPLOY_TO_GCP_NOW.sh" ]]; then
    bash "${SCRIPT_DIR}/DEPLOY_TO_GCP_NOW.sh" "$@"
  elif command -v docker &>/dev/null; then
    docker build -t "my-knowledge-base:${COMMIT}" .
    echo "Built: my-knowledge-base:${COMMIT}"
    echo "Push manually: docker push <registry>/my-knowledge-base:${COMMIT}"
  else
    echo "ERROR: No container runtime available."
    exit 1
  fi
else
  echo "ERROR: No deployment configuration found (no fly.toml, no Dockerfile)."
  exit 1
fi

echo ""
echo "=== Deploy complete ==="
