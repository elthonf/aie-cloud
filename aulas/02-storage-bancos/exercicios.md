# Exercícios — Aula 2

**Tema:** Storage & Bancos de Dados na Nuvem
**Formato:** **Entrega obrigatória por grupo** — ZIP no Portal FIAP
**Vale:** 10% da nota final ([rubrica completa](../../entregas/rubrica.md))
**Prazo:** 1 dia antes da Aula 3
**Como entregar:** ver [entregas/entrega-02/INSTRUCOES.md](../../entregas/entrega-02/INSTRUCOES.md)

---

## Instruções gerais

Esta é a **2ª entrega de grupo** da disciplina. Os 3 níveis são **divisão de trabalho dentro do grupo**, não escolha livre:

- 🟢 **Nível 1 — Básico:** consolida storage, tiers, relacional vs NoSQL, RBAC do Key Vault
- 🟡 **Nível 2 — Intermediário:** modelagem de dados QC + plano de migração + particionamento Cosmos
- 🔴 **Nível 3 — Avançado:** **bônus opcional** — vector search verdadeira (embeddings), Synapse serverless, benchmark Cosmos vs SQL vs AI Search

**Mínimo obrigatório:** N1 + N2 cobertos. **N3 é bônus** (até +2 pts extras).

### Distribuição entre membros do grupo (sugerida)

- Iniciantes em cloud: N1 (consolidação)
- Intermediários: N2 (bloco QC — matriz de decisão e plano de migração)
- Experientes: N3 (bônus) — vector search é o tópico mais técnico

> **Rodízio:** quem fez N1 na Aula 1 deve preferencialmente fazer N2 ou N3 agora. Vale ponto da rubrica (Critério 4 — Colaboração).

### Template obrigatório

Use o [template em `entregas/template-entrega-grupo.md`](../../entregas/template-entrega-grupo.md) para o `entrega-grupo-aula02.md` dentro do ZIP.

> **Política "no install":** Tudo roda no Azure Cloud Shell. `pip install --user` é OK no Cloud Shell.

---

## 🟢 Nível 1 — Básico: Consolidando os Fundamentos

### Exercício 1.1 — Tipos de Storage

Para cada cenário, escolha **Object Storage**, **File Storage** ou **Block Storage** e justifique em uma frase.

| Cenário | Tipo | Justificativa |
|---------|------|---------------|
| Hospedar imagens de produtos do e-commerce QC (5M de SKUs) | | |
| Disco onde roda o sistema operacional de uma VM de banco | | |
| Pasta compartilhada entre 10 VMs de um time de DevOps | | |
| Backup mensal de bancos de dados (retenção 7 anos) | | |
| Storage de modelos `.pkl` do time de ML para serving | | |
| Dump diário de logs de aplicação para análise futura | | |

<details>
<summary>Gabarito sugerido</summary>

- Imagens de produtos: **Object** (volume alto, acesso via HTTP, sem necessidade de sistema de arquivos)
- Disco da VM de banco: **Block** (baixa latência, atrelado a uma VM)
- Pasta compartilhada entre VMs: **File** (montável em múltiplas VMs simultaneamente como `/mnt/dados`)
- Backup com 7 anos: **Object com Archive tier** (custo baixíssimo, acesso raro)
- Modelos `.pkl` para serving: **Object** (downloads via HTTP, versionamento por blob)
- Logs para análise: **Object com lifecycle Hot→Cool→Archive** (analytics serverless sobre Blob)

</details>

---

### Exercício 1.2 — Tiers de acesso (cálculo)

A Quantum Commerce armazena **2 TB de logs de compras**. Os primeiros 30 dias os logs são consultados para detecção de fraude (Hot). Depois disso, viram dados arquivados de compliance LGPD (Archive, retenção 5 anos).

a) Quanto custaria 1 mês desses logs **se mantidos 100% em Hot tier**? (Use ~$0,018/GB/mês)
b) Quanto custaria 1 mês desses logs **com lifecycle: 30 dias Hot + Archive depois**? (Archive ~$0,002/GB/mês)
c) Economia anual com a lifecycle policy?

<details>
<summary>Gabarito</summary>

- a) 2.048 GB × $0,018 = **$36,86/mês** (~$442/ano)
- b) Dados estão sempre em Archive depois de 30 dias. Considerando steady state, ~96,7% em Archive:
  - Hot: 2048 × 30/365 × $0,018 = $3,03/mês (média anual)
  - Archive: 2048 × 335/365 × $0,002 = $3,76/mês (média anual)
  - Total: ~**$6,79/mês**
- c) Economia anual: ($36,86 - $6,79) × 12 = **~$360/ano**

> Para a QC com volumes reais (centenas de TB), essa decisão impacta facilmente seis dígitos por ano.

</details>

---

### Exercício 1.3 — Relacional vs NoSQL

Para cada caso de uso da Quantum Commerce, marque qual tipo de banco é mais adequado e justifique:

| Caso de uso | Relacional (Azure SQL) | NoSQL doc (Cosmos) | Vector DB (AI Search) | Justificativa |
|-------------|------------------------|--------------------|-----------------------|---------------|
| Carrinho de compras ativo do usuário | | | | |
| Catálogo de produtos com SKU, preço, estoque | | | | |
| Reviews dos clientes (texto livre + score) | | | | |
| "Encontre produtos similares a este" (recomendação) | | | | |
| Histórico de pedidos para faturamento | | | | |
| Sessão do usuário (chave-valor, expira em 30min) | | | | |
| Logs de comportamento de navegação | | | | |

<details>
<summary>Sugestões</summary>

- Carrinho ativo: **NoSQL doc** (esquema variável, leitura rápida, expira)
- Catálogo: **Relacional** (esquema fixo, joins com categorias, integridade de estoque)
- Reviews: **NoSQL doc** (texto livre, sem schema rígido)
- Recomendação: **Vector DB** (similaridade semântica)
- Histórico de pedidos: **Relacional** (ACID, faturamento exige garantias)
- Sessão (key-value): **Redis** ou **Cosmos com TTL** (não cabe perfeitamente nas opções, mas Cosmos é o mais próximo)
- Logs de navegação: **NoSQL** ou Object Storage + Synapse — depende do uso analítico

</details>

---

### Exercício 1.4 — Key Vault e RBAC

Você acabou de provisionar o Key Vault da Aula 2. Para cada perfil, escolha a role built-in e justifique:

| Perfil | Role no Key Vault | Justificativa |
|--------|-------------------|---------------|
| Você (criador do Vault, faz dev e ops) | | |
| Azure Function que consulta `T_PRODUTOS` precisa ler a connection string | | |
| Engenheiro de segurança que audita os segredos sem alterá-los | | |
| Pipeline de CI/CD que injeta novos segredos automaticamente | | |
| Time de FinOps que precisa ver custo do Vault sem ver segredos | | |

**Referência:** [Azure Built-in Roles — Key Vault](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#key-vault)

<details>
<summary>Sugestões</summary>

- Você: **Key Vault Secrets Officer** (CRUD em segredos — sem precisar de Owner)
- Function lendo segredos: **Key Vault Secrets User** (só leitura no plano de dados de segredos) — via Managed Identity
- Auditor: **Key Vault Reader** (lê metadados, não os valores)
- CI/CD injetando segredos: **Key Vault Secrets Officer** com escopo limitado (idealmente Service Principal dedicado)
- FinOps: **Reader** no Resource Group (vê custo no Cost Management, não acessa Vault)

</details>

---

## 🟡 Nível 2 — Intermediário: Decisões Arquiteturais

### Exercício 2.1 — Modelagem de dados da QC (em grupo)

A Quantum Commerce tem os seguintes domínios:

- **Produtos** (catálogo: 5M SKUs)
- **Clientes** (~50M de clientes ativos, perfil + endereço + preferências)
- **Pedidos** (~10M/mês, alta criticidade transacional)
- **Carrinhos ativos** (~500k a qualquer momento, expiram em 24h)
- **Reviews** (~30M de textos livres, alimentam análise de sentimento)
- **Busca de produtos** (consultas dos agentes + frontend)
- **Sessões de usuário** (~1M ativas)
- **Histórico de navegação** (clickstream — bilhões de eventos)
- **Modelos de ML** (recomendação, classificação, predição de churn)

**Sua tarefa:** Preencha a matriz de decisão abaixo:

| Domínio | Serviço Azure escolhido | SKU/Configuração | Justificativa em 1-2 frases |
|---------|-------------------------|------------------|------------------------------|
| Produtos | | | |
| Clientes | | | |
| Pedidos | | | |
| Carrinhos | | | |
| Reviews | | | |
| Busca de produtos | | | |
| Sessões | | | |
| Histórico navegação | | | |
| Modelos ML | | | |

**Bonus:** Desenhe o diagrama da camada de dados completa da QC no Excalidraw / draw.io e cole no `respostas-aula02.md`.

> Este exercício é peça-chave do projeto final. Tente fazer em grupo discutindo cada decisão.

---

### Exercício 2.2 — Plano de migração de dados

A Quantum Commerce hoje tem:

- Banco Oracle on-premise com 8 TB (produtos + pedidos + clientes)
- 50 TB de imagens em servidor NAS local
- ~200 TB de logs históricos em fitas magnéticas (compliance fiscal)

**Sua tarefa:** Proponha um plano de migração de 12 meses considerando:

a) **Quais dos 6 Rs** (Aula 1) você usaria para cada repositório atual?
b) **Quais serviços Azure** ficariam com cada um, considerando custo + criticidade?
c) **Como migrar** sem downtime? (Pesquise sobre Azure Database Migration Service e AzCopy)
d) **Estimativa de custo de egress** para os 50 TB de imagens (a primeira saída custa banda)
e) **Como manter compliance LGPD** — onde os dados de brasileiros podem ficar?

Use as calculadoras dos 3 provedores se quiser comparar custos.

---

### Exercício 2.3 — Particionamento no Cosmos DB

No lab da Aula 2, o container `reviews` foi particionado por `produto_id`. Responda:

a) Por que **NÃO** seria boa partitioning key:
   - `id` da review? (3 razões)
   - `score` (1-5)? (2 razões)
   - `data_da_review` (timestamp)? (2 razões)

b) Por que `produto_id` **funciona razoavelmente bem** mas pode ter um problema. Qual problema?

c) Se a QC quisesse otimizar para "todas as reviews de um cliente específico", como seria a estratégia? (Pesquise sobre "hierarchical partition keys" do Cosmos)

d) Estime: se um produto tiver 50.000 reviews, qual o tamanho aproximado da partição? Quanto isso é da quota de 20 GB por partição lógica do Cosmos?

---

## 🔴 Nível 3 — Avançado: Vector Search Real e Analytics

### Exercício 3.1 — Vector search verdadeira no AI Search

O lab usou `semantic_search`. Vamos agora fazer **vector search real** gerando embeddings.

**Tudo no Cloud Shell — sem instalação local.**

#### Parte A — Gerar embeddings

Como a disciplina é Cloud (e Azure OpenAI não está no escopo padrão), use a biblioteca `sentence-transformers` que roda local no Cloud Shell:

```bash
pip install --user sentence-transformers azure-search-documents azure-storage-blob azure-identity
```

> ⚠️ Sentence Transformers baixa modelo de ~80MB no primeiro uso — vai para `~/.cache` no storage persistente do Cloud Shell.

Script:

```python
"""
Gera embeddings dos produtos e indexa no AI Search com campo vector.
Requer: pip install --user sentence-transformers azure-search-documents
"""
import os, csv
from sentence_transformers import SentenceTransformer
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchField,
    SearchFieldDataType, VectorSearch, HnswAlgorithmConfiguration,
    VectorSearchProfile,
)
from azure.search.documents import SearchClient
from azure.storage.blob import BlobServiceClient

DIMENSION = 384  # all-MiniLM-L6-v2 produz vetores 384-dim
INDEX_NAME = "produtos-vector-index"

def main():
    endpoint = os.environ["SEARCH_ENDPOINT"]
    storage = os.environ["STORAGE_ACCOUNT_NAME"]
    credential = DefaultAzureCredential()

    print("→ Carregando modelo de embedding...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Baixar produtos
    blob = BlobServiceClient(f"https://{storage}.blob.core.windows.net", credential=credential)
    csv_text = blob.get_blob_client("catalogo", "produtos.csv").download_blob().readall().decode("utf-8")
    rows = list(csv.DictReader(csv_text.splitlines()))

    # Gerar embeddings de "nome + descricao"
    print(f"→ Gerando embeddings de {len(rows)} produtos...")
    textos = [f"{r['nome']}. {r['descricao']}" for r in rows]
    embeddings = model.encode(textos).tolist()
    print(f"✓ Embeddings gerados (dim={len(embeddings[0])})")

    # Definir índice com campo vector
    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
    index = SearchIndex(
        name=INDEX_NAME,
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="nome", type=SearchFieldDataType.String),
            SearchableField(name="descricao", type=SearchFieldDataType.String),
            SimpleField(name="categoria", type=SearchFieldDataType.String, filterable=True),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=DIMENSION,
                vector_search_profile_name="produtos-hnsw-profile",
            ),
        ],
        vector_search=VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="produtos-hnsw")],
            profiles=[VectorSearchProfile(name="produtos-hnsw-profile", algorithm_configuration_name="produtos-hnsw")],
        ),
    )
    try: index_client.delete_index(INDEX_NAME)
    except: pass
    index_client.create_index(index)

    # Indexar
    search_client = SearchClient(endpoint=endpoint, index_name=INDEX_NAME, credential=credential)
    docs = [
        {
            "id": r["id"], "nome": r["nome"], "descricao": r["descricao"],
            "categoria": r["categoria"], "content_vector": embeddings[i],
        }
        for i, r in enumerate(rows)
    ]
    search_client.upload_documents(docs)
    print(f"✓ {len(docs)} produtos indexados com vetores")

    # Busca por vetor: gerar embedding da query e buscar nearest
    queries = [
        "preciso de uma cadeira boa para minha coluna",
        "algo para acompanhar séries",
        "presente para um amigo que ama café",
    ]
    for q in queries:
        q_vec = model.encode(q).tolist()
        print(f"\n=== Vector search: '{q}' ===")
        results = search_client.search(
            search_text=None,
            vector_queries=[{
                "kind": "vector",
                "vector": q_vec,
                "k_nearest_neighbors": 3,
                "fields": "content_vector",
            }],
        )
        for r in results:
            print(f"  [{r['@search.score']:.4f}] {r['nome']}")

if __name__ == "__main__":
    main()
```

**Tarefa:** Execute, registre os resultados das 3 queries no `respostas-aula02.md` e **compare** com o semantic search do lab (parte B). Qual deu resultados mais relevantes? Onde cada um falha?

#### Parte B — Reflexão

Responda no `respostas-aula02.md`:

1. Por que o modelo `all-MiniLM-L6-v2` é uma má escolha para produção da Quantum Commerce? (Dica: língua portuguesa, latência, qualidade)
2. Que serviço da Azure você usaria para gerar embeddings em produção? (Dica: Azure OpenAI text-embedding-3-large)
3. Como você manteria os embeddings atualizados quando produtos novos chegam? (Pipeline incremental)
4. Quanto custaria gerar embeddings para 5M de produtos da QC com Azure OpenAI? (Pesquise os preços)

---

### Exercício 3.2 — Synapse Serverless: query sobre Blob

A QC armazenou os `logs de compras` em formato Parquet no Blob. Em vez de carregar tudo num DWH, vamos usar **Synapse Serverless SQL Pool** para queryar direto no Blob (zero ETL).

#### Setup

Adicione ao Terraform (crie `lab/terraform/synapse.tf` no seu fork):

```hcl
resource "azurerm_synapse_workspace" "qc" {
  name                                 = "synapse-qc-${random_string.sufixo.result}"
  resource_group_name                  = azurerm_resource_group.rg.name
  location                             = azurerm_resource_group.rg.location
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.synapse.id
  sql_administrator_login              = "synadmin"
  sql_administrator_login_password     = var.sql_admin_password
  identity { type = "SystemAssigned" }
  tags = local.tags
}

# Synapse precisa de Data Lake Storage Gen2
resource "azurerm_storage_data_lake_gen2_filesystem" "synapse" {
  name               = "synapsefs"
  storage_account_id = azurerm_storage_account.qc.id   # precisa de is_hns_enabled=true
}

resource "azurerm_synapse_firewall_rule" "all_azure" {
  name                 = "AllowAzure"
  synapse_workspace_id = azurerm_synapse_workspace.qc.id
  start_ip_address     = "0.0.0.0"
  end_ip_address       = "0.0.0.0"
}
```

> ⚠️ Synapse requer Storage com HNS habilitado: no `azurerm_storage_account` adicione `is_hns_enabled = true`. Isso impede algumas features de Blob clássico — leia a doc.

#### Gerar dados de exemplo

Crie 3 arquivos `logs_compras_jan.csv`, `_fev.csv`, `_mar.csv` com 1000 registros cada (script no `respostas-aula02.md`) e faça upload ao Blob.

#### Query no Synapse

1. No portal, abrir o Synapse Studio
2. Conectar ao Serverless SQL Pool
3. Executar:

   ```sql
   SELECT
     CAST(periodo AS DATE) AS dia,
     COUNT(*)              AS pedidos,
     SUM(valor)            AS receita
   FROM OPENROWSET(
     BULK 'https://STORAGE.blob.core.windows.net/logs/compras_*.csv',
     FORMAT = 'CSV',
     PARSER_VERSION = '2.0',
     FIRSTROW = 2
   ) WITH (periodo VARCHAR(20), valor DECIMAL(10,2)) AS dados
   GROUP BY CAST(periodo AS DATE)
   ORDER BY dia;
   ```

4. **Reporte:** quantos bytes Synapse processou na query? (visível na aba "Resultados")

#### Reflexão

Responda no `respostas-aula02.md`:

1. Por que Synapse Serverless faz sentido para a QC em vez de Synapse Dedicated Pool?
2. Qual o custo de query: 5 TB processados/mês a $5 por TB?
3. Como reduzir custo por query? (Dica: Parquet + partições)

---

### Exercício 3.3 — Benchmark: Cosmos vs SQL vs AI Search

Para a query "buscar produto que melhor responde à pergunta `cadeira ergonômica para dor lombar`", você tem 3 opções na QC:

a) **Azure SQL** com `LIKE '%cadeira%'` e filtros sobre categoria/preço
b) **Cosmos DB** com índice full-text (Cosmos não tem nativo — precisa Azure AI Search externo)
c) **Azure AI Search** com semantic ranking ou vector search

**Tarefa:**

1. Implemente as 3 versões (você já tem AI Search no lab — adicione versão SQL e Cosmos)
2. Meça latência média de 10 queries em cada
3. Compare **qualidade** das respostas (subjetivamente — quem traria o produto certo?)
4. Compare **custo** projetado: 1M queries/mês em cada
5. **Recomende** qual usar para o agente de busca da QC

Entrega: tabela comparativa + recomendação justificada no `respostas-aula02.md`.

---

## Critérios de entrega

A entrega é **um ZIP por grupo** (`entrega-grupo-NN-aula02.zip`) no Portal FIAP. Estrutura completa, prazo e dicas de geração do ZIP em [entregas/entrega-02/INSTRUCOES.md](../../entregas/entrega-02/INSTRUCOES.md).

| Item | Obrigatório? | Pontos máximos |
|------|--------------|----------------|
| Cabeçalho do grupo + distribuição do trabalho | ✅ Sim | 1 pt (Critério 4) |
| 🟢 N1 — Exercícios 1.1, 1.2, 1.3, 1.4 respondidos | ✅ Sim | 3 pts (Critério 1) |
| 🟡 N2 — 2.1 (matriz + diagrama), 2.2 (migração), 2.3 (particionamento Cosmos) | ✅ Sim | 3 pts (Critério 2) + 2 pts qualidade técnica (Critério 3) |
| 🔴 N3 — 3.1 (vector search verdadeira), 3.2 (Synapse), 3.3 (benchmark) | 🎁 Bônus | até +2 pts extras |
| Reflexão coletiva ao final | ✅ Sim | 1 pt (Critério 5) |
| **Total da entrega** | | **10 pts** (10% da nota final) |

**Prazo:** 1 dia antes da Aula 3.
**Onde:** upload do ZIP no Portal FIAP. Apenas 1 membro do grupo faz o upload.
