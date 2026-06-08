# Scripts Python — Aula 2

Scripts que populam e exploram as bases provisionadas pelo Terraform da Aula 2.

| Script | Atividade | O que faz |
|--------|-----------|-----------|
| [popular_produtos.py](popular_produtos.py) | L₂ | Lê CSV do Blob, lê connection string do Key Vault, cria e popula `T_PRODUTOS` no Azure SQL |
| [popular_reviews.py](popular_reviews.py) | L₃-A | Insere 30 reviews fictícias no Cosmos DB (particionado por `produto_id`) |
| [indexar_produtos.py](indexar_produtos.py) | L₃-B | Cria índice no Azure AI Search com semantic ranking e indexa os produtos |

## Pré-requisitos

- Terraform da Aula 2 já aplicado (`cd ../terraform && terraform apply ...`)
- CSV de produtos enviado ao Blob (ver Atividade 1 do [guia-lab.md](../guia-lab.md))
- Permissões data plane no Cosmos (concedidas via `az cosmosdb sql role assignment` — ver guia)

## Instalação das dependências

No Cloud Shell (instala em `~/.local`, sem mexer na máquina do aluno):

```bash
pip install --user pyodbc azure-identity azure-keyvault-secrets \
                    azure-storage-blob azure-cosmos azure-search-documents
```

## Variáveis de ambiente esperadas

Cada script lê o que precisa do ambiente. O guia-lab mostra como exportá-las a partir dos outputs do Terraform.

| Script | Variáveis necessárias |
|--------|------------------------|
| `popular_produtos.py` | `KEY_VAULT_NAME`, `STORAGE_ACCOUNT_NAME` |
| `popular_reviews.py` | `COSMOS_ENDPOINT`, `KEY_VAULT_NAME` |
| `indexar_produtos.py` | `SEARCH_ENDPOINT`, `STORAGE_ACCOUNT_NAME` |

Atalho para exportar todas:

```bash
cd ~/aie-cloud/aulas/02-storage-bancos/lab/terraform
export KEY_VAULT_NAME=$(terraform output -raw key_vault_name)
export STORAGE_ACCOUNT_NAME=$(terraform output -raw storage_account_name)
export COSMOS_ENDPOINT=$(terraform output -raw cosmos_endpoint)
export SEARCH_ENDPOINT=$(terraform output -raw search_endpoint)
```

## Como executar

```bash
cd ~/aie-cloud/aulas/02-storage-bancos/lab/scripts
python3 popular_produtos.py
python3 popular_reviews.py
python3 indexar_produtos.py
```

## Autenticação

Os scripts usam **`DefaultAzureCredential`** da `azure-identity` para Key Vault, Blob e AI Search — sem chaves hardcoded; a identidade do Cloud Shell é detectada automaticamente.

**Exceção — Cosmos DB:** o Cloud Shell **não** consegue emitir token AAD para a audience de data-plane do Cosmos (`AudienceNotSupported`). Por isso o `popular_reviews.py` autentica no Cosmos com a **key**, lida do **Key Vault** (mesmo padrão de "segredo no Vault" do SQL). Continua sem hardcode.

> **Lição:** em produção, uma **Function/Container com Managed Identity** consegue token AAD para o Cosmos e usaria `DefaultAzureCredential` direto (graças à role data-plane do Terraform). A limitação é só do Cloud Shell.
