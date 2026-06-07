# Guia de Laboratório — Aula 2

**Tema:** Storage & Bancos de Dados na Nuvem
**Plataforma:** Microsoft Azure (Azure for Students)
**Ambiente:** **Azure Cloud Shell** — tudo no browser, sem instalar nada localmente

---

## Visão geral do lab

Este lab é intercalado com a teoria. Cada atividade corresponde a um momento do cronograma.

```
Preparação — terraform apply de TODA a camada de dados            ~10 min
Atividade 1 — Storage Account + upload de CSV ao Blob              ~15 min  (L₁)
Atividade 2 — Azure SQL + Key Vault + Python (T_PRODUTOS)          ~30 min  (L₂)
Atividade 3 — Cosmos DB + Azure AI Search (reviews + semantic)     ~50 min  (L₃)
Wrap-up     — terraform destroy + verificação custo zero           ~10 min
```

> **Regra de ouro:** sempre encerrar com `terraform destroy`. Custo zero ao final.

### Por que `terraform apply` de uma vez só, antes das atividades?

A camada de dados completa da QC é uma **declaração única** — provisionar tudo de uma vez (~8 min) reflete como IaC funciona na vida real e libera o lab para focar em **explorar cada peça** via Python. Enquanto o Terraform roda, você lê os arquivos `.tf` para entender o que está sendo construído.

---

## Pré-requisitos

- ✅ Aula 1 concluída (Cloud Shell funcional, Terraform rodando, conta Azure ativa)
- ✅ Repositório `aie-cloud` clonado no Cloud Shell (`git clone https://github.com/elthonf/aie-cloud.git`)
- ✅ Esboço da arquitetura QC do grupo commitado no fork

Se não fez algum desses passos, ver [pre-aula da Aula 1](../../01-fundamentos-iac/pre-aula.md) e [pos-aula-git](../../01-fundamentos-iac/pos-aula-git.md).

---

## Preparação (10 min — antes do L₁)

No Cloud Shell:

```bash
# Confirmar autenticação
az account show --query "{nome:name, id:id}" -o table

# Atualizar o repositório (caso já tenha clonado antes)
cd ~/aie-cloud
git pull origin main

# Ir para a pasta do Terraform da Aula 2
cd aulas/02-storage-bancos/lab/terraform
ls
# Você verá: main.tf  variables.tf  outputs.tf  storage.tf  sql.tf  keyvault.tf  cosmos.tf  search.tf  README.md
```

Leia rapidamente cada `.tf` (5 min) — entenda o que vai ser provisionado. O [README da pasta](terraform/README.md) tem uma visão geral.

### Provisionar tudo

```bash
# Gerar senha forte para o admin do SQL (não use senha trivial)
SQL_PASSWORD=$(openssl rand -base64 24)
echo "Senha gerada (guarde em local seguro): $SQL_PASSWORD"

# Inicializar providers
terraform init

# Aplicar (~8 minutos — vá tomando café e relendo os .tf)
terraform apply -auto-approve -var="sql_admin_password=$SQL_PASSWORD"
```

> **Lições neste passo:**
> - Você gerou uma **senha forte com `openssl`** em vez de inventar — boa prática.
> - O `-var=` passa a senha sem deixá-la em arquivo. Veremos no L₂ como armazená-la no Key Vault para uso pelos serviços.

### Exportar outputs como variáveis de ambiente

Os scripts Python das atividades vão precisar desses valores:

```bash
export STORAGE_ACCOUNT_NAME=$(terraform output -raw storage_account_name)
export KEY_VAULT_NAME=$(terraform output -raw key_vault_name)
export COSMOS_ENDPOINT=$(terraform output -raw cosmos_endpoint)
export SEARCH_ENDPOINT=$(terraform output -raw search_endpoint)

echo "Storage: $STORAGE_ACCOUNT_NAME"
echo "Key Vault: $KEY_VAULT_NAME"
echo "Cosmos: $COSMOS_ENDPOINT"
echo "Search: $SEARCH_ENDPOINT"
```

---

## Atividade 1 — Storage Account + Blob (CSV do catálogo QC)

**Objetivo:** Entender a estrutura de Object Storage e fazer upload do CSV de produtos da QC ao container `catalogo`.

### Passo 1 — Conferir o que foi provisionado

Abra o [storage.tf](terraform/storage.tf) e observe:

- **`azurerm_storage_account.qc`** — a "conta" do storage (nome globalmente único)
- **3 containers** dentro dela: `catalogo`, `imagens`, `logs`
- **`azurerm_storage_management_policy`** — política de lifecycle que migra automaticamente os blobs do prefixo `logs/`: Hot → Cool (30 dias) → Archive (90 dias) → delete (365 dias)

No portal Azure, busque o Storage Account criado e clique em **Containers** para visualizar os 3.

### Passo 2 — Upload do CSV de produtos

O CSV de 20 produtos da QC já está no repo em [data/produtos.csv](data/produtos.csv). Fazer upload:

```bash
az storage blob upload \
  --account-name "$STORAGE_ACCOUNT_NAME" \
  --container-name catalogo \
  --name produtos.csv \
  --file ~/aie-cloud/aulas/02-storage-bancos/lab/data/produtos.csv \
  --auth-mode login \
  --overwrite

# Listar para confirmar
az storage blob list \
  --account-name "$STORAGE_ACCOUNT_NAME" \
  --container-name catalogo \
  --auth-mode login \
  --output table
```

> **Se aparecer "AuthorizationPermissionMismatch"**: você está autenticado mas seu papel ainda não permite Data Plane no Storage. Conceda a role:
> ```bash
> az role assignment create \
>   --assignee $(az ad signed-in-user show --query id -o tsv) \
>   --role "Storage Blob Data Contributor" \
>   --scope $(az storage account show -n "$STORAGE_ACCOUNT_NAME" --query id -o tsv)
> ```
> Aguardar 30s e tentar de novo.

**✅ Checkpoint L₁:** Você consegue listar `produtos.csv` dentro do container `catalogo`?

---

## Atividade 2 — Azure SQL Serverless + Key Vault + Python

**Objetivo:** Popular a tabela `T_PRODUTOS` no Azure SQL **lendo a connection string do Key Vault** (sem hardcoded) e os dados do **CSV no Blob**.

### Passo 1 — Conferir o que foi provisionado

Abra [sql.tf](terraform/sql.tf) e [keyvault.tf](terraform/keyvault.tf). Observe:

- **`azurerm_mssql_database.qc`** — banco SQL **General Purpose Serverless** (`GP_S_Gen5_2`) com **auto-pause** após 60 min de inatividade: pausado, paga-se só o storage (centavos), e com o destroy ao final o custo é desprezível. *(A "oferta gratuita" do Azure SQL ainda não tem suporte no provider azurerm liberado — [PR #32055](https://github.com/hashicorp/terraform-provider-azurerm/pull/32055) — por isso usamos serverless com auto-pause.)*
- **`azurerm_mssql_firewall_rule.cloud_shell`** — libera o IP do Cloud Shell automaticamente (usando o data source `http.meu_ip`).
- **`azurerm_key_vault.qc`** — Vault com **RBAC habilitado** (sem usar Access Policies legadas).
- **`azurerm_key_vault_secret.sql_connection`** — a connection string completa, armazenada como segredo.

> **Por que `time_sleep` antes do segredo?** RBAC tem ~30-60s de propagação. Sem o sleep, o `apply` falha porque a role ainda não está ativa quando o Terraform tenta criar o segredo.

### Passo 2 — Instalar dependências Python

```bash
pip install --user pyodbc azure-identity azure-keyvault-secrets azure-storage-blob
```

> No Cloud Shell, `pip install --user` vai para `~/.local` (storage persistente — não suja a máquina do aluno).

### Passo 3 — Rodar o script

O script [popular_produtos.py](scripts/popular_produtos.py) já está pronto. Ele:

1. Lê a connection string do Key Vault (usando a identidade do Cloud Shell)
2. Baixa o CSV do Blob
3. Conecta no SQL e cria a tabela `T_PRODUTOS`
4. Insere os 20 produtos
5. Mostra o top 3 mais caros

Execute:

```bash
cd ~/aie-cloud/aulas/02-storage-bancos/lab/scripts
python3 popular_produtos.py
```

Esperado: 20 produtos inseridos, lista do top 3 mais caros.

> **Erro comum 1:** "Login failed for user 'sqladminqc'" — a senha tem caractere especial que o shell mascarou. Ver troubleshooting.
>
> **Erro comum 2:** "The client with object id ... does not have authorization to perform action..." no Key Vault — espera 1 min e tenta de novo (a RBAC ainda está propagando, embora o Terraform já tenha esperado 60s).

**✅ Checkpoint L₂:** Você inseriu 20 produtos no Azure SQL **lendo o segredo do Key Vault**?

### Passo 4 — Discussão (3 min)

Anote no `respostas-aula02.md` do seu fork:

1. O que aconteceria se a `conn_str` viesse hardcoded no `popular_produtos.py` e o arquivo fosse commitado num repo público?
2. Como você protegeria esse mesmo segredo se ele fosse usado por um agente AI rodando em Azure Function?
3. Qual o papel do `DefaultAzureCredential` aqui? Por que ele "simplesmente funciona" no Cloud Shell mas não funcionaria no notebook local?

---

## Atividade 3 — Cosmos DB Serverless + Azure AI Search

**Objetivo:** Inserir reviews dos clientes da QC no Cosmos DB (NoSQL) e indexar o catálogo no Azure AI Search com semantic ranking — base para o RAG dos agentes.

### Parte A — Cosmos DB (20 min)

#### Passo 1 — Conferir o que foi provisionado

Abra [cosmos.tf](terraform/cosmos.tf):

- **`azurerm_cosmosdb_account.qc`** — conta Cosmos em modo **Serverless** (paga por operação). Custo das 4h de aula ≈ centavos.
- **Container `reviews`** particionado por `/produto_id`.

> **Por que não Free Tier?** O Free Tier do Cosmos só beneficia *provisioned throughput* (não serverless) e o Azure permite **apenas 1 conta free-tier por assinatura** — o que trava o `apply` se já houver outra. Por isso o lab usa serverless sem free-tier (`var.cosmos_free_tier = false`). Para ligar mesmo assim: `terraform apply -var="cosmos_free_tier=true"`.

#### Passo 2 — Conceder permissão de Data Plane no Cosmos

O Cosmos exige role específica para indexar/consultar via Python:

```bash
COSMOS_NAME=$(cd ~/aie-cloud/aulas/02-storage-bancos/lab/terraform && terraform output -raw cosmos_account_name)
RG=$(cd ~/aie-cloud/aulas/02-storage-bancos/lab/terraform && terraform output -raw resource_group_name)
MY_ID=$(az ad signed-in-user show --query id -o tsv)

az cosmosdb sql role assignment create \
  --account-name "$COSMOS_NAME" \
  --resource-group "$RG" \
  --scope "/" \
  --principal-id "$MY_ID" \
  --role-definition-id 00000000-0000-0000-0000-000000000002

# Aguardar propagação
sleep 30
```

> **Por que via `az` e não Terraform?** A role data plane do Cosmos hoje é melhor concedida via CLI. Em produção, a Function/Agente que acessa o Cosmos teria sua **Managed Identity** com essa role.

#### Passo 3 — Rodar o script de reviews

[popular_reviews.py](scripts/popular_reviews.py) insere 30 reviews fictícias com diferentes scores.

```bash
pip install --user azure-cosmos
cd ~/aie-cloud/aulas/02-storage-bancos/lab/scripts
python3 popular_reviews.py
```

Esperado: 30 reviews inseridas + listagem de reviews score ≥ 4 do produto 5.

#### Passo 4 — Explorar no portal

1. Portal → seu Cosmos account → **Data Explorer**
2. Expandir `qc-db` → `reviews` → **Items**
3. Visualizar os documentos JSON inseridos

**✅ Checkpoint L₃-A:** Você vê 30 reviews no Data Explorer do Cosmos?

---

### Parte B — Azure AI Search (25 min)

#### Passo 1 — Conferir o que foi provisionado

Abra [search.tf](terraform/search.tf):

- **`azurerm_search_service.qc`** — Search service SKU **free** (3 índices, 50 MB) com `semantic_search_sku = "free"`.
- **2 role assignments**: `Search Service Contributor` (gerencia índices) e `Search Index Data Contributor` (indexa/consulta documentos).

> **Atenção:** AI Search Free também é **1 por subscription**. Mesma lógica do Cosmos.

#### Passo 2 — Rodar o script de indexação

[indexar_produtos.py](scripts/indexar_produtos.py) cria o índice `produtos-index` com **analyzer em português** e configuração de semantic ranking, depois indexa os 20 produtos.

```bash
pip install --user azure-search-documents

# Aguardar role propagar (~30s desde o terraform apply)
sleep 30

cd ~/aie-cloud/aulas/02-storage-bancos/lab/scripts
python3 indexar_produtos.py
```

O script já demonstra 3 tipos de busca:
- **Keyword:** `cadeira escritório`
- **Semantic:** `algo para trabalhar em pé`
- **Filtro + ordenação:** `categoria = moveis` ordenado por preço

#### Passo 3 — Validar no portal

1. Portal → `srch-qc-xxxxxx` → **Search Explorer**
2. Testar query: `cadeira ergonomica` — observar resultados
3. Mudar **Query type** para **Semantic** → testar `produto para dor nas costas`
4. Observar o ranking semântico

**✅ Checkpoint L₃-B:** Você consegue executar buscas semânticas via Python e via Portal?

> **Nota importante:** Aqui usamos **semantic search** (ranking inteligente baseado nos modelos da Microsoft). Para fazer **vector search verdadeira** seria preciso gerar embeddings dos textos — chamando Azure OpenAI ou um modelo de embedding. **Veja Exercício 3.1 do [exercicios.md](../exercicios.md)** se quiser implementar vector search real.

---

## Wrap-up — Destroy e Custo Zero (10 min)

### Passo 1 — Destruir o ambiente

```bash
cd ~/aie-cloud/aulas/02-storage-bancos/lab/terraform
terraform destroy -auto-approve -var="sql_admin_password=$SQL_PASSWORD"
```

Tempo: ~5 minutos.

### Passo 2 — Verificar custo zero

1. Portal → **Cost Management** → **Análise de custo** → filtrar por hoje
2. Total deve estar próximo de $0 (serverless/auto-pause + Search free + duração curta do lab)

### Passo 3 — Commitar progresso no seu fork

No seu fork (não no repo `aie-cloud` clonado direto):

```bash
cd ~/aie-cloud-do-meu-fork    # ajuste para o caminho do SEU fork
# Copiar arquivos relevantes para sua estrutura de fork (ou trabalhar direto nele)
git add aula02/
git status
git commit -m "feat(aula02): provisionamento da camada de dados QC"
git push origin main
```

> **NÃO commitar:** O `terraform.tfstate` (já está no `.gitignore`) — ele tem segredos. Se você criou `terraform.tfvars` com a senha, também não commitar.

---

## Conexão com o projeto Quantum Commerce

Saída desta aula — a **camada de dados da QC** está pronta:

```
infrastructure/
  ├── main.tf, variables.tf, outputs.tf
  ├── storage.tf    (Blob: catálogo, imagens, logs)
  ├── sql.tf        (T_PRODUTOS — transacional)
  ├── keyvault.tf   (segredos)
  ├── cosmos.tf     (reviews — NoSQL)
  └── search.tf     (índice de produtos — base de RAG)
```

Esses recursos serão consumidos por:

- **Aula 3** — funções serverless que leem do SQL via Key Vault
- **Aula 4** — serviços cognitivos que usam imagens do Blob e o índice do Search
- **Aula 5** — pipeline de MLOps que treina recomendação sobre reviews + produtos
- **Disciplinas paralelas** — Integration Architecture e Knowledge Management consomem `T_PRODUTOS` e o índice de produtos

---

## Troubleshooting — Problemas comuns

| Problema | Causa | Solução |
|----------|-------|---------|
| `RequestDisallowedByAzure` / "best available regions" no apply | A política da conta Azure for Students bloqueia a região (ex.: `brazilsouth`) para esses recursos | Rode com uma região permitida: `terraform apply -var="location=eastus2"`. Para descobrir as permitidas, abra no portal a criação de um Storage Account e veja as regiões do dropdown |
| Cosmos: "Free tier has already been applied to another account" | Já existe (ou existiu) outra conta Cosmos free-tier na assinatura | Já tratado: o lab usa serverless sem free-tier por padrão. Se você ligou com `-var="cosmos_free_tier=true"`, volte para `false` |
| AI Search: limite de SKU Free atingido | 1 search service Free por subscription | Destruir o existente em outra subscription, ou usar SKU `basic` (~$60/mês — evite) |
| Python: "Login failed for user 'sqladminqc'" | Senha do shell tinha `$` ou aspas — interpretado errado | Use `openssl rand -base64 24` (não contém caracteres problemáticos) ou guarde em variável escapada |
| Python pyodbc: "Can't open lib 'ODBC Driver 18 for SQL Server'" | Cloud Shell pode ter v17 em vez de v18 | Mudar `driver = "{ODBC Driver 17 for SQL Server}"` no script |
| Key Vault: "Forbidden — the user does not have ... action" | RBAC ainda não propagou | `sleep 60` e tentar de novo |
| Cosmos: "Request is unauthorized" | Falta role data plane | Rodar o `az cosmosdb sql role assignment create...` do Passo 2 da Parte A |
| `terraform destroy` falha em Key Vault | Purge protection ou soft-delete | Confirmar `purge_protection_enabled = false` no `keyvault.tf` (já está) |
| `AuthorizationPermissionMismatch` no upload Blob | Sem role data plane no Storage | Conceder `Storage Blob Data Contributor` (ver Passo 2 da L₁) |

---

## Tarefa pós-aula

Antes da Aula 3:

1. **Commitar tudo no fork** (já feito no wrap-up)
2. **Atualizar `respostas-aula02.md`** com:
   - Diagrama da arquitetura QC atualizado (camada de dados detalhada)
   - Respostas às 3 perguntas de reflexão da L₂ (Key Vault)
   - Justificativa: por que esses serviços para esses dados da QC
3. **Resolver pelo menos os exercícios Nível 1** de [exercicios.md](../exercicios.md)

---

## Referências

- [Azure Storage Blob — Lifecycle](https://learn.microsoft.com/azure/storage/blobs/lifecycle-management-overview)
- [Azure SQL Free Offer](https://learn.microsoft.com/azure/azure-sql/database/free-offer)
- [Azure Cosmos DB Free Tier](https://learn.microsoft.com/azure/cosmos-db/free-tier)
- [Azure AI Search — Semantic Ranking](https://learn.microsoft.com/azure/search/semantic-search-overview)
- [Azure AI Search — Vector Search](https://learn.microsoft.com/azure/search/vector-search-overview) (Aula 4 / Exercício 3.1)
- [DefaultAzureCredential — fluxo de autenticação](https://learn.microsoft.com/python/api/overview/azure/identity-readme#defaultazurecredential)
- [Terraform AzureRM Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
