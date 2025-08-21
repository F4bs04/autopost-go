# Clio Agent API - Documentação

API para geração de conteúdo e imagens usando IA.

## Base URL
```
http://127.0.0.1:8000
```

## Endpoints

### 1. Health Check
**GET** `/api/health`

Verifica o status da API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-21T19:04:34.123456",
  "version": "1.0.0",
  "endpoints": [
    "/api/generate",
    "/api/regenerate-text",
    "/api/regenerate-image",
    "/api/health",
    "/docs"
  ]
}
```

### 2. Gerar Conteúdo Completo
**POST** `/api/generate`

Gera conteúdo estruturado e imagem sobre um tema.

**Request Body:**
```json
{
  "tema": "inteligência artificial",
  "gerar_imagem": true,
  "estilo_imagem": "realista"
}
```

**Parâmetros:**
- `tema` (string, obrigatório): Tema para pesquisa e geração
- `gerar_imagem` (boolean, opcional): Se deve gerar imagem (default: true)
- `estilo_imagem` (string, opcional): Estilo da imagem - "realista", "ilustracao", "abstrato", "criativo" (default: "realista")

**Response:**
```json
{
  "tema": "inteligência artificial",
  "data_geracao": "2025-08-21T19:04:34.123456",
  "conteudo": {
    "titulo": "O Futuro da Inteligência Artificial",
    "subtitulo": "Como a IA está transformando o mundo",
    "conteudo": "Texto detalhado sobre o tema...",
    "fontes": [
      {
        "titulo": "Artigo sobre IA",
        "link": "https://exemplo.com/artigo",
        "resumo": "Resumo do artigo..."
      }
    ],
    "imagem": {
      "url": null,
      "local_path": "output/O_Futuro_da_Inteligencia_Artificial_image.jpg",
      "public_url": "/output/O_Futuro_da_Inteligencia_Artificial_image.jpg",
      "prompt_usado": "Prompt usado para gerar a imagem...",
      "modelo": "gpt-image-1",
      "tamanho": "1536x1024",
      "data_geracao": "2025-08-21T19:04:34.123456"
    }
  },
  "workflow_version": "agno-1.0"
}
```

### 3. Regenerar Apenas Texto
**POST** `/api/regenerate-text`

Regenera apenas o conteúdo textual (sem imagem).

**Request Body:**
```json
{
  "tema": "blockchain"
}
```

**Response:**
```json
{
  "conteudo": {
    "titulo": "Blockchain: A Revolução Digital",
    "subtitulo": "Entendendo a tecnologia por trás das criptomoedas",
    "conteudo": "Texto detalhado sobre blockchain...",
    "fontes": [...]
  }
}
```

### 4. Regenerar Apenas Imagem
**POST** `/api/regenerate-image`

Regenera apenas a imagem baseada em um título.

**Request Body:**
```json
{
  "titulo": "O Futuro da Inteligência Artificial",
  "tema": "tecnologia",
  "estilo_imagem": "criativo"
}
```

**Response:**
```json
{
  "imagem": {
    "url": null,
    "local_path": "output/O_Futuro_da_Inteligencia_Artificial_image.jpg",
    "public_url": "/output/O_Futuro_da_Inteligencia_Artificial_image.jpg",
    "prompt_usado": "Prompt usado...",
    "modelo": "gpt-image-1",
    "tamanho": "1536x1024",
    "data_geracao": "2025-08-21T19:04:34.123456"
  }
}
```

## Estilos de Imagem Disponíveis

- **realista**: Fotorrealista, alta qualidade, bem iluminado, composição profissional
- **ilustracao**: Ilustração digital, arte conceitual, estilo cartoon, colorido
- **abstrato**: Arte abstrata, formas geométricas, cores vibrantes, minimalista
- **criativo**: Arte criativa, imaginativo, surreal, único, experimental

## Arquivos Estáticos

As imagens geradas ficam disponíveis em:
```
GET /output/{filename}
```

## Documentação Interativa

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## Códigos de Status

- `200`: Sucesso
- `422`: Erro de validação (dados inválidos)
- `500`: Erro interno do servidor

## Exemplo de Uso com JavaScript

```javascript
// Gerar conteúdo completo
const response = await fetch('http://127.0.0.1:8000/api/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    tema: 'inteligência artificial',
    gerar_imagem: true,
    estilo_imagem: 'realista'
  })
});

const data = await response.json();
console.log(data);
```

## Exemplo de Uso com cURL

```bash
# Health check
curl -X GET "http://127.0.0.1:8000/api/health"

# Gerar conteúdo
curl -X POST "http://127.0.0.1:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "tema": "inteligência artificial",
    "gerar_imagem": true,
    "estilo_imagem": "realista"
  }'
```

## Configuração CORS

A API está configurada para aceitar requisições de qualquer origem (`*`). Em produção, configure domínios específicos para maior segurança.

## Requisitos

- Python 3.11+
- OpenAI API Key configurada no arquivo `.env`
- Dependências instaladas via `requirements.txt`
