#!/usr/bin/env bash
# Activate the GCP service account (mounted key) once, then run the container command.
set -e
if [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
  gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS" >/dev/null 2>&1 || echo "WARN: SA activate failed"
  gcloud config set project lithe-record-440915-m9 >/dev/null 2>&1 || true
else
  echo "WARN: no service-account key at $GOOGLE_APPLICATION_CREDENTIALS — bq will fail."
fi
exec "$@"
