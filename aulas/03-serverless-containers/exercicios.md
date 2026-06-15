# Exercícios — Aula 3

**Tema:** Serverless & Containers
**Formato:** **Entrega obrigatória por grupo** — ZIP no Portal FIAP
**Vale:** 10% da nota final ([rubrica completa](../../entregas/rubrica.md))
**Prazo:** 1 dia antes da Aula 4
**Como entregar:** ver [entregas/entrega-03/INSTRUCOES.md](../../entregas/entrega-03/INSTRUCOES.md)

---

## Instruções gerais

Esta é a **3ª entrega de grupo** da disciplina. Os 3 níveis são **divisão de trabalho dentro do grupo**:

- 🟢 **Nível 1 — Básico:** serverless, Managed Identity, Function vs Container, Dockerfile review
- 🟡 **Nível 2 — Intermediário:** segunda tool (cálculo de frete), Application Insights e observabilidade, endurecimento/dimensionamento do ACI
- 🔴 **Nível 3 — Avançado:** **bônus opcional** — spec de tool para agente AI, benchmark de carga, CI/CD com GitHub Actions + OIDC

**Mínimo obrigatório:** N1 + N2 cobertos. **N3 é bônus** (até +2 pts extras).

### Distribuição entre membros (sugerida)

- Iniciantes: N1 (consolidação dos conceitos de serverless + MI)
- Intermediários: N2 (estender a Function da aula com nova tool e observabilidade)
- Experientes: N3 (bônus) — design de tool de agente, benchmark, CI/CD

> **Rodízio:** quem fez N1 nas Aulas 1-2 deve assumir N2 ou N3 agora. Vale Critério 4 da rubrica.

### Template obrigatório

Use o [template em `entregas/template-entrega-grupo.md`](../../entregas/template-entrega-grupo.md) para o `entrega-grupo-aula03.md` dentro do ZIP.

> **Política "no install":** Tudo no Azure Cloud Shell.

---

## 🟢 Nível 1 — Básico: Consolidando os Fundamentos

### Exercício 1.1 — Quando usar Serverless?

Para cada cenário da Quantum Commerce, marque **Function**, **ACI**, **Container Apps** ou **AKS** e justifique em uma frase:

| Cenário | Escolha | Justificativa |
|---------|---------|---------------|
| API de busca de produtos (1M chamadas/mês, picos na Black Friday) | | |
| Worker que processa pedidos da fila (1000 pedidos/dia, picos noturnos) | | |
| API legado em Java Spring Boot (não pode reescrever, time conhece) | | |
| Pipeline de processamento de imagens de produtos (chega 1 hora por noite) | | |
| Microserviço de pagamentos (regulado, precisa logs detalhados, 100 req/s constante) | | |
| Plataforma com 25 microserviços + service mesh (Itaú-like) | | |
| Container que extrai dados uma vez por dia e morre | | |

<details>
<summary>Sugestões de gabarito</summary>

- API de busca (1M/mês, picos): **Function** — pay-per-call, scale automático, free tier cobre
- Worker de fila: **Function com Queue trigger** ou **Container Apps com KEDA** — event-driven, scale to zero
- Java Spring Boot legado: **Container Apps** (auto-scale) ou **App Service** (PaaS clássico) — Function tem custom handler mas é overhead
- Pipeline batch de 1h/noite: **ACI** — pay-per-second, sem manter ligado, simples
- Pagamentos com tráfego constante e regulado: **Container Apps** ou **AKS** — controle fino, logs/auditoria, sem cold start
- 25 microserviços + service mesh: **AKS** — único que comporta service mesh maduro
- Container one-shot: **ACI** — exato caso de uso

</details>

---

### Exercício 1.2 — Managed Identity vs alternativas

Para cada estratégia de credencial, marque **vulnerabilidade alta**, **média** ou **baixa** e justifique:

| Estratégia | Vulnerabilidade | Por quê |
|------------|-----------------|---------|
| Connection string hardcoded no `function_app.py` | | |
| Connection string em variável de ambiente do Function App | | |
| Connection string em Key Vault, lida via API key do Vault | | |
| Connection string em Key Vault, lida via Managed Identity | | |
| Sem connection string — Managed Identity diretamente no recurso (Storage) | | |

**Pergunta adicional:** Em uma das estratégias acima, **um vazamento do código no GitHub continua sendo problema**? Em quais não é? Por quê?

---

### Exercício 1.3 — Cold start na prática

Faça **3 chamadas** à sua Function (do lab L₂), com intervalo de:

- Chamada 1: **agora** (Function provavelmente fria)
- Chamada 2: **5 segundos depois**
- Chamada 3: **30 minutos depois** (Function provavelmente fria de novo)

Use `time curl ...` para medir.

Preencha:

| Chamada | Tempo decorrido | Observação |
|---------|-----------------|------------|
| 1 (fria) | | |
| 2 (quente) | | |
| 3 (fria de novo) | | |

**Pergunta:** Se o agente da QC chamar essa Function 1 vez a cada hora durante o dia (24 chamadas), quantas serão "frias"? Como você mitigaria isso se a UX dos usuários exige resposta em < 500ms?

---

### Exercício 1.4 — Dockerfile review

Considere este `Dockerfile` para a API da QC:

```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

Liste **5 problemas** com este Dockerfile (segurança, tamanho, eficiência, boas práticas) e proponha melhorias.

<details>
<summary>Sugestões</summary>

1. Usa `python:3.11` (imagem completa ~1GB) em vez de `python:3.11-slim` (~150MB) → trocar para slim
2. `COPY . .` copia TUDO incluindo `.git`, `__pycache__`, etc. → usar `.dockerignore`
3. `pip install -r requirements.txt` sem `--no-cache-dir` → infla a imagem
4. Não usa multi-stage build → builders + libs grandes ficam no runtime
5. Roda como root → `USER appuser` (não-root) para segurança
6. `CMD ["python", "app.py"]` para web service → deveria usar uvicorn/gunicorn explicitamente
7. Não declara EXPOSE → menos legível
8. Sem `HEALTHCHECK` → orquestrador não sabe se está saudável

</details>

---

## 🟡 Nível 2 — Intermediário: Decisões de Design + IaC

### Exercício 2.1 — Adicionar segunda tool no agente: cálculo de frete

A QC tem outro caso de uso para Function: **calcular frete**. Specs:

- Input: CEP origem, CEP destino, peso (kg)
- Output: valor em R$ + tempo estimado de entrega
- Lógica: cálculo simples (R$ por km + R$ por kg). Pode ser determinístico.
- 50.000 chamadas/mês esperadas

**Sua tarefa:**

a) Decida: nova Function no mesmo Function App, ou novo Function App separado?
b) Implemente a Function HTTP `calcular_frete` no mesmo `function_app.py` da Aula 3 (continue a aplicação).
c) Atualize o Terraform se necessário (provavelmente não — mesma Function App).
d) Documente como "tool" no formato JSON Schema (parecido com o catálogo no wrap-up da aula).
e) Reflexão: quando você criaria **um Function App diferente** vs **adicionar funções no mesmo App**?

---

### Exercício 2.2 — Application Insights e observabilidade

A Function da Aula 3 não tinha Application Insights habilitado (foi desativado para custo). Em produção, você quer observabilidade.

**Sua tarefa:**

a) Estenda o Terraform da Aula 3 para criar `azurerm_application_insights` e conectar à Function via `application_insights_connection_string`.
b) Após aplicar, faça 20 chamadas variadas à Function e abra o portal → Application Insights → Live Metrics. Tire **um print** da tela mostrando as métricas.
c) Use o **Failures blade** do AI para responder:
   - Quanto % das suas chamadas falhou (se houver)?
   - Qual o p95 de latência da Function?
   - Onde está o "gargalo" (tempo gasto em I/O, computação, etc.)?
d) Pergunta de arquitetura: para um sistema multi-agente em produção, qual a estratégia ideal de logs/métricas/traces? Pesquise sobre **OpenTelemetry**.

---

### Exercício 2.3 — Endurecer e dimensionar o ACI da QC

O lab (Atividade 3) subiu um ACI **básico**. Aqui você evolui esse mesmo ACI no Terraform para cenários mais próximos de produção da QC.

**Sua tarefa (partindo do `containers.tf` do lab):**

a) **Restart policy** — o ACI do lab usa o padrão (`Always`, bom para um serviço sempre-on). Crie/justifique uma variante para um **job batch** da QC (ex.: recalcular recomendações à noite e terminar) usando `restart_policy = "OnFailure"`. Explique em uma frase quando usar `Always`, `OnFailure` e `Never`.

b) **Right-sizing + custo** — o ACI do lab usa `0.5` vCPU / `1.0` GB. Suba uma variante com `1` vCPU / `2` GB. No [Pricing Calculator](https://azure.microsoft.com/pricing/calculator), estime o custo/hora de cada uma e o custo de deixar **1 ACI 24/7** vs a **Function equivalente** (que escala a zero). ACI cobra por segundo enquanto o container existir.

c) **Segredo via secure env** — mova ao menos uma configuração para `secure_environment_variables` (não aparece em texto plano no portal/CLI) em vez de `environment_variables`. Mostre a diferença ao inspecionar com `az container show`.

d) **Limite de réplica única** — o ACI roda **1 réplica fixa**, sem autoscale nativo. Explique o que isso significa para um pico de tráfego da QC (ex.: Black Friday) e qual serviço (Function/AKS/Container Apps) você escolheria nesse caso e por quê.

e) **Reflexão:** Para a QC, em quais workloads você levaria **ACI** e em quais levaria **Function**? Considere custo idle, HTTPS, escala e simplicidade operacional.

---

## 🔴 Nível 3 — Avançado: Tool de Agente + Benchmark + CI/CD

### Exercício 3.1 — Function como Tool de um Agente AI (conceitual + código)

Você é arquiteto de um agente conversacional da QC. O agente usa um modelo de função (function calling) e precisa decidir quando chamar `buscar_produtos`.

**Sua tarefa:**

a) Escreva a **descrição completa** da tool no formato OpenAI Function Calling / Anthropic Tool Use:

```json
{
  "name": "buscar_produtos_qc",
  "description": "...",
  "input_schema": {
    "type": "object",
    "properties": {
      "categoria": {"type": "string", "description": "..."},
      "nome": {"type": "string", "description": "..."}
    }
  }
}
```

A descrição **deve ensinar o agente quando usar a tool**. Inclua exemplos.

b) Escreva 3 exemplos de **conversas usuário-agente** onde o agente decide chamar a tool:
   - "Tem cadeira boa para home office?"
   - "Quanto custa o Samsung S24?"
   - "Preciso de algo para café"

   Para cada, mostre: pergunta → call à tool (quais parâmetros) → resposta do agente.

c) Identifique 2 casos onde o agente **NÃO deve chamar a tool** mesmo o usuário falando de produto. Justifique.

d) **Reflexão:** Como você manteria a descrição da tool sincronizada com mudanças no endpoint? (Versionamento, contract testing, OpenAPI spec)

---

### Exercício 3.2 — Benchmark de carga

Use a ferramenta `hey` (já vem no Cloud Shell) para fazer load test na sua Function da Aula 3:

```bash
hey -n 1000 -c 50 "https://<sua-func>.azurewebsites.net/api/produtos?categoria=moveis"
```

**Reporte:**

- Latência média, p50, p95, p99
- Throughput (req/s)
- Taxa de erro
- Custo total (calcule: $0.20 per million executions + $0.000016 per GB-second)

Faça o mesmo benchmark contra o ACI da Aula 3. Compare:

| Métrica | Function | ACI |
|---------|----------|-----|
| Latência média | | |
| p95 | | |
| Throughput | | |
| Erros | | |
| Custo aprox por 1M req | | |

**Reflexão (escrever):**

a) Qual aguentou melhor a carga? Por quê?
b) Em qual cenário a Function venceria? Em qual o ACI venceria?
c) Como você arquitetaria a API da QC para suportar Black Friday (10x tráfego)?

---

### Exercício 3.3 — Pipeline CI/CD para a Function

Crie um workflow do **GitHub Actions** em `.github/workflows/deploy-function.yml` no repo privado do seu grupo que:

a) Roda em cada push para `main` que altere arquivos em `aula03/function/**`
b) Faz lint do código Python (`ruff`)
c) Roda testes (criar pelo menos 1 teste com `pytest`)
d) Faz `func azure functionapp publish` automaticamente

**Pontos extras:**

- Use OIDC para autenticar no Azure sem secrets
- Adicione um step de **slot deployment** (deploy num slot staging, troca depois)

> **Tudo via GitHub UI / github.dev** — sem instalar localmente.

---

## Critérios de entrega

A entrega é **um ZIP por grupo** (`entrega-grupo-NN-aula03.zip`) no Portal FIAP. Estrutura completa, prazo e dicas de geração do ZIP em [entregas/entrega-03/INSTRUCOES.md](../../entregas/entrega-03/INSTRUCOES.md).

| Item | Obrigatório? | Pontos máximos |
|------|--------------|----------------|
| Cabeçalho do grupo + distribuição do trabalho | ✅ Sim | 1 pt (Critério 4) |
| 🟢 N1 — Exercícios 1.1, 1.2, 1.3, 1.4 | ✅ Sim | 3 pts (Critério 1) |
| 🟡 N2 — 2.1 (segunda tool), 2.2 (App Insights), 2.3 (ACI: restart/sizing/secure env) | ✅ Sim | 3 pts (Critério 2) + 2 pts qualidade técnica (Critério 3) |
| 🔴 N3 — 3.1 (tool spec), 3.2 (benchmark), 3.3 (CI/CD) | 🎁 Bônus | até +2 pts extras |
| Reflexão coletiva ao final | ✅ Sim | 1 pt (Critério 5) |
| **Total da entrega** | | **10 pts** (10% da nota final) |

**Prazo:** 1 dia antes da Aula 4.
**Onde:** upload do ZIP no Portal FIAP. Apenas 1 membro do grupo faz o upload.
