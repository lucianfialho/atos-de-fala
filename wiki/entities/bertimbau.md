---
type: entity
tags: [bertimbau, bert, portuguese, token-classification, model, atos-project]
sources: 1
updated: 2026-06-05
---

# BERTimbau

## What It Is

A family of monolingual BERT models pre-trained on Brazilian Portuguese (brWaC corpus) by
neuralmind (Unicamp). The canonical starting point for PT-BR NLP fine-tuning. The atos student
model fine-tunes `neuralmind/bert-base-portuguese-cased` as a BIOES speech-act token classifier.

## Significance

First high-quality monolingual BERT for Brazilian Portuguese; beats multilingual BERT on all
evaluated tasks. Cased, PT-specific vocab (~29.8k WordPiece) gives better subword segmentation
than mBERT for PT-BR. Used as the backbone in Plan 3.

## Key Facts

| Property | Base | Large |
|---|---|---|
| HF ID | `neuralmind/bert-base-portuguese-cased` | `neuralmind/bert-large-portuguese-cased` |
| Layers / hidden / heads | 12 / 768 / 12 | 24 / 1024 / 16 |
| Params | 110M | ~330M |
| Vocab | 29,794 cased WordPiece | same |
| Max tokens | 512 | 512 |
| Training corpus | brWaC (2.68B tokens) | same |
| MiniHAREM NER F1 (5-cls) | 83.1 | 83.7 |
| License | MIT | MIT |

- Token-cls usage: fast tokenizer (`return_offsets_mapping=True`) for subword→span alignment.
- For LoRA, the BERT head is `classifier` and attention projections are `query`/`value`
  (differs from Privacy Filter BR's `score` / `q_proj`/`v_proj`). See [LoRA Fine-tuning Pitfalls](../concepts/lora-fine-tuning-pitfalls.md).

## Sources

- [BERTimbau (Souza et al., BRACIS 2020)](../sources/2020-bertimbau-souza.md)
- HF model card: https://huggingface.co/neuralmind/bert-base-portuguese-cased
