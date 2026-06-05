---
type: concept
tags: [annotation, agreement, taxonomy, kappa, rubric, chomsky-project]
sources: 1
updated: 2026-06-05
---

# Dialogue Act Annotation Reliability

## Definition

How reliably a dialogue-act tagset can be applied, measured by inter-annotator agreement
(taxonomically-weighted Cohen's kappa) and accuracy against a gold standard. Empirically,
reliability depends heavily on **tagset granularity** and on **which dimensions** are tagged.

## How It Works

Coarser tagsets agree better: collapsing fine-grained act hierarchies into general parent acts
removes disagreement caused by subtle distinctions (Geertzen et al. 2008, DIT++→LIRICS). Some
dimensions are intrinsically hard (Turn Management, fine Feedback levels); others are reliable
(Social Obligations, coarse Task acts). Inter-annotator agreement alone *underestimates*
reliability — a gold standard is needed.

## Why It Matters (for chomsky)

- Justifies the **compact 13-act v1** taxonomy and dropping dialogue-control dimensions — these
  are the empirically reliable choices.
- The known **confusable pairs** (inform×answer×elaborate×explain; instruct×answer) directly seed
  the Plan-2 annotation rubric ("treat answer/elaborate/explain as `informar`; instruct as `pedir`").
- Motivates the teacher-mixture **agreement gate** + Claude adjudication (Plan 1/2): a gold-style
  arbiter beats raw inter-model agreement, mirroring the gold-standard finding.

## Related Concepts

- [Speech Act Label Scheme](speech-act-label-scheme.md)
- [ISO 24617-2 Dialogue Acts](iso-24617-2-dialogue-acts.md)
- Teacher-Mixture Generation Pipeline (a criar no Plano 2)

## Sources

- [Geertzen, Petukhova & Bunt (LREC 2008)](../sources/2008-geertzen-da-tagging-naive-expert.md)
