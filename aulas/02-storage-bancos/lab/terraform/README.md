# Terraform — Aula 2

Código IaC pronto para provisionar **toda a camada de dados** da Quantum Commerce:

- Storage Account + 3 containers (catálogo, imagens, logs) + lifecycle policy
- Azure SQL Database (GP Serverless, auto-pause)
- Key Vault com a connection string do SQL como segredo
- Cosmos DB (Serverless)
- Azure AI Search (SKU Free)

## Como usar (no Azure Cloud Shell)

```bash
# Ir para a pasta
cd ~/aie-cloud/aulas/02-storage-bancos/lab/terraform

# Gerar uma senha forte para o admin do SQL (não use senha trivial)
SQL_PASSWORD=$(openssl rand -base64 24)
echo "Senha gerada (guarde em local seguro): $SQL_PASSWORD"

# Inicializar providers
terraform init

# Ver o plano
terraform plan -var="sql_admin_password=$SQL_PASSWORD"

# Aplicar (provisiona TUDO de uma vez — ~8 min)
terraform apply -auto-approve -var="sql_admin_password=$SQL_PASSWORD"

# ... usar os recursos durante o lab ...

# Destruir tudo ao final (regra de ouro — custo zero)
terraform destroy -auto-approve -var="sql_admin_password=$SQL_PASSWORD"
```

## Arquivos

| Arquivo | O que define |
|---------|--------------|
| [main.tf](main.tf) | Providers, sufixo aleatório, Resource Group, locals |
| [variables.tf](variables.tf) | `location` e `sql_admin_password` |
| [outputs.tf](outputs.tf) | Nomes e endpoints consumidos pelos scripts Python |
| [storage.tf](storage.tf) | Storage Account + 3 containers + lifecycle |
| [sql.tf](sql.tf) | SQL Server + Database (GP Serverless, auto-pause) + firewall rules |
| [keyvault.tf](keyvault.tf) | Key Vault + RBAC + segredo da connection string |
| [cosmos.tf](cosmos.tf) | Cosmos DB Account (Serverless) + DB + container `reviews` |
| [search.tf](search.tf) | AI Search service (SKU Free) + 2 role assignments |

## Outputs disponíveis após `apply`

Pegue valores específicos com `terraform output -raw <nome>`:

```bash
terraform output -raw storage_account_name
terraform output -raw key_vault_name
terraform output -raw cosmos_endpoint
terraform output -raw search_endpoint
```

Os scripts Python em [../scripts/](../scripts/) consomem esses outputs via variáveis de ambiente.

## Observações

- **Região:** default `centralus`. Em contas Azure for Students o Azure SQL costuma ficar `ProvisioningDisabled` em eastus2; `centralus` é permitido pela política e provisiona SQL. Sobrescreva com `-var="location=<regiao>"` se necessário.
- **Cosmos serverless (sem free-tier):** evita o limite de "1 conta free-tier por assinatura". Serverless cobra por operação — custo do lab ≈ centavos. Para ligar o free-tier: `-var="cosmos_free_tier=true"`.
- **AI Search SKU Free:** permite **apenas 1 instância free por assinatura**. Se faltar capacidade na região, tente outra região permitida.
- **Auto-pausa do SQL:** o banco serverless entra em standby após 60 min sem uso. A primeira query depois disso pode levar ~30s.
- **Custo:** serverless + auto-pause + SKUs free deixam o lab em ~$0 enquanto rodando. Não esqueça do `destroy` no final.
- **Senha do SQL:** sempre gere com `openssl rand -base64 24`. Nunca commite a senha. O Terraform usa `var.sql_admin_password` via `-var=`.
