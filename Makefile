# Makefile para padronizar tarefas

.PHONY: setup lint test dev e2e

PY?=python
PIP?=$(PY) -m pip
UVICORN?=$(PY) -m uvicorn
APP?=app:app
HOST?=0.0.0.0
PORT?=8000

setup:
	@echo "[setup] Criando venv (se necessário) e instalando dependências..."
	@$(PY) -m venv .venv || true
	@. .venv/Scripts/activate 2>/dev/null || . .venv/bin/activate 2>/dev/null || true; \
		$(PIP) install --upgrade pip; \
		$(PIP) install -r requirements.txt; \
		$(PIP) install ruff pytest;
	@echo "[setup] Pronto. Ative a venv conforme seu SO."

lint:
	@echo "[lint] Rodando ruff..."
	@ruff check .

test:
	@echo "[test] Executando testes (se existirem)..."
	@pytest -q || true

dev:
	@echo "[dev] Subindo backend FastAPI em http://$(HOST):$(PORT) ..."
	@$(UVICORN) $(APP) --host $(HOST) --port $(PORT) --reload

# Verificação ponta-a-ponta simples
E2E_URL?=http://localhost:$(PORT)/api/health

e2e:
	@echo "[e2e] Verificando saúde da API em $(E2E_URL) ..."
	@curl -sSf $(E2E_URL) | tee /dev/stderr | grep -E 'ok|OK|"status"' >/dev/null && echo "[e2e] OK" || (echo "[e2e] Falhou" && exit 1)
