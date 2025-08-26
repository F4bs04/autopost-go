#!/usr/bin/env bash
set -euo pipefail
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
APP=${APP:-app:app}

# shellcheck disable=SC1091
if [[ -f ".venv/bin/activate" ]]; then
  source .venv/bin/activate
elif [[ -f ".venv/Scripts/activate" ]]; then
  source .venv/Scripts/activate
fi

echo "[start] Subindo FastAPI em http://${HOST}:${PORT}"
python -m uvicorn ${APP} --host ${HOST} --port ${PORT} --reload
