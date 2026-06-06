---
type: source
tags: [dialogue-acts, dit++, lirics, annotation, agreement, taxonomy, atos-project]
sources: 1
updated: 2026-06-05
---

# Evaluating Dialogue Act Tagging with Naive and Expert Annotators

**Authors:** Jeroen Geertzen, Volha Petukhova, Harry Bunt (Tilburg University)
**Venue / Year:** LREC 2008
**Raw:** `raw/sources/2008-geertzen-da-tagging-naive-expert.pdf`

## Summary

Compares dialogue-act annotation by naive vs. expert annotators on task-oriented Dutch dialogue,
using the **DIT++** tagset (the predecessor of ISO 24617-2). Measures inter-annotator agreement
(taxonomically-weighted kappa) and accuracy against a gold standard, per dimension, and studies
the effect of **reducing tagset granularity** (collapsing DIT++ hierarchies to the coarser LIRICS
acts).

## Key Takeaways (and what they validate for atos)

- **Coarser tagset → higher agreement.** Collapsing fine-grained hierarchies (DIT++ → LIRICS)
  raised κ, especially for non-experts (e.g. auto-feedback 0.36→0.71 naive). **Validates our
  compact 13-act v1** over full ISO granularity. "On less complex tagsets the difference between
  naive and expert annotators becomes smaller."
- **Hard-to-annotate dimensions:** Turn Management (low κ for *both* groups; guidelines unclear),
  Feedback (naive struggle to pick the feedback level). **Validates dropping turn/time/feedback
  dimensions from v1.**
- **Reliable dimensions:** Social Obligations Management (κ ~0.91–0.94) and Task with coarse acts
  (~0.82–0.90 expert). **These are exactly the dimensions our 13 acts keep.**
- **Confusable act pairs (even for experts):** INFORM×ELABORATE, INFORM×WH-ANSWER,
  INFORM×EXPLAIN, INSTRUCT×WH-ANSWER. **Supports our merges** (answer/elaborate/explain → `informar`;
  Instruct → `pedir`) and seeds the Plan-2 annotation rubric's "do not confuse" guidance.
- **LIRICS coarse mapping (Fig. 3):** inform/uncertain-inform/clarify/elaborate/exemplify/explain/
  justify → **inform**; WHQ/HQ → set question; YNA → propositional answer; correction → disagreement.
  A coarse GPF inventory close to ours.
- **Methodology:** inter-annotator agreement *underestimates* reliability vs. a gold standard;
  distinguish "agreement on whether to annotate a dimension" from "agreement on the function".
  Informs the Plan-1 agreement gate + the need for Claude-adjudicated gold.

## Concepts Introduced

- [Dialogue Act Annotation Reliability](../concepts/dialogue-act-annotation-reliability.md)

## Entities Mentioned

- [ISO 24617-2 / DiAML](../entities/iso-24617-2.md) (DIT++ is its basis; DAMSL the lineage)
