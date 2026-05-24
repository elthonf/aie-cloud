# Entrega 04 — Aula 4 (Serviços Cognitivos & APIs)

**Vale:** 10% da nota final
**Prazo:** até 1 dia antes da Aula 5
**Onde:** upload de UM ZIP no Portal FIAP

---

## O que entregar (preview — material da aula em construção)

Aplica-se a [rubrica única](../rubrica.md). Mínimo obrigatório:

- ✅ Cabeçalho do grupo + distribuição do trabalho
- ✅ 🟢 N1 — Conceitos: APIs cognitivas prontas vs modelos customizados, trade-offs de custo/latência/controle
- ✅ 🟡 N2 — Bloco do projeto QC: pipeline cognitivo integrado (Vision + Speech + Language) — ex.: busca de produto por imagem, análise de sentimento de reviews
- 🎁 🔴 N3 (bônus) — exercício avançado
- ✅ Reflexão coletiva

Material detalhado em `aulas/04-servicos-cognitivos/` (a publicar).

---

## Estrutura do ZIP

Nome: `entrega-grupo-NN-aula04.zip`.

```
qc-grupo-NN-aula04/
├── entrega-grupo-aula04.md
├── README.md
├── terraform/                 # Azure AI Services
├── scripts/                   # Pipelines Python (Vision/Speech/Language)
└── diagramas/                 # Arquitetura QC atualizada com camada cognitiva
```

**NÃO incluir:** `terraform.tfstate*`, `.env`, `*.pem`, `__pycache__/`.

---

```bash
cd ~/qc-grupo-NN
git pull origin main
git archive --format=zip --prefix=qc-grupo-NN-aula04/ -o ~/entrega-grupo-NN-aula04.zip HEAD:aula04
```

Upload no Portal FIAP, tarefa "Entrega Aula 4".

---

> **Esta página é um placeholder** — instruções detalhadas serão atualizadas com o material completo da Aula 4.
