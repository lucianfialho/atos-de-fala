---
type: source
tags: [speech-acts, portuguese, bertimbau, iso-24617-2, corpus, class-imbalance, atos-project]
sources: 1
updated: 2026-06-05
---

# Bringing Pragmatics to Porttinari — Adding Speech Acts to News Texts

**Authors:** Nataly L. P. da Silva, Norton T. Roman (EACH/USP), Ariani Di Felippo (UFSCar)
**Venue / Year:** PROPOR 2024
**Raw:** `raw/sources/2024-porttinari-speech-acts-propor.pdf`
**URL:** https://aclanthology.org/2024.propor-1.14
**Corpus (CC):** https://github.com/natalypatti/porttinari-base-speech-acts

## Summary

The closest prior work to atos: builds the **first PT-BR corpus annotated with speech acts**
(a 50% sample of Porttinari-base news: 536 news / 4,091 sentences), using an **adapted ISO 24617-2**
taxonomy, and fine-tunes **BERTimbau-large** to classify them. Annotation is **sentence-level**
(one act per sentence) — not span-level, so atos's per-span granularity remains novel.

## Key Takeaways

- **A reusable PT-BR speech-act corpus exists** (CC license) → ideal **real-text holdout** for our
  Plan-3 evaluation. Their labels map cleanly onto our act names (inform→`informar`, question→
  `perguntar`, suggest→`sugerir`, disagreement→`discordar`, request→`pedir`, promise→`prometer`,
  thanking→`agradecer`, instruct→`pedir`, apology→`desculpar`…).
- **Taxonomy convergence:** they use ISO 24617-2 and ended with **13 ML classes** — strongly
  validates our 13-act v1. Extra distinctions they kept: `confirm`/`disconfirm`, `compliment`,
  `congratulation`, `sympathy-expression`, `answer` (we fold these into concordar/discordar /
  expressar_emocao / informar — candidates for a future v2).
- **Severe class imbalance is the core difficulty:** in news, `inform` = **91%** of sentences.
  Weighted-F1 reached 92% but **macro-F1 only 29.5%**; rare classes (answer, thanking, request,
  promise, confirm) scored **F1 = 0** for lack of examples. **This is the strongest argument for
  our synthetic teacher pipeline:** we *control* the class distribution and can balance rare acts —
  exactly what natural corpora cannot.
- **Rubric rules (adopt in Plan 2):**
  - Use the **most specific** applicable act (e.g. "Isso é uma vergonha" → `discordar`, not `informar`).
  - **Describing an act ≠ performing it:** "Vettel pediu desculpas à equipe" is `informar` (reports
    an apology), NOT `desculpar`.
  - Multifunctionality exists (inform+suggest in one sentence); span-level lets us assign different
    acts to different spans instead of forcing one.
- Setup: BERTimbau-large, Colab T4, batch 32, ≤5 epochs, inverse-frequency class weights.

## Concepts Introduced

- [Dialogue Act Annotation Reliability](../concepts/dialogue-act-annotation-reliability.md)
- [Speech Act Label Scheme](../concepts/speech-act-label-scheme.md)

## Entities Mentioned

- [Porttinari speech-act corpus](../entities/porttinari-corpus.md)
- [BERTimbau](../entities/bertimbau.md)
- [ISO 24617-2 / DiAML](../entities/iso-24617-2.md)
