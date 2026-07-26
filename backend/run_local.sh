#!/usr/bin/env bash
# Start FastAPI, Celery worker, and Flower for local development.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PIDS=()

cleanup() {
  echo
  echo "Stopping local services..."
  for pid in "${PIDS[@]:-}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
  wait 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "Starting FastAPI (http://127.0.0.1:8000)..."
uv run fastapi dev app/main.py &
PIDS+=($!)

echo "Starting Celery worker..."
uv run celery -A app.core.celery_app.celery_app worker -l info &
PIDS+=($!)

echo "Starting Flower (http://127.0.0.1:5555)..."
uv run celery -A app.core.celery_app.celery_app flower &
PIDS+=($!)

echo
echo "Local stack is up. Press Ctrl+C to stop all services."
wait
