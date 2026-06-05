---
type: concept
tags: [bertimbau, lora, token-classification, speech-acts, chomsky-project]
sources: 0
updated: 2026-06-04
---

# BERTimbau LoRA Token Classification

## Definition

The student model: BERTimbau (`neuralmind/bert-base-portuguese-cased`) fine-tuned with LoRA as a
BIOES token classifier over the speech-act label set. Trained on the Plan-2 synthetic dataset;
evaluated with span-level F1.

## How It Works

`build_model` wires `num_labels`/id maps from the taxonomy; `apply_lora` targets BERT's
`query`/`value` projections and fully trains the `classifier` head (modules_to_save). Features:
char-span annotations → fast-tokenizer offsets → `char_spans_to_bioes` → label ids (-100 on
special tokens). Inference: argmax tags → `bioes_tags_to_spans` → char-offset spans → span-F1.

## Why It Matters

Distills the teacher mixture into a cheap, fast, self-hostable model. Reuses Plan-1 tagger/eval
and Plan-2 data. The BERT-specific names (`classifier`, `query`/`value`) differ from Privacy
Filter BR (`score`, `q_proj`/`v_proj`) — the exact-name pitfall.

## Related Concepts

- [LoRA Fine-tuning Pitfalls](lora-fine-tuning-pitfalls.md)
- [Speech Act Label Scheme](speech-act-label-scheme.md)
- [Teacher-Mixture Generation Pipeline](teacher-mixture-pipeline.md)

## Sources

- Plan: `docs/superpowers/plans/2026-06-04-training-eval.md`
- Colab: `docs/colab/train_bertimbau_lora.md`
