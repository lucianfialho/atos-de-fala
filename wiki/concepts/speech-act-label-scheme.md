---
type: concept
tags: [speech-acts, bioes, labels, annotation, iso-24617-2, atos-project]
sources: 1
updated: 2026-06-05
---

# Speech Act Label Scheme (PT-BR)

## Definition

The BIOES label set for span-level speech-act classification. Derived mechanically from
`config/taxonomy.yaml`: for N acts, labels = `O` plus `{B,I,E,S}×acts` = `4N+1` classes.
**Frozen v1 (2026-06-05): 13 acts → 53 labels**, grounded in ISO 24617-2 (Bunt et al., LREC
2012) general-purpose + Social Obligations functions, mapped to Searle's 5 classes, and adapted
for open PT-BR text (dialogue-control dimensions out of scope for v1).

## How It Works

`atos.taxonomy.bioes_labels(acts)` emits `O` first, then `B-/I-/E-/S-` per act in config
order. `label_maps` gives contiguous `label2id`/`id2label`. Non-overlapping spans only (v1).

## The 13 acts (act — ISO function — Searle class)

- `informar` — Inform — assertivo
- `perguntar` — Question — diretivo
- `concordar` — Agreement — assertivo/expressivo
- `discordar` — Disagreement — assertivo/expressivo
- `pedir` — Request/Instruct — diretivo
- `sugerir` — Suggestion — diretivo
- `oferecer` — Offer — comissivo
- `prometer` — Promise — comissivo
- `saudar` — Greeting — expressivo (social)
- `agradecer` — Thanking — expressivo (social)
- `desculpar` — Apology — expressivo (social)
- `despedir` — Valediction — expressivo (social)
- `expressar_emocao` — (sentiment) — expressivo

## Why It Matters

Same architectural shape as the Privacy Filter BR head (PII → speech acts) — 53 labels, like
that project. Swapping or refining the taxonomy is a config change, not a code change.

## Related Concepts

- [ISO 24617-2 Dialogue Acts](iso-24617-2-dialogue-acts.md)
- [Speech Act Theory](speech-act-theory.md)
- [BIOES Tagging](bioes-tagging.md)
- [Token Classification](token-classification.md)
- [LoRA Fine-tuning Pitfalls](lora-fine-tuning-pitfalls.md)

## Sources

- [ISO 24617-2 (Bunt et al., LREC 2012)](../sources/2012-iso-24617-2-bunt-lrec.md)
- Design spec: `docs/superpowers/specs/2026-06-04-speech-act-span-classifier-design.md`
