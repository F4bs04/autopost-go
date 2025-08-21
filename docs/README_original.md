# Agente de IA - Gerador de Conteúdo

Este projeto implementa um agente de IA em Python que realiza pesquisas na internet e gera textos estruturados usando a API da OpenAI.

## Funcionalidades

- 🔍 **Pesquisa na Internet**: Realiza buscas no Google sobre qualquer tema
- 🤖 **Geração de Texto com IA**: Usa GPT-3.5-turbo para criar conteúdo estruturado
- 📄 **Saída Estruturada**: Gera textos com Título, Subtítulo e Conteúdo
- 💾 **Salvamento Automático**: Salva os resultados em arquivos de texto

## Instalação

1. Clone ou baixe este projeto
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure sua chave da OpenAI no arquivo `.env` (já configurado)

## Como Usar

Execute o programa principal:
```bash
python agente_ia.py
```

O programa irá:
1. Solicitar um tema para pesquisa
2. Realizar buscas na internet sobre o tema
3. Extrair informações relevantes
4. Gerar um texto estruturado usando IA
5. Exibir o resultado e salvar em arquivo

## Exemplo de Uso

```
📝 Digite o tema: inteligência artificial

🔍 Pesquisando sobre: inteligência artificial
✅ Encontrados 5 resultados
📄 Extraindo conteúdo da página 1...
📄 Extraindo conteúdo da página 2...
📄 Extraindo conteúdo da página 3...
🤖 Gerando texto estruturado...
✅ Texto gerado com sucesso!

📄 RESULTADO FINAL:
TÍTULO: Inteligência Artificial: A Revolução Tecnológica do Século XXI
SUBTÍTULO: Como a IA está transformando nossa sociedade e moldando o futuro
CONTEÚDO: [texto gerado pela IA...]
```

## Estrutura do Projeto

- `agente_ia.py` - Código principal do agente
- `requirements.txt` - Dependências do projeto
- `.env` - Configurações (chave da API)
- `README.md` - Este arquivo

## Dependências

- `openai` - Para integração com GPT-3.5-turbo
- `requests` - Para requisições HTTP
- `beautifulsoup4` - Para parsing de HTML
- `python-dotenv` - Para carregar variáveis de ambiente

## Recursos do Agente

### Classe AgenteIA

- `pesquisar_google()` - Realiza pesquisas no Google
- `extrair_conteudo_pagina()` - Extrai texto de páginas web
- `gerar_texto_estruturado()` - Gera conteúdo usando OpenAI
- `processar_tema()` - Processo completo de pesquisa e geração

## Notas Importantes

- O agente respeita limites de requisições para não sobrecarregar servidores
- Os resultados são salvos automaticamente em arquivos `.txt`
- O programa pode ser encerrado digitando 'sair'
- A chave da OpenAI já está configurada no arquivo `.env`

## Exemplo de Saída

O agente gera textos no formato:

```
TÍTULO: [Título atrativo sobre o tema]
SUBTÍTULO: [Subtítulo complementar]
CONTEÚDO: [Texto informativo de pelo menos 300 palavras baseado nas pesquisas realizadas]
```
