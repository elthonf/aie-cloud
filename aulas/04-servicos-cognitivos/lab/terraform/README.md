# Terraform — Aula 4

Código IaC para provisionar a **camada cognitiva** da Quantum Commerce — totalmente autocontido, sem dependência das aulas anteriores:

- **Azure AI Services multi-service (S0)** — 1 endpoint para Speech, Language e Vision, com `custom_subdomain_name` habilitado (pré-requisito para Managed Identity).
- **Key Vault** — armazena a chave do AI Services; a Function lê via Key Vault reference sem expor a chave no código.
- **Storage Account** (`stdata04*`) — containers `audios` e `imagens` para os arquivos do lab.
- **MongoDB via ACI** — container group com `mongo:7.0` + `mongo-express:1.0.2`; Mongo Express disponível em `http://<IP>:8081`.
- **Function App** Python 3.11 (Consumption Y1) com Managed Identity SystemAssigned.
- **Roles** na Function: `Key Vault Secrets User` (lê o AI_KEY) + `Cognitive Services User` (Language e Vision) + `Storage Blob Data Contributor` (áudios e imagens).

## Como usar (no Azure Cloud Shell)

```bash
cd ~/qc-grupo-NN/aula04/terraform

terraform init
terraform apply -auto-approve
```

Tempo: ~5-8 min (ACI + AI Services demoram mais).

## Outputs principais

```bash
terraform output -raw function_app_hostname    # URL da Function
terraform output -raw mongodb_public_ip        # IP do MongoDB ACI
terraform output -raw mongo_express_url        # http://<IP>:8081
terraform output -raw data_storage_account_name
terraform output -raw key_vault_name
# (mongodb_connection_string é sensitive — use: terraform output mongodb_connection_string)
```

## Destroy

```bash
terraform destroy -auto-approve
```

Tempo: ~2-3 min. Todos os recursos da Aula 4 são destruídos. Nenhum recurso externo é afetado.

## Arquivos

| Arquivo | O que define |
|---------|--------------|
| [main.tf](main.tf) | Providers, RG, locals (tags + credenciais Mongo), data source de identidade |
| [variables.tf](variables.tf) | `location` (default: `eastus2`) |
| [outputs.tf](outputs.tf) | Todos os outputs consumidos pelo guia e pelos scripts |
| [cognitive.tf](cognitive.tf) | Azure AI Services multi-service (Speech, Language, Vision) |
| [keyvault.tf](keyvault.tf) | Key Vault + role para o usuário + segredo `ai-services-key` |
| [storage.tf](storage.tf) | Storage Account de dados + containers `audios` e `imagens` |
| [mongodb.tf](mongodb.tf) | Container Group ACI: MongoDB 7.0 + Mongo Express 1.0.2 |
| [function.tf](function.tf) | Storage da Function + App Service Plan + Function App + 3 role assignments |

## Observações

- **Custom subdomain:** sem ele, a Managed Identity não consegue autenticar no AI Services. Já está configurado em `cognitive.tf`.
- **Speech usa chave, não MI:** o endpoint de Speech STT exige a role `Cognitive Services Speech User` separada. Para simplificar, a aula usa a chave (armazenada no Key Vault, lida pela Function via KV reference no `AI_KEY` app setting).
- **ACI em vez de VM:** Azure for Students pode ter capacidade de SKU de VM esgotada na região. ACI não tem esse problema e inicializa em ~2 min.
- **Região:** `eastus2` padrão. Vision 4.0 `Caption` não está disponível em `eastus2` — o lab usa Tags + OCR + Objects.
- **Custo:** AI Services S0 é pay-per-call. Sem chamadas = sem custo. Function Consumption Y1 = grátis até 1M req/mês. ACI cobra por hora de execução (~$0,001/h para este size).
