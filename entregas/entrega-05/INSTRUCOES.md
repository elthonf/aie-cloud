# Entrega 05 — Aula 5 (MLOps)

**Vale:** 10% da nota final
**Prazo:** até 1 dia antes da Aula 6
**Onde:** upload de UM ZIP no Portal FIAP

---

## O que entregar (preview — material da aula em construção)

Aplica-se a [rubrica única](../rubrica.md). Mínimo obrigatório:

- ✅ Cabeçalho do grupo + distribuição do trabalho
- ✅ 🟢 N1 — Conceitos: ciclo de vida de modelos, MLflow, versionamento de dados/código/modelos
- ✅ 🟡 N2 — Bloco do projeto QC: **modelo registrado** (MLflow) + **endpoint de predição funcionando** — ex.: recomendação de produtos
- 🎁 🔴 N3 (bônus) — exercício avançado
- ✅ Reflexão coletiva

Material detalhado em `aulas/05-mlops/` (a publicar).

---

## Estrutura do ZIP

Nome: `entrega-grupo-NN-aula05.zip`.

```
qc-grupo-NN-aula05/
├── entrega-grupo-aula05.md
├── README.md
├── terraform/                 # Azure ML Workspace
├── notebooks/                 # Notebooks de treino (Jupyter)
├── scripts/                   # Pipeline de deploy do endpoint
└── diagramas/                 # Arquitetura QC atualizada com camada de MLOps
```

**NÃO incluir:** `terraform.tfstate*`, `.env`, `*.pem`, `__pycache__/`.

---

```bash
cd ~/qc-grupo-NN
git pull origin main
git archive --format=zip --prefix=qc-grupo-NN-aula05/ -o ~/entrega-grupo-NN-aula05.zip HEAD:aula05
```

Upload no Portal FIAP, tarefa "Entrega Aula 5".

---

> **Esta página é um placeholder** — instruções detalhadas serão atualizadas com o material completo da Aula 5.
