#!/usr/bin/env bash
set -euo pipefail

echo "[setup] Criando venv .venv (se não existir)"
python -m venv .venv || true

# shellcheck disable=SC1091
if [[ -f ".venv/bin/activate" ]]; then
  source .venv/bin/activate
elif [[ -f ".venv/Scripts/activate" ]]; then
  source .venv/Scripts/activate
fi

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install ruff pytest

if [[ ! -f ".env" && -f ".env.example" ]]; then
  cp .env.example .env
  echo "[setup] .env criado a partir de .env.example (edite as chaves)."
fi

echo "[setup] Concluído. Use: source .venv/bin/activate (Linux/macOS) ou .venv\\Scripts\\activate (Windows)"
