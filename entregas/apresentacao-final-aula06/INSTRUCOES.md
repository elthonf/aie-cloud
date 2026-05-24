# Apresentação Final — Aula 6 (FinOps & Projeto Integrado)

**Vale:** 50% da nota final
**Quando:** ao vivo na Aula 6
**Formato:** apresentação do grupo (10-15 min) + Q&A do professor
**Rubrica específica:** seção "Rubrica da apresentação final" em [rubrica.md](../rubrica.md)

---

## O que apresentar (50 pontos)

| Critério | Pontos | Descrição |
|----------|--------|-----------|
| A — Arquitetura cloud completa | 15 | Todas as camadas (compute, dados, cognitivos, ML) com justificativa de escolhas e conexões claras |
| B — IaC funcionando | 10 | Terraform aplicável sem erros, sem segredos hardcoded, infra reproduzível |
| C — Análise FinOps | 10 | Estimativa executiva detalhada + propostas de otimização concretas |
| D — Conexão com AI/Agentes | 10 | Cada componente justificado pela necessidade dos agentes (RAG, tools, identidade, governança) |
| E — Apresentação coletiva | 5 | **Todos** os membros apresentam; tempo bem distribuído; respostas consistentes |
| **Total** | **50** | |

---

## Estrutura sugerida da apresentação (12 min)

1. **Contexto QC (1 min)** — o problema que vocês estão resolvendo
2. **Arquitetura completa (4 min)** — diagrama final + walkthrough das camadas (cobre Critério A)
3. **IaC demo (2 min)** — `terraform plan` ao vivo OU walkthrough do código já provisionado (Critério B)
4. **Análise de custos (2 min)** — tabela de custo mensal + otimizações propostas (Critério C)
5. **Conexão com agentes (2 min)** — como a arquitetura habilita os agentes da QC, em concreto (Critério D)
6. **Aprendizados do grupo (1 min)** — fecho coletivo

---

## Materiais a levar para a apresentação

- **Slides** (PPT / Google Slides / PDF) — ~10-15 slides; rode previamente para garantir que tudo abre
- **Diagrama final** da arquitetura QC (alta resolução)
- **Repositório privado do grupo** com toda a infra IaC, scripts, notebooks etc. — link no slide final
- **Planilha/tabela** de custos (executar a calculadora Azure no dia ou ter print pronto)
- **Demo opcional** — endpoint vivo ou notebook executando (só se for confiável; senão, vídeo curto pré-gravado)

---

## Boas práticas

- **Ensaie em grupo** — pelo menos uma vez completo, marcando o tempo de cada parte.
- **Decida quem fala o quê** — Critério E exige participação de todos.
- **Antecipe perguntas:** "Por que Cosmos e não Postgres aqui?", "Como o agente acessa este segredo?", "Quanto custaria escalar 10×?".
- **Prepare-se para falar do trade-off** — toda escolha tem alternativas; saiba defender a sua.
- **Não esqueça do FinOps** — Critério C vale 10 pts inteiros; uma proposta de otimização concreta (ex: "trocar VM por Function reduz custo em 60%") faz diferença.

---

## O que o professor avalia ao vivo

- Coerência entre o que cada membro fala (sinal de trabalho coletivo, não fragmentado)
- Qualidade técnica dos slides + diagramas
- Habilidade de defender escolhas arquiteturais sob perguntas
- Conexão visível com tudo que foi entregue nas Aulas 1-5

---

## Após a apresentação

Não há ZIP para esta entrega — a nota vem da apresentação ao vivo + repositório privado linkado.

> Boa apresentação! Esta é a consolidação de tudo que vocês construíram desde a Aula 1.
