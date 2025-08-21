# 🤖 Agente de IA com Agno Framework

Este projeto implementa um agente de inteligência artificial usando o **Agno Framework**, combinando pesquisa na internet com geração de texto usando a API da OpenAI. O agente utiliza uma arquitetura multi-agente moderna para pesquisar informações sobre qualquer tema e gerar conteúdo estruturado com título, subtítulo e conteúdo detalhado.

## ⚡ Início Rápido

1. **Instalar dependências**:
```bash
pip install -r requirements.txt
```

2. **Configurar chave OpenAI** no arquivo `.env`:
```
OPENAI_API_KEY=sua_chave_aqui
```

3. **Executar**:
```bash
python main.py
```

## 📁 Estrutura do Projeto

```
├── src/                   # Código fonte
│   └── agente_ia.py      # Classe principal
├── examples/             # Exemplos de uso
├── tests/                # Testes unitários
├── docs/                 # Documentação completa
├── output/               # Arquivos gerados
└── main.py              # Script principal
```

## 📊 Exemplo de Saída

### JSON Estruturado (com Agno)
```json
{
  "tema": "Blockchain",
  "data_geracao": "2025-07-28T12:00:00",
  "conteudo": {
    "titulo": "Blockchain: Revolução Digital",
    "subtitulo": "Tecnologia que Transforma o Futuro",
    "conteudo": "Texto detalhado sobre blockchain...",
    "fontes": [
      {
        "titulo": "Notícia sobre Blockchain - G1",
        "link": "https://g1.globo.com/...",
        "resumo": "Resumo da notícia..."
      }
    ]
  },
  "workflow_version": "agno-1.0"
}
```

## 🚀 Funcionalidades

- **Framework Agno**: Arquitetura multi-agente moderna e otimizada
- **Performance Superior**: 10.000x mais rápido que frameworks tradicionais
- **Pesquisa Inteligente**: Busca automática na web usando DuckDuckGo
- **Foco em Notícias**: Prioriza sites de notícias confiáveis (G1, Folha, UOL, etc.)
- **Geração com IA**: Usa OpenAI GPT-3.5-turbo para criar conteúdo estruturado
- **Saída Dupla**: Salva primeiro em JSON e depois converte para Markdown
- **Fontes Incluídas**: Sempre inclui links e resumos das fontes consultadas
- **Sistema Robusto**: Fallback automático se a pesquisa falhar
- **Extensibilidade**: Preparado para múltiplos agentes e workflows

## 📖 Uso Básico

```python
from src.agente_ia import AgenteIA

agente = AgenteIA()
resultado = agente.processar_tema("blockchain")
print(resultado)
```

## 🧪 Executar Testes

```bash
python tests/test_agente_ia.py
```

## 📚 Documentação Completa

Veja [docs/README.md](docs/README.md) para documentação detalhada.

## 📦 Dependências

```txt
openai>=1.12.0          # API OpenAI
requests>=2.31.0        # HTTP requests
beautifulsoup4>=4.12.2  # HTML parsing
python-dotenv>=1.0.0    # Variáveis ambiente
agno>=1.7.0            # Framework principal
pydantic>=2.11.0       # Validação dados
typer>=0.16.0          # CLI interface
rich>=14.0.0           # Output formatado
```

---

**Desenvolvido com IA** | **Pronto para produção** | **Totalmente testado**
