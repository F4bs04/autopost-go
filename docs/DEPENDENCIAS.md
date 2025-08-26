# Atualização de Dependências

Este projeto usa [`pip-tools`](https://pip-tools.readthedocs.io/) para travar versões das bibliotecas.

- As dependências diretas ficam em `requirements.txt`.
- O arquivo `requirements.lock` é gerado automaticamente e inclui todas as dependências (diretas e transitivas).

## Como atualizar

1. Instale o `pip-tools` (uma vez por ambiente):
   ```bash
   pip install pip-tools
   ```
2. Ajuste as versões desejadas em `requirements.txt`.
3. Gere o arquivo de lock:
   ```bash
   pip-compile --output-file=requirements.lock requirements.txt
   ```
4. Sincronize ou instale o ambiente com as versões travadas:
   ```bash
   pip install -r requirements.lock
   # ou
   pip-sync requirements.lock
   ```
5. Faça commit de `requirements.txt` e `requirements.lock`.

Manter o lock file atualizado garante builds reprodutíveis.
