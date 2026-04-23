#!/usr/bin/env bash
set -euo pipefail

# DEPLOY_TO_GCP_NOW.sh — One-shot deployment to Google Cloud Platform
# Usage: ./DEPLOY_TO_GCP_NOW.sh [--project PROJECT_ID] [--region REGION]

PROJECT_ID="${1:-}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="my-knowledge-base"
IMAGE_TAG="$(git rev-parse --short HEAD 2>/dev/null || echo 'latest')"

# --- Argument parsing ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) PROJECT_ID="$2"; shift 2 ;;
    --region)  REGION="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: $0 [--project PROJECT_ID] [--region REGION]"
      echo ""
      echo "Deploys the knowledge base to GCP Cloud Run."
      echo "Requires: gcloud CLI authenticated, Docker installed."
      exit 0
      ;;
    *) shift ;;
  esac
done

if [[ -z "$PROJECT_ID" ]]; then
  PROJECT_ID="$(gcloud config get-value project 2>/dev/null || true)"
  if [[ -z "$PROJECT_ID" ]]; then
    echo "ERROR: No GCP project specified. Use --project or set gcloud default."
    exit 1
  fi
fi

echo "=== Deploying ${SERVICE_NAME} to GCP ==="
echo "  Project: ${PROJECT_ID}"
echo "  Region:  ${REGION}"
echo "  Tag:     ${IMAGE_TAG}"
echo ""

# Step 1: Build container image
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${IMAGE_TAG}"
echo "[1/4] Building container image..."
gcloud builds submit --tag "${IMAGE}" --project "${PROJECT_ID}" .

# Step 2: Deploy to Cloud Run
echo "[2/4] Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --port 3000

# Step 3: Get service URL
echo "[3/4] Retrieving service URL..."
SERVICE_URL="$(gcloud run services describe "${SERVICE_NAME}" \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --format 'value(status.url)')"

echo "[4/4] Deployment complete."
echo ""
echo "Service URL: ${SERVICE_URL}"
echo "Image:       ${IMAGE}"
