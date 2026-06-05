---
type: concept
tags: [speech-acts, bioes, labels, annotation, chomsky-project]
sources: 0
updated: 2026-06-04
---

# Speech Act Label Scheme (PT-BR)

## Definition

The BIOES label set for span-level speech-act classification. Derived mechanically from
`config/taxonomy.yaml`: for N acts, labels = `O` plus `{B,I,E,S}×acts` = `4N+1` classes.
Provisional taxonomy (12 acts → 49 labels), to be frozen in Phase 1 from the papers.

## How It Works

`chomsky.taxonomy.bioes_labels(acts)` emits `O` first, then `B-/I-/E-/S-` per act in config
order. `label_maps` gives contiguous `label2id`/`id2label`. Non-overlapping spans only (v1).

## Provisional acts

afirmar, perguntar, pedir, sugerir, prometer, agradecer, concordar, discordar, saudar,
despedir, informar, expressar_emocao.

## Why It Matters

Same architectural shape as the Privacy Filter BR head (PII → speech acts). Swapping the
taxonomy is a config change, not a code change.

## Related Concepts

- [BIOES Tagging](bioes-tagging.md)
- [Token Classification](token-classification.md)
- [LoRA Fine-tuning Pitfalls](lora-fine-tuning-pitfalls.md)

## Sources

- Design spec: `docs/superpowers/specs/2026-06-04-speech-act-span-classifier-design.md`
