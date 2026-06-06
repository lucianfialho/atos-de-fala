---
type: source
tags: [bertimbau, bert, portuguese, pretraining, ner, atos-project]
sources: 1
updated: 2026-06-05
---

# BERTimbau: Pretrained BERT Models for Brazilian Portuguese

**Authors:** Fábio Souza, Rodrigo Nogueira, Roberto Lotufo
**Venue / Year:** BRACIS 2020 (Springer LNAI 12319)
**URL:** https://link.springer.com/chapter/10.1007/978-3-030-61377-8_28 (paper PDF paywalled)
**HF:** https://huggingface.co/neuralmind/bert-base-portuguese-cased
**Raw:** `raw/sources/2020-bertimbau-hf-modelcard.md` (HF model card snapshot)

## Summary

Introduces BERTimbau, the first monolingual BERT for Brazilian Portuguese, trained on the brWaC
web corpus. Base and Large variants beat multilingual BERT on NER, STS, and RTE, setting SOTA on
Portuguese NER (HAREM/MiniHAREM).

## Key Takeaways

- Corpus: brWaC — 2.68B tokens, 3.53M documents (17.5GB).
- Pre-training: 1M steps, whole-word masking MLM + NSP, max length 512.
- Vocab: 29,794 cased WordPiece. Base 110M / Large ~330M params.
- MiniHAREM NER F1 (5-class): Large 83.7, Base 83.1 (mBERT 79.2).
- MIT license; `neuralmind/bert-base-portuguese-cased` / `-large-`.

## Relevance to atos

- The student backbone for Plan 3 (BIOES speech-act token classifier).
- Confirms strong PT-BR token-classification capability to fine-tune from.
- The broader PT-BR NLP search found **no public span-level speech-act dataset** — validating the
  synthetic teacher-mixture approach (Plan 2).

## Concepts Introduced

- BERTimbau LoRA Token Classification — a ser criado no Plano 3 (`docs/superpowers/plans/2026-06-04-training-eval.md`)

## Entities Mentioned

- [BERTimbau](../entities/bertimbau.md)
