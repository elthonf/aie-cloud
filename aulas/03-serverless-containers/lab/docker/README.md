# Container code — Aula 3

Versão **FastAPI** da API de catálogo da QC, com mesma lógica de negócio da Function `v2-blob`, mas empacotada num **container Docker** para rodar no Azure Container Instances (ACI).

## Arquivos

| Arquivo | O que é |
|---------|---------|
| [app.py](app.py) | API FastAPI com endpoints `/health` e `/produtos` |
| [requirements.txt](requirements.txt) | Dependências (FastAPI + Uvicorn + azure-identity + azure-storage-blob) |
| [Dockerfile](Dockerfile) | Multi-stage build, imagem final leve (~150 MB) |

## Build & push (modo recomendado: server-side via ACR)

Pré-requisito: Terraform da Aula 3 já aplicado (Phase 1), com ACR provisionado.

```bash
ACR=$(cd ~/aie-cloud/aulas/03-serverless-containers/lab/terraform && terraform output -raw acr_name)

# Build da imagem no servidor do ACR (não usa quota do Cloud Shell)
cd ~/aie-cloud/aulas/03-serverless-containers/lab/docker
az acr build -t produtos-api:v1 -r "$ACR" .

# Confirmar
az acr repository list -n "$ACR" -o table
```

`az acr build` é **mais robusto** que `docker build` local no Cloud Shell (que pode esgotar quota de disco).

## Build & push (alternativa: docker local no Cloud Shell)

```bash
cd ~/aie-cloud/aulas/03-serverless-containers/lab/docker

# Build local
docker build -t produtos-api:v1 .

# Teste local (opcional — vai falhar em /produtos porque Cloud Shell não tem MI)
STORAGE_CATALOGO=$(cd ../terraform && terraform output -raw catalogo_storage_account_name)
docker run --rm -p 8080:8080 \
  -e STORAGE_ACCOUNT_CATALOGO="$STORAGE_CATALOGO" \
  produtos-api:v1 &
sleep 3
curl http://localhost:8080/health
docker stop $(docker ps -lq)

# Login no ACR e push
ACR=$(cd ../terraform && terraform output -raw acr_login_server)
ACR_NAME=$(cd ../terraform && terraform output -raw acr_name)
az acr login -n "$ACR_NAME"

docker tag produtos-api:v1 "$ACR/produtos-api:v1"
docker push "$ACR/produtos-api:v1"
```

## Depois do push, habilitar o ACI

```bash
cd ~/aie-cloud/aulas/03-serverless-containers/lab/terraform
terraform apply -auto-approve -var="aci_enabled=true"
```

## Testar o ACI

```bash
ACI_FQDN=$(cd ~/aie-cloud/aulas/03-serverless-containers/lab/terraform && terraform output -raw aci_fqdn)

sleep 60   # aguardar a MI propagar
curl "http://$ACI_FQDN:8080/health"
curl "http://$ACI_FQDN:8080/produtos?categoria=moveis"
```

> **Nota:** ACI não tem HTTPS built-in. Em produção, colocar Front Door, Application Gateway ou Azure Container Apps na frente (ou usar Container Apps direto, que tem TLS gerenciado).

## Comparação com a Function (mesma lógica, runtime diferente)

| Aspecto | Function v2-blob | ACI (este container) |
|---------|------------------|----------------------|
| URL | `https://<func>.azurewebsites.net/api/produtos` | `http://<aci>:8080/produtos` |
| TLS | ✅ Built-in | ❌ Não (manual) |
| Cold start | 1-3s | Não há (sempre on) |
| Custo idle | $0 | $$ pay-per-second mesmo idle |
| Auto-scale | ✅ 0-200 | ❌ 1 réplica fixa |
| Linguagem | Python/.NET/JS/Java | Qualquer |
| Identidade | System-assigned MI | User-assigned MI |
