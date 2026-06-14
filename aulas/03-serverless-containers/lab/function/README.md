# Function code — Aula 3

Duas versões da API HTTP de catálogo da QC, em Python (programming model v2 do Azure Functions):

| Pasta | Quando | Características |
|-------|--------|-----------------|
| [v1-mock/](v1-mock/) | L₁ | 5 produtos hardcoded no código. Sem dependências externas. Bom para validar que o deploy funciona. |
| [v2-blob/](v2-blob/) | L₂ | Lê os 20 produtos reais do **Blob Storage do catálogo** (criado nesta aula) via **Managed Identity** — **sem credenciais no código**. |

Cada pasta é **self-contained** (`function_app.py` + `host.json` + `requirements.txt`), pronta para `func azure functionapp publish` de dentro dela.

## Como fazer deploy

Pré-requisito: Terraform da Aula 3 já aplicado (Phase 1 — provisiona a Function App e o Storage de catálogo). Sem dependência da Aula 2 (ver [../terraform/README.md](../terraform/README.md)).

```bash
# Pegar o nome da Function App
FUNC_NAME=$(cd ~/aie-cloud/aulas/03-serverless-containers/lab/terraform && terraform output -raw function_app_name)
echo "Function: $FUNC_NAME"

# Deploy da v1 (mock)
cd ~/aie-cloud/aulas/03-serverless-containers/lab/function/v1-mock
func azure functionapp publish "$FUNC_NAME" --python

# Depois, deploy da v2 (Blob + MI)
cd ~/aie-cloud/aulas/03-serverless-containers/lab/function/v2-blob
func azure functionapp publish "$FUNC_NAME" --python
```

Cada `publish` substitui o código no Function App.

## Como testar

```bash
HOSTNAME=$(cd ~/aie-cloud/aulas/03-serverless-containers/lab/terraform && terraform output -raw function_app_default_hostname)

curl -s "$HOSTNAME/api/health" | python3 -m json.tool
curl -s "$HOSTNAME/api/produtos?categoria=moveis" | python3 -m json.tool
curl -s "$HOSTNAME/api/produtos?nome=cadeira" | python3 -m json.tool
```

> **Cold start:** a primeira chamada após inatividade leva 1-3s. Chamadas seguintes são milissegundos.

## Lição central

Comparar a v1 com a v2: a v2 **lê do Blob via Managed Identity** e em nenhum momento aparece chave, senha, connection string ou secret no código. Isso é o padrão a ser usado por todos os componentes que os agentes da QC vão consumir.
