---
type: source
tags: [privacy-filter, brazilian-pii, lora, fine-tuning, lessons-learned, build-log]
sources: 1
updated: 2026-05-06
---

# Privacy Filter BR — Build Process & Lessons Learned

**Project:** `metricasboss/privacy-filter-br`
**Period:** 2026-05-03 to 2026-05-06
**Status:** Trained, F1 0.97 on internal holdout. Competitor `arthrod/gliner-opf-ptbr-pii-v1` discovered late.

## Summary

Built a fine-tuned version of OpenAI Privacy Filter for Brazilian PII detection (CPF, CNPJ, RG, CNH, PIS, IE, Título de Eleitor, Certidão + standard categories). Generated 11k synthetic labeled examples via 4devs API + Claude Haiku, fine-tuned with LoRA on Colab A100, achieved F1 0.97 on internal holdout.

**Late discovery:** Two competitors had already published on HuggingFace:
- `arthrod/gliner-opf-ptbr-pii-v1` (914k samples, F1 0.885 detection.span)
- `OpenMed/privacy-filter-multilingual` (multilingual including PT, F1 ~0.89)

Project shifted from "create the BR Privacy Filter" to "create a complementary specialized version for Brazilian commercial documents".

## Pipeline Architecture

```
4devs API (gerar_pessoa, gerar_cpf, gerar_cnpj, gerar_ie, etc.)
  → 8 Jinja2 templates (email, NF-e, contrato, holerite, certidão, cadastro, comunicado, relatório)
  → Claude Haiku (rewrites templates naturally)
  → Validator (verbatim span check, 5 failure modes)
  → BIOES auto-labeler
  → 11k examples (9.5MB JSONL, train + holdout)
  ↓
Privacy Filter base (1.5B / 50M active)
  → Output head replaced: 33 → 53 classes (1 + 13×4 BIOES)
  → LoRA on q_proj, v_proj (rank 16)
  → Trained 5 epochs on Colab A100 (~1.5h)
  → F1 0.97 on internal holdout
```

## Key Numbers

| Metric | Value |
|---|---|
| Training examples | 9,953 |
| Holdout examples | 1,047 |
| Total entities | 64,022 |
| Document templates | 8 |
| BR PII categories | 13 |
| Format variants per ID | 4 (formatado, raw, parcial, espaços) |
| Total params | 1.4B |
| Trainable params (LoRA + new head) | 328k (0.02%) |
| Final F1 (internal holdout) | 0.971 |
| Training cost | ~20 Colab Pro units (~$2 effective) |
| Total project time | ~3 days |

## Lessons Learned

### 1. Search HuggingFace BEFORE building
The biggest cost was discovering `arthrod/gliner-opf-ptbr-pii-v1` AFTER building. 15 minutes of HF/GitHub search before starting would have shown the competitive landscape. New rule: any model project starts with market research, not coding.

### 2. Local LLM proxies have quirks
Routing the Anthropic SDK through a local proxy (GLM 4.7) revealed:
- Streaming format differences (SSE blocks with thinking_delta vs text_delta)
- Token consumption explosion in thinking models (300 tokens vanished before any text)
- Need for raw HTTP + manual SSE parsing instead of SDK auto-parsing
- 76s/example for thinking models (vs 9.4s for non-thinking like Mixtral 8x7B)

### 3. Synthetic data quality > quantity (in narrow domains)
With 11k examples, we hit F1 0.97 on a narrow domain — same level the paper showed for 10% of SPY dataset. The 914k of arthrod's dataset is necessary for general PT-BR; for narrow commercial docs, 1-10k is sufficient.

### 4. Format variants are critical
4 variants per identifier (formatado, raw, parcial, espaços) doubled the practical robustness:
- `680.075.670-97` (formatado)
- `68007567097` (raw — sistemas em DB)
- `680.075.***-**` (parcial — sistemas de verificação)
- `680 075 670 97` (espaços)

Without all 4 in the dataset, the model fails on common real-world variants.

### 5. PEFT + CUDA gotchas
When wrapping with `get_peft_model()`:
- Always move base model `.cuda()` BEFORE `get_peft_model()` — the wrapper doesn't propagate device transfers reliably
- New head (with `ignore_mismatched_sizes=True`) needs `dtype=torch.float32` — bf16 produces NaN logits in the freshly-initialized layer
- `modules_to_save` requires the EXACT layer name — Privacy Filter calls it `score`, not `classifier`

### 6. Transformers API churn
Same training loop broke 3 times in a row:
- `evaluation_strategy` → `eval_strategy`
- `tokenizer=` → `processing_class=` in Trainer
- `warmup_ratio` deprecated, use `warmup_steps`

Need to install transformers from main for any model with `transformers_version: "5.6.0.dev0"` in config.

### 7. Disk fills fast with nohup logs
20GB nohup.out from a single training run filled the disk. Always redirect to a controlled file AND `< /dev/null` for stdin AND set up rotation.

### 8. Resume from disk > resume from memory
Wrote each example to disk on generation (with `flush()`). When the process crashed at 117 examples (no resume), ALL work was lost. After fix, resumed cleanly multiple times across power events, token outages, and disk fills.

## Comparative Analysis

| Aspect | arthrod/gliner-opf-ptbr | privacy-filter-br |
|---|---|---|
| Training data | 914k natural-text | 11k synthetic from templates |
| Categories | 73 (24 PT-BR + 47 cross) | 13 BR-specific |
| Hardware | AMD MI300X | Colab A100 |
| F1 (own benchmark) | 0.885 (5k val PT-BR) | 0.97 (internal, narrow) |
| Strengths | Person/address granularity, LGPD sensitive data | CNPJ, IE 27 states, CNH, formats parciais |
| Weaknesses | No CNPJ-specific labels, no IE state breakdown | Narrow domain (commercial docs only) |
| Reusable as-is | Yes for general PT-BR PII | Yes for BR commercial documents |

## What Got Built (Reusable Assets)

- **Dataset pipeline** (`metricasboss/privacy-filter-br/scripts/generate_dataset.py`) — reusable for any NER task in PT-BR
- **11k labeled examples** — Apache 2.0 compatible, can be released or kept private
- **Colab notebook** for fine-tuning Privacy Filter — copy-paste for next NER project
- **8 Jinja2 templates** for BR documents — extendable to 30+ types
- **Validator + auto-labeler** — domain-agnostic, works for any NER auto-labeling

## Concepts Introduced

- [Synthetic Data Generation](../concepts/synthetic-data-generation.md)
- [LoRA Fine-tuning Pitfalls](../concepts/lora-fine-tuning-pitfalls.md)
- [Specialization vs Generalization](../concepts/specialization-vs-generalization.md)
- [Competitive Research Discipline](../concepts/competitive-research-discipline.md)

## Entities Mentioned

- [4devs API](../entities/4devs-api.md)
- [Mixtral 8x7B (no-thinking)](../entities/mixtral-8x7b.md)
- [arthrod/gliner-opf-ptbr-pii-v1](../entities/arthrod-privacy-filter-ptbr.md)
- [OpenMed Privacy Filter Multilingual](../entities/openmed-privacy-filter-multilingual.md)
- [GLM 4.7 (proxy)](../entities/glm-4-7-proxy.md)

## Open Questions

- Will the model trained on 11k synthetic generalize to real-world BR commercial documents?
- Should we publish as `metricasboss/privacy-filter-br-commercial` or keep internal?
- Is there value in combining arthrod's dataset (914k) with our 11k for a hybrid model?
- For the Analytics Copilot use case, is a specialized commercial-doc model better than the general arthrod model? Need to benchmark both on actual Copilot data.
