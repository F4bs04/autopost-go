# 🚀 Deploy no Railway

## Pré-requisitos

1. **Conta no Railway**: Crie uma conta em [railway.app](https://railway.app)
2. **Chave OpenAI**: Obtenha sua chave em [platform.openai.com](https://platform.openai.com/api-keys)

## 📋 Passos para Deploy

### 1. Conectar Repositório
- Acesse [railway.app](https://railway.app)
- Clique em "New Project"
- Selecione "Deploy from GitHub repo"
- Conecte este repositório

### 2. Configurar Variáveis de Ambiente
No painel do Railway, vá em **Variables** e adicione:

```
OPENAI_API_KEY=sua_chave_openai_aqui
```

**Variáveis opcionais:**
```
IMAGE_MODEL=gpt-image-1
IMAGE_SIZE=1536x1024
```

### 3. Deploy Automático
O Railway detectará automaticamente:
- ✅ `requirements.txt` - Dependências Python
- ✅ `Procfile` - Comando de inicialização
- ✅ `runtime.txt` - Versão do Python
- ✅ `railway.toml` - Configurações específicas

## 🔧 Arquivos de Configuração

### `Procfile`
```
web: python start.py
```

### `start.py`
```python
#!/usr/bin/env python3
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, log_level="info")
```

### `railway.toml`
```toml
[build]
builder = "nixpacks"

[deploy]
healthcheckPath = "/api/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
```

## 🚨 Possíveis Problemas e Soluções

### 1. Erro de Chave API
**Sintoma:** Erro 500 ao gerar conteúdo/imagem
**Solução:** 
- Verifique se `OPENAI_API_KEY` está configurada corretamente
- Confirme que a chave tem créditos disponíveis
- Teste a chave localmente primeiro

### 2. Timeout na Geração
**Sintoma:** Requests demoram muito ou falham
**Solução:**
- Aumente o `healthcheckTimeout` no `railway.toml`
- Verifique se o modelo `gpt-image-1` está disponível

### 3. Erro de Build
**Sintoma:** Deploy falha durante a instalação
**Solução:**
- Verifique se todas as dependências em `requirements.txt` são válidas
- Confirme a versão do Python em `runtime.txt`

## 📊 Endpoints Disponíveis

Após o deploy, sua aplicação terá:

- `GET /` - Interface web
- `POST /api/generate` - Gerar conteúdo completo
- `POST /api/regenerate-text` - Apenas texto
- `POST /api/regenerate-image` - Apenas imagem  
- `GET /api/health` - Health check
- `GET /docs` - Documentação da API

## 🔍 Monitoramento

- **Logs**: Acesse via painel do Railway
- **Health Check**: Automático via `/api/health`
- **Métricas**: Disponíveis no dashboard do Railway

## 💡 Dicas

1. **Teste Local Primeiro**: Execute `uvicorn app:app --reload` antes do deploy
2. **Monitore Créditos**: Acompanhe o uso da API OpenAI
3. **Backup de Configuração**: Mantenha as variáveis de ambiente documentadas
