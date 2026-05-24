# Entrega 03 — Aula 3 (Serverless & Containers)

**Vale:** 10% da nota final
**Prazo:** até 1 dia antes da Aula 4
**Onde:** upload de UM ZIP no Portal FIAP

---

## O que entregar (preview — material da aula em construção)

Aplica-se a [rubrica única](../rubrica.md). Mínimo obrigatório:

- ✅ Cabeçalho do grupo + distribuição do trabalho
- ✅ 🟢 N1 — Conceitos: serverless vs containers vs VMs, modelo de cobrança serverless, papel do Kubernetes
- ✅ 🟡 N2 — Bloco do projeto QC: **Function HTTP funcional** + **Dockerfile** + **reflexão sobre Function vs Container** + spec de tool de agente que consume a API
- 🎁 🔴 N3 (bônus) — exercício avançado (definido no `exercicios.md` da Aula 3)
- ✅ Reflexão coletiva

Material detalhado em `aulas/03-serverless-containers/` (a publicar).

---

## Estrutura do ZIP

Nome: `entrega-grupo-NN-aula03.zip`.

```
qc-grupo-NN-aula03/
├── entrega-grupo-aula03.md
├── README.md
├── terraform/                 # Function App + Container Registry
├── functions/                 # Código Python da Function
├── docker/                    # Dockerfile e imagem
└── diagramas/                 # Arquitetura QC atualizada com camada de API
```

**NÃO incluir:** `terraform.tfstate*`, `.env`, `*.pem`, `__pycache__/`.

---

## Como gerar e enviar

```bash
cd ~/qc-grupo-NN
git pull origin main
git archive --format=zip --prefix=qc-grupo-NN-aula03/ -o ~/entrega-grupo-NN-aula03.zip HEAD:aula03
```

Upload no Portal FIAP, tarefa "Entrega Aula 3".

---

> **Esta página é um placeholder** — instruções detalhadas serão atualizadas com o material completo da Aula 3.
