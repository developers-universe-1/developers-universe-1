#!/usr/bin/env bash
# Deploy the RAG agent to Cloud Run.
# Prereqs: gcloud authenticated, APIs enabled, Cloud SQL instance + Secret Manager
# secret for DB password already created (see README).
set -euo pipefail

PROJECT_ID="${GCP_PROJECT:?set GCP_PROJECT}"
REGION="${GCP_REGION:-us-central1}"
SERVICE="vertex-ai-rag-agent"
SQL_INSTANCE="${SQL_INSTANCE:?set SQL_INSTANCE (e.g. my-project:us-central1:rag-pg)}"
DB_NAME="${DB_NAME:-rag}"
DB_USER="${DB_USER:-rag_app}"
DB_PASSWORD_SECRET="${DB_PASSWORD_SECRET:-rag-db-password}"  # Secret Manager name

# Build and push the container image.
gcloud builds submit --tag "gcr.io/${PROJECT_ID}/${SERVICE}" --project "${PROJECT_ID}"

# Deploy to Cloud Run:
#  - --add-cloudsql-instances mounts the Cloud SQL Auth Proxy as a sidecar so the
#    app connects over localhost with IAM-level transport security.
#  - --set-secrets injects the DB password from Secret Manager (never in env files).
#  - max-instances caps spend; concurrency 40 matches a small pg pool per instance.
gcloud run deploy "${SERVICE}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --image "gcr.io/${PROJECT_ID}/${SERVICE}" \
  --add-cloudsql-instances "${SQL_INSTANCE}" \
  --set-env-vars "GCP_PROJECT=${PROJECT_ID},GCP_REGION=${REGION},DB_HOST=127.0.0.1,DB_NAME=${DB_NAME},DB_USER=${DB_USER}" \
  --set-secrets "DB_PASSWORD=${DB_PASSWORD_SECRET}:latest" \
  --min-instances 0 \
  --max-instances 10 \
  --concurrency 40 \
  --memory 1Gi \
  --timeout 60 \
  --allow-unauthenticated

gcloud run services describe "${SERVICE}" \
  --project "${PROJECT_ID}" --region "${REGION}" \
  --format 'value(status.url)'
