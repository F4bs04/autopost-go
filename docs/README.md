# Agente de IA - Gerador de Conteúdo

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-green.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Um agente de IA inteligente que realiza pesquisas na internet e gera textos estruturados usando a API da OpenAI.

## 🚀 Funcionalidades

- **🔍 Pesquisa Inteligente**: Busca informações na internet via DuckDuckGo
- **🤖 Geração de Texto IA**: Usa GPT-3.5-turbo para criar conteúdo estruturado
- **📄 Saída Estruturada**: Gera textos com Título, Subtítulo e Conteúdo
- **🔄 Fallback Automático**: Usa dados simulados se a pesquisa online falhar
- **💾 Salvamento Automático**: Salva resultados em arquivos organizados
- **🧪 Testável**: Inclui suite de testes unitários

## 📁 Estrutura do Projeto

```
agente-ia/
├── src/                    # Código fonte principal
│   ├── __init__.py
│   └── agente_ia.py       # Classe principal do agente
├── examples/              # Exemplos de uso
│   ├── exemplo_basico.py
│   └── exemplo_multiplos_temas.py
├── tests/                 # Testes unitários
│   └── test_agente_ia.py
├── docs/                  # Documentação
│   └── README.md
├── output/                # Arquivos de saída gerados
├── requirements.txt       # Dependências
├── .env                   # Configurações (chave API)
└── main.py               # Script principal
```

## 🛠️ Instalação

1. **Clone o projeto**:
```bash
git clone <url-do-repositorio>
cd agente-ia
```

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Configure a chave da OpenAI**:
   - Edite o arquivo `.env`
   - Adicione sua chave: `OPENAI_API_KEY=sua_chave_aqui`

## 📖 Como Usar

### Uso Básico

```python
from src.agente_ia import AgenteIA

# Criar instância do agente
agente = AgenteIA()

# Processar um tema
resultado = agente.processar_tema("inteligência artificial")

if resultado:
    print(resultado)
```

### Execução Interativa

```bash
python main.py
```

### Executar Exemplos

```bash
# Exemplo básico
python examples/exemplo_basico.py

# Múltiplos temas
python examples/exemplo_multiplos_temas.py
```

### Executar Testes

```bash
python tests/test_agente_ia.py
```

## 🔧 API Reference

### Classe `AgenteIA`

#### `__init__(api_key=None)`
Inicializa o agente com a chave da OpenAI.

#### `processar_tema(tema, salvar_arquivo=True, pasta_output="output")`
Processa um tema completo: pesquisa + geração de texto.

**Parâmetros:**
- `tema` (str): Tema para processar
- `salvar_arquivo` (bool): Se deve salvar em arquivo
- `pasta_output` (str): Pasta de destino

**Retorna:**
- `str`: Texto gerado ou `None` em caso de erro

#### `pesquisar_tema(tema, num_resultados=5)`
Pesquisa informações sobre um tema.

#### `gerar_texto_estruturado(tema, informacoes_pesquisa)`
Gera texto estruturado usando OpenAI.

## 📊 Exemplo de Saída

```
TÍTULO: Inteligência Artificial: A Revolução Tecnológica do Século XXI
SUBTÍTULO: Como a IA está transformando nossa sociedade e moldando o futuro
CONTEÚDO: A inteligência artificial representa uma das mais significativas 
revoluções tecnológicas da nossa era...
```

## 🧪 Testes

O projeto inclui testes unitários abrangentes:

- Testes de inicialização
- Testes de pesquisa web
- Testes de geração de dados simulados
- Testes de tratamento de erros

Execute com: `python tests/test_agente_ia.py`

## 📋 Dependências

- `openai>=1.12.0` - API da OpenAI
- `requests>=2.31.0` - Requisições HTTP
- `beautifulsoup4>=4.12.2` - Parsing HTML
- `python-dotenv>=1.0.0` - Variáveis de ambiente

## 🔒 Segurança

- A chave da API é carregada de variáveis de ambiente
- Não hardcode credenciais no código
- Use o arquivo `.env` para configurações locais

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 🆘 Suporte

Se encontrar problemas:

1. Verifique se a chave da OpenAI está configurada
2. Confirme que as dependências estão instaladas
3. Execute os testes para validar o ambiente
4. Consulte os exemplos para uso correto

## 🔄 Changelog

### v1.0.0
- Implementação inicial
- Pesquisa via DuckDuckGo
- Geração de texto com OpenAI
- Sistema de fallback
- Testes unitários
- Documentação completa
