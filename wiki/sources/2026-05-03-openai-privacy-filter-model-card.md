---
type: source
tags: [privacy-filter, pii, token-classification, fine-tuning, lora, bioes, model-card]
sources: 1
updated: 2026-05-03
---

# OpenAI Privacy Filter — Model Card (April 22, 2026)

**URL:** https://cdn.openai.com/pdf/c66281ed-b638-456a-8ce1-97e9f5264a90/OpenAI-Privacy-Filter-Model-Card.pdf
**Raw:** `raw/sources/2026-05-03-openai-privacy-filter-model-card.pdf`
**Type:** Technical paper / model card (21 páginas)
**Date ingested:** 2026-05-03

## Summary

Model card oficial do Privacy Filter da OpenAI. Detalha arquitetura, processo de treinamento, taxonomia de labels, benchmarks e fine-tuning efficiency. A fonte mais importante para o projeto Privacy Filter BR — define exatamente como replicar e adaptar o modelo.

## Key Takeaways

### Fine-tuning efficiency (Table 2 — SPY dataset)

| Train Fraction | Best Epoch | F1 (tokens) |
|---|---|---|
| 0% (zero-shot) | 0 | 0.545 |
| 1% | 13 | 0.879 |
| **10%** | **39** | **0.962** ← satura aqui |
| 50% | 18 | 0.983 |

> "Training on 10% of the dataset is enough to drive F1 scores above 96% and nearly saturates the benchmark."

**Implicação para Privacy Filter BR:** 10k exemplos bem curados provavelmente atingem F1 > 0.96. Não precisa de 50k.

### Como os dados sintéticos foram construídos

> "Synthetic privacy datasets were constructed from public datasets by applying **format-matching augmentation** to increase subtype and surface-form diversity, **inserting the resulting spans into a natural context**, and running **automated quality controls** that removed examples with missing target spans, extraneous spans, or formatting failures."

Exatamente o pipeline que usaremos: 4devs gera spans → Haiku insere em contexto → validação automática remove exemplos com spans faltando.

### Anotação com modelo frontier

> "In cases where ground truths were missing for publicly available data, we used a frontier model in the GPT-5 family for annotation with a 2x2 protocol: two prompt formats × two reasoning settings (medium and high)."

Para o BR, nosso auto-labeling é mais simples e mais confiável: inserimos os spans programaticamente, então sempre sabemos onde estão.

### CLI `opf` para fine-tuning

O Privacy Filter tem um CLI próprio chamado `opf`:
```bash
# Fine-tuning
opf train --output-dir finetuned/ dataset.jsonl

# Inferência com redação
opf redact "texto com PII"

# Inferência com labels coloridos
opf redact --output-mode annotated "texto com PII"

# Ajuste do operating point (precision vs recall)
opf redact -help  # ver opções do decoder Viterbi
```

**Implicação:** Não precisamos implementar o loop de treinamento manualmente. O `opf train` aceita um `dataset.jsonl` e faz o fine-tuning. Fase 2 do projeto fica muito mais simples.

### Formato do dataset.jsonl para fine-tuning

Baseado no model card, o formato aceito pelo `opf train` é JSONL com BIOES span annotations. A estrutura exata precisa ser confirmada via `opf train --help`.

### Arquitetura (confirmada)

- **Base:** checkpoint autorregressivo similar ao gpt-oss, adaptado para classificador bidirecional
- **Atenção:** Banded attention, band size 128 (janela efetiva: 257 tokens)
- **FFN:** Sparse Mixture-of-Experts, 128 experts, top-4 routing
- **Output:** 33 classes = 1 background (O) + 8 categorias × 4 tags BIOES
- **d_model:** 640
- **Blocos:** 8 transformer blocks

### Benchmark: PII-Masking-300k

O modelo **não foi treinado** no training split do PII-Masking-300k. Apenas avaliado no test split.

Resultados:
- Baseline: F1 tokens = 0.960, F1 spans = 0.926
- Corrected: F1 tokens = 0.974, F1 spans = 0.942

### Multilingual (importante para BR)

O paper avalia multilingual performance e menciona que há variação entre línguas. Português não é mencionado explicitamente como língua bem representada — confirma a necessidade do Privacy Filter BR.

### Clue Position (insight para templates)

> "Influence of the Category Clue Position": o modelo performa melhor quando o contexto que identifica o tipo de PII está próximo do valor.

**Implicação para templates BR:** incluir sempre o "clue" próximo ao valor:
- ✅ "CPF 680.075.670-97" (clue antes)
- ✅ "680.075.670-97 (CPF)" (clue depois)
- ⚠️ "680.075.670-97" sozinho (sem clue — performa pior)

Mas também incluir exemplos sem clue para robustez.

## Conceitos Confirmados/Atualizados

- [BIOES Tagging](../concepts/bioes-tagging.md) — confirmado: 33 classes = 1 + 8×4
- [Viterbi Decoding](../concepts/viterbi-decoding.md) — confirmado: constrained Viterbi com linear-chain scoring
- [Fine-tuning Efficiency](../concepts/fine-tuning-efficiency.md) — confirmado: 10% satura em F1 0.962
- [Token Classification](../concepts/token-classification.md) — confirmado: banded attention, forward pass único

## Entidades Mencionadas

- [OpenAI Privacy Filter](../entities/openai-privacy-filter.md)
- [opf CLI](../entities/opf-cli.md) — CLI para inferência e fine-tuning do Privacy Filter
- [PII-Masking-300k Benchmark](../entities/pii-masking-300k.md)
- [SPY Dataset](../entities/spy-dataset.md) — dataset sintético de consultas médicas/legais usado no fine-tuning eval
