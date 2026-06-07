# Aula 2 — Armazenamento & Bancos de Dados na Nuvem

## Objetivos de aprendizagem

Ao final desta aula, você será capaz de:

- Distinguir os 3 tipos de storage em cloud (Object, File, Block) e escolher o adequado para cada caso de uso.
- Provisionar e configurar um Azure Storage Account via Terraform com containers, tiers e lifecycle policies.
- Diferenciar bancos de dados relacionais (SQL) e NoSQL (documentos), entendendo quando usar cada um.
- Provisionar um **Azure SQL Database Serverless (auto-pause)** via Terraform e popular tabelas via Python.
- Aplicar **Azure Key Vault** para eliminar segredos hardcoded (connection strings, API keys).
- Provisionar **Cosmos DB Serverless** e popular documentos via Python.
- Criar um índice no **Azure AI Search** e fazer busca semântica — base para o RAG dos agentes da QC.
- Reconhecer quando se usa um banco analítico (Synapse/Fabric) — sem aprofundar no lab.
- Integrar os componentes provisionados à arquitetura cloud da Quantum Commerce.

---

## Por que esta aula importa para um AI Engineer

> *"Um agente sem dados é um chatbot genérico. Um agente com os dados certos, na estrutura certa, no banco certo — é uma experiência transformadora."*

Storage e banco **não são detalhes de implementação** — são decisões arquiteturais que definem o que um agente consegue (ou não) fazer.

---

## Conexão com o Quantum Commerce

Nesta aula você define **onde os dados dos agentes da Quantum Commerce vão viver**:

- **Catálogo de produtos** → Azure SQL (esquema fixo, joins, integridade)
- **Imagens e arquivos** → Blob Storage (object storage)
- **Reviews dos clientes** → Cosmos DB (NoSQL, texto livre)
- **Índice semântico de busca** → Azure AI Search (base de RAG)
- **Segredos (connection strings)** → Key Vault (nunca hardcoded)

A camada de dados desta aula é consumida pelas funções da **Aula 3**, pelos serviços cognitivos da **Aula 4** e pelo pipeline de MLOps da **Aula 5**.

---

## Material da aula

| Arquivo | Quando usar |
|---------|-------------|
| [lab/guia-lab.md](lab/guia-lab.md) | Durante a aula — 3 atividades intercaladas |
| [lab/terraform/](lab/terraform/) | Código IaC pronto (8 arquivos `.tf`) |
| [lab/scripts/](lab/scripts/) | Scripts Python (popular SQL, popular Cosmos, indexar Search) |
| [lab/data/produtos.csv](lab/data/produtos.csv) | 20 produtos de exemplo da QC |
| [exercicios.md](exercicios.md) | Após a aula — exercícios em 3 níveis (🟢/🟡/🔴) que compõem a entrega de grupo |

## Entrega de grupo

Esta aula gera a **2ª entrega de grupo** (10% da nota): instruções em [entregas/entrega-02/](../../entregas/entrega-02/). Rubrica única em [entregas/rubrica.md](../../entregas/rubrica.md).

---

## Pré-requisitos

- ✅ Aula 1 concluída — Azure ativo, Cloud Shell, Terraform funcionando
- ✅ Tarefa pós-Aula 1 entregue — `respostas-aula01.md` no fork via github.dev (ver [pos-aula-git](../01-fundamentos-iac/pos-aula-git.md))
- ✅ Esboço da arquitetura QC do grupo commitado no fork (diagrama Excalidraw/draw.io/foto)

Quem perdeu a Aula 1: faça o [pre-aula](../01-fundamentos-iac/pre-aula.md) e o [pos-aula-git](../01-fundamentos-iac/pos-aula-git.md) da Aula 1 antes desta aula.
