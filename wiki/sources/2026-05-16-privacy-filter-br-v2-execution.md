---
type: source
tags: [privacy-filter, v2, build-log, debugging, multi-provider, lessons-learned]
sources: 1
updated: 2026-05-16
---

# Privacy Filter BR v2 — Execution Log & Bugs Encontrados

**Período:** 2026-05-15 a 2026-05-16
**Status:** Em geração (Claude + MiniMax em paralelo, target 100k)
**Antecedentes:** v2 plan documentado em [2026-05-07](2026-05-07-privacy-filter-br-v2-plan.md)

## Sumário

Sessão de retomada do projeto após pausa de ~9 dias. Pipeline original (claude CLI subprocess) revivido, expandido com 6 categorias e-commerce + 4 templates B2B, ajustado pra multi-provider (Claude + MiniMax M2.7 em paralelo). Geração de 100k examples lançada em background. F1 de v1 era 0.97 em holdout sintético; expectativa pra v2 com mais categorias e mais dados é F1 macro ≥ 0.95.

## Decisões de Arquitetura

### 1. Multi-provider Generation
Em vez de um único LLM, rodamos Claude CLI (subscription, 3 workers) + MiniMax M2.7 (API, 5 workers) em paralelo, **mesmo output file**. Cada um apenda à mesma `data/dataset_br_v2.jsonl`. Resume baseado em `wc -l`.

Benefícios:
- 2× throughput sem dobrar consumo de Claude
- Diversidade de estilo entre LLMs (Claude vs Chinese model)
- Tolerância a falha: se um para, outro continua

Custos:
- 2 logs separados (`run_claude.log`, `run_minimax.log`)
- Estratégia de paralelismo diferente por provider

### 2. Categorias Expandidas (13 → 19)
v1 cobria PII brasileira tradicional (CPF, CNPJ, RG, etc). v2 adiciona **e-commerce/B2B**:
- `PRIVATE_ORDER_ID` (Mercado Livre, Magalu, Shopee patterns)
- `PRIVATE_TRACKING_CODE` (Correios `BR123456789BR`)
- `PRIVATE_INVOICE_NUMBER` (NF, fatura, INV)
- `PRIVATE_CLIENT_REVENUE` (valores financeiros sigilosos)
- `PRIVATE_TRANSACTION_ID` (PIX, cartão, boleto)
- `PRIVATE_CUSTOMER_ID` (IDs internos)

Output head v2: 53 → 77 classes (1 + 19×4 BIOES).

### 3. 4 Templates B2B Novos
Além dos 14 originais: `pedido_marketplace`, `dashboard_vendas`, `comprovante_delivery`, `relatorio_faturamento`. Cobre o caso "agência/consultoria mascarando dados de cliente" identificado na sessão anterior.

## Bugs Encontrados (e Resolvidos)

### Bug 1: AI4Privacy "PT" é Portugal, não Brasil

**Sintoma:** Procuramos dataset PT-BR no HuggingFace e achamos `ai4privacy/pii-masking-openpii-1m` com tag `pt`. Baixamos.

**Realidade:** os exemplos PT mostravam "Setúbal Algodeia" e "Marietherese Pourtehrani" — cidade portuguesa e nome europeu. Sem CPF/CNPJ. Distribuição era ~1% PT em 230k linhas.

**Lição:** `language: pt` no HuggingFace pode ser PT-PT OU PT-BR. Sempre validar amostras antes de baixar dataset inteiro.

### Bug 2: Dataset do arthrod é privado

**Sintoma:** Model card do arthrod referencia `arthrod/oai-pf-ptbr-chunked-v2` com 914k samples PT-BR.

**Realidade:** O dataset está marcado como `(private)` no próprio README do modelo. Não disponível via API pública. Só o benchmark de avaliação está público.

**Lição:** Verificar disponibilidade do dataset antes de planejar pipeline em torno dele. Sempre ler o "(private)" do README dos modelos.

### Bug 3: `claude --print` falha com `ANTHROPIC_API_KEY` no env

**Sintoma:** Pipeline com `python-dotenv` carregava `.env` que tinha `ANTHROPIC_API_KEY=your_key_here` (placeholder). Subprocess `claude --print` retornava `Invalid API key · Fix external API key`.

**Causa:** Claude CLI prefere variável de ambiente sobre a subscription quando ela existe. Mesmo se a chave for placeholder.

**Fix:** No subprocess invocation, fazer `env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}` e passar pro `subprocess.run(..., env=env)`.

```python
env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
result = subprocess.run(["claude", "--print"], input=prompt, env=env, ...)
```

### Bug 4: MiniMax M2.7 é reasoning model — gasta tokens em `<think>`

**Sintoma:** Configurado com `max_tokens=1024`, response chegava com `<think>...` truncado, sem conteúdo após o thinking. KeyError 'choices'.

**Causa:** M2.7 emite blocos `<think>` antes do conteúdo real. Com max_tokens baixo, o thinking consome tudo.

**Fix:**
1. `max_tokens=4096` (espaço pra thinking + answer)
2. Strip `<think>...</think>` no pós-processamento:
```python
text = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
```
3. Timeout 120s (thinking demora)

### Bug 5: MiniMax `-highspeed` não disponível no Starter plan

**Sintoma:** `MiniMax-M2.7-highspeed` retornava `usage limit exceeded, 5-hour usage limit reached for Token Plan Starter (0/0 used)`.

**Realidade:** O Starter plan literalmente tem 0/0 cota pros highspeed. Mas tem cota pros default (`MiniMax-M2.7`).

**Fix:** Default pra `MiniMax-M2.7` (sem `-highspeed`). Documentar no `.env.example`.

### Bug 6: Errors silently swallowed by generator

**Sintoma:** Pipeline rodava com 0% acceptance e não dava nenhuma pista do porquê.

**Causa:** `except Exception: return None` no `generator.py` engolia tudo.

**Fix:** `DEBUG=1` env var imprime errors com `[generator] error (template_name): TypeName: message`. Achou todos os bugs acima.

```python
except Exception as e:
    if _DEBUG:
        print(f"[generator] haiku error ({template_name}): {type(e).__name__}: {e}", file=sys.stderr)
    return None
```

## Cost & Time Reality Check

**Estimativa inicial:** 1-2 dias pra gerar 100k examples
**Realidade:** 3-4 dias com Claude + MiniMax paralelos

| Provider | Workers | Velocidade | Throughput/h | Limit |
|---|---|---|---|---|
| Claude CLI | 3 | ~7s/call | ~1.400 | Session 5h rolling |
| MiniMax M2.7 | 5 | ~30s/call (thinking) | ~600 | Plan Starter cota |
| **Combined** | 8 | - | **~2.000** | Variado |

Pra 100k: ~50 horas em condição ideal. Com pauses de session: ~70-80h.

**Lição:** Reasoning models são lentos. Pra geração em massa, vale modelo não-reasoning (mas Starter plan não dá).

## "Como Profissionais Fazem vs Nosso Approach"

Discussão honesta surgida durante o build:

**70% padrão da indústria:**
- Synthetic data + LLM augmentation (Stanford Alpaca, Vicuna)
- Auto-labeling por inserção
- BIOES tagging
- LoRA fine-tuning
- Format variants

**30% improviso por restrição:**
- Claude CLI subprocess (vs SDK profissional)
- 11k-100k samples (vs 1M-10M)
- 2 providers misturados (vs pipeline K8s)
- Colab A100 single (vs cluster de H100)

OpenAI/Google fazem o **mesmo pipeline**, só escalado 100×. Big labs iteram 10x; nós 1x. Não é "errado" — é menor.

## Pipeline State (Snapshot)

```
v1 (deployed):
  Dataset: 11.000 samples (sintético)
  Model:   ~/Downloads/privacy-filter-br-merged.zip (2.5GB)
  F1:      0.97 holdout interno (mesmo distribuição)
  Status:  Funcional, repo público

v2 (em geração):
  Target:  100.000 samples (Claude 3w + MiniMax 5w paralelo)
  Categories: 19 (era 13) — adicionado 6 e-commerce
  Templates: 18 (era 14) — adicionado 4 B2B
  Estimated finish: ~3 dias
  Output:  data/dataset_br_v2.jsonl + holdout
```

## Open Questions Updadas

- Vai o F1 do v2 melhorar significativamente sobre v1 (0.97)? Ou já saturamos?
- Categorias e-commerce vão ter F1 razoável com ~5-10k exemplos cada?
- Validação em docs B2B reais (não-sintéticos) — F1 cai pra quanto?
- Se MiniMax cota acabar, vale rotacionar pra Sonnet/Haiku via API?

## Related Wiki Pages

- [v2 Plan Original](2026-05-07-privacy-filter-br-v2-plan.md) — plano antes da execução
- [v1 Build](2026-05-06-privacy-filter-br-build.md) — o que veio antes
- [LoRA Pitfalls](../concepts/lora-fine-tuning-pitfalls.md)
- [Synthetic Data Generation](../concepts/synthetic-data-generation.md)
- [Competitive Research Discipline](../concepts/competitive-research-discipline.md)
