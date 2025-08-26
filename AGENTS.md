# Guia para Agentes (AGENTS.md)

Este documento padroniza como trabalhar neste repositório.

## Onde trabalhar
- Backend FastAPI: `app.py` e utilitários em `src/` (ex.: `src/agente_ia.py`).
- Frontend estático: `frontend/` (`index.html`, `app.js`, `style.css`).
- Saídas geradas: `output/` (não commitar arquivos grandes).
- Configurações de deploy Railway: `railway.toml`, `DEPLOY_RAILWAY.md`.

## Como validar (checklist)
- `make setup` para preparar ambiente local.
- `make lint` deve passar (estilo e qualidade).
- `make test` deve passar (testes unitários, se existirem).
- `make dev` deve subir o backend e servir o frontend. Aponte o navegador para:
  - API: http://localhost:8000
  - Frontend: http://localhost:8000 (servido pelo FastAPI)
- `make e2e` executa uma verificação simples de saúde/endpoint.

## Padrões de código
- Python: seguir PEP 8. Use `ruff` para lint. Tipagem gradual com `typing` quando possível.
- JS: manter código simples (ES6+), sem frameworks. Evitar dependências desnecessárias.
- Logs e erros: mensagens claras em português. Não vaze chaves de API em logs.
- Commits: mensagens curtas e descritivas. Ex.: `feat(image): ...`, `fix(api): ...`.

## Convenções de API (resumo)
- Imagens OpenAI: `POST /api/regenerate-image` com `{"fonte":"openai"}`. Texto sobreposto deve estar em pt-BR.
- Imagens Pexels: `POST /api/generate-pexels-image`. Retorna `imagem`/`image`, `url` absoluto.
- Health: `GET /api/health`.

## O que NÃO mexer (sem alinhamento prévio)
- Estrutura e nomes dos endpoints públicos já integrados com clientes externos (ex.: `/api/generate-pexels-image`).
- Contratos de resposta consolidados (campos `imagem`, `image`, `url`, `success`).
- Arquivos de deploy (`railway.toml`, `Procfile`) sem combinar.

## Variáveis de ambiente (local)
- Copie `.env.example` para `.env` e preencha:
  - `OPENAI_API_KEY`
  - `PEXELS_API_KEY`

## Fluxo de desenvolvimento sugerido
1. `make setup`
2. `make dev`
3. Validar endpoints e UI.
4. `make lint && make test`
5. Commit + push.
