# Terraform — Aula 3

Código IaC para provisionar a **camada de compute** da Quantum Commerce:

- Storage Account de catálogo **criado nesta aula** + upload automático do `produtos.csv`
- Azure Function App em **Flex Consumption** (plano FC1, sucessor do Linux Consumption/Y1, com Managed Identity SystemAssigned)
- Azure Container Registry (Basic SKU)
- Managed Identity user-assigned para o ACI
- Role assignments para ler blobs do Storage do catálogo (sem credenciais no código)
- Azure Container Instances (habilitado via flag `aci_enabled` após push da imagem)

> **Independente da Aula 2.** Não é preciso aplicar nada da Aula 2 nem passar
> variáveis de storage — esta aula cria o próprio catálogo e sobe o CSV no apply.

## Como usar (no Azure Cloud Shell)

### Phase 1 — Provisionar tudo exceto ACI (~3 min)

```bash
cd ~/aie-cloud/aulas/03-serverless-containers/lab/terraform

terraform init
terraform apply -auto-approve
# aci_enabled fica em false (default) → não cria ACI ainda
```

Provisiona: Resource Group + Storage de catálogo (com produtos.csv) + Function App + ACR + UAI + role assignments.

### Phase 2 — Após importar a imagem no ACR, habilitar o ACI

```bash
# (depois do 'az acr import' da imagem produtos-api:v1 do GHCR — ver docker/README)
terraform apply -auto-approve -var="aci_enabled=true"
```

### Destroy (regra de ouro — custo zero ao final)

```bash
terraform destroy -auto-approve -var="aci_enabled=true"
```

> Tudo é removido, inclusive o Storage do catálogo (ele é desta aula).

## Arquivos

| Arquivo | O que define |
|---------|--------------|
| [main.tf](main.tf) | Providers (azurerm 4.x), RG, sufixo aleatório, locals, Flex Consumption Plan FC1 |
| [storage.tf](storage.tf) | Storage da Function + Storage do catálogo + container + upload do produtos.csv |
| [variables.tf](variables.tf) | `location`, `aci_enabled` |
| [outputs.tf](outputs.tf) | `function_app_name`, `function_app_default_hostname`, `acr_login_server`, `acr_name`, `aci_fqdn`, `catalogo_storage_account_name` |
| [function.tf](function.tf) | Function App + Managed Identity + role Blob Data Reader |
| [containers.tf](containers.tf) | ACR + UAI + role + ACI (count condicional) |

## Outputs disponíveis

```bash
terraform output -raw function_app_name
terraform output -raw function_app_default_hostname
terraform output -raw acr_login_server
terraform output -raw acr_name
terraform output -raw aci_fqdn   # só faz sentido com aci_enabled=true
```
