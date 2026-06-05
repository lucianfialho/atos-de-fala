---
type: entity
tags: [model, competitor, pii, multilingual, privacy-filter, fork]
sources: 1
updated: 2026-05-06
---

# OpenMed/privacy-filter-multilingual

## What It Is

Multilingual fine-tune of OpenAI Privacy Filter covering 16 languages including Portuguese. Published by OpenMed organization. Apache 2.0.

## Significance

The first multilingual extension of Privacy Filter. Includes Portuguese (mixed PT-BR and PT-PT) but no specialization for any single market. Trained on AI4Privacy datasets (general PII, no Brazilian commercial documents).

## Key Facts

- **Base:** openai/privacy-filter (1.4B params, 50M active per token, MoE)
- **Languages (16):** Arabic, Bengali, Chinese, Dutch, English, French, German, Hindi, Italian, Japanese, Korean, **Portuguese**, Spanish, Telugu, Turkish, Vietnamese
- **Categories:** 54 PII types (217 BIOES classes = 1 + 54×4)
- **Training data:** AI4Privacy mix — `pii-masking-200k`, `pii-masking-400k`, `open-pii-masking-500k-ai4privacy`
- **Recipe:** `opf train` (official CLI), full fine-tune, 5 epochs, bf16, balanced language sampling
- **License:** Apache 2.0
- **Downloads:** ~5.5k (as of 2026-05-06)

## Brazilian Coverage

The Portuguese examples mix BR and PT-PT. Sample widget data shows European Portuguese ("Lisboa"). Brazilian-specific PII (CPF, CNPJ, IE) is detected as generic `account_number` or `government_id`, not specific labels.

## Variants Available

- `OpenMed/privacy-filter-multilingual` — PyTorch, full
- `OpenMed/privacy-filter-multilingual-mlx` — Apple Silicon BF16
- `OpenMed/privacy-filter-multilingual-mlx-8bit` — Apple Silicon quantized

## Strategic Position

Best when you need:
- Multiple languages in one model
- General PII coverage without country-specific specialization
- Apple Silicon deployment (via MLX variant)

Not the right choice if:
- You need granular Brazilian categories (CNPJ, IE, CNH separately)
- You're processing only PT-BR text
- You need partial format detection (`123.456.***-**`)

## Sources

- [Privacy Filter BR Build](../sources/2026-05-06-privacy-filter-br-build.md)
- HuggingFace: https://huggingface.co/OpenMed/privacy-filter-multilingual
