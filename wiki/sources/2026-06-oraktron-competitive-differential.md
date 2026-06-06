---
type: source
tags: [oraktron, pragmatics, competitive-analysis, multi-axis, intention]
added: 2026-06-06
anchor: "Ma et al., Pragmatics in the Era of LLMs, ACL 2025, arXiv:2502.12378"
---

# ORAKTRON — Competitive Differential (internal doc)

Internal technical doc positioning the ORAKTRON kernel ([[oraktron-pragmatic-os]] Layer 3) against
peers. Diagnosis from a literature review (ACL Anthology, arXiv cs.CL, LREC, commercial docs).

## The claim

No direct competitor decomposes an arbitrary sentence into 14+ pragmatic dimensions **in one
structured pass and crosses them to reconstruct intention**. The field is **siloed** — one
classifier per phenomenon. Anchor survey (Ma et al., ACL 2025) states pragmatic tasks "are designed
in isolation, making it hard to evaluate holistic pragmatic competence." Genuine vacuum, not a
graveyard: nobody tried to unify (each phenomenon had its own community/dataset; reliable structured
output via JSON Schema only became commodity Aug 2024; multi-axis prompts cause "prompt overload").

## Competitor map (three groups)

- **A — many dims but not pragmatic** (lexical/statistical): LIWC-22 (117 cats), Receptiviti (200+),
  Biber MDA (6 register dims), IBM Watson NLU (10 features), Hume AI (53 text, API sunset 2026-06-14).
  Count lexicon / one feature at a time; no composition, no intent.
- **B — real pragmatics but one axis at a time** (SOTA silos, each likely beats ORAKTRON on its axis):
  ISO 24617-2 / DIT++ (acts, dialogue-only — **this is the atos de fala axis**), FactBank
  (evidentiality), MPQA (subjectivity), Appraisal Theory (evaluation), Stanford Politeness (social
  deixis), VU Amsterdam Metaphor (tropes), Stab & Gurevych (argumentation), PDTB 3.0 (discourse
  relations), *SEM 2012 (negation), IMPPRES (presupposition), SemEval-2020 Task 11 (manipulation).
- **C — LLM era, broader but still < 14 axes**: PUB (4 phenomena/14 tasks, not one-pass), DiPlomat,
  MultiPragEval (5 Gricean maxims). **SOTA ceiling for breadth-in-one-pass = 5 dims.** ORAKTRON
  proposes 14 + TROP + CTX.

## Differential in one line

Not depth-per-axis (silos win each axis) but **compositional integration**: 16 fields on the same
sentence, crossed to reconstruct intention. The sum of silos doesn't track intention; the crossing does.

## Engineering implications (→ [[layered-pragmatic-axes]])

- **Orthogonal annotation** — one sentence gets a value on every axis (not mutually exclusive);
  opposite of SWBD-DAMSL, follows DIT++.
- **Ground-truth per public benchmark, axis by axis** — run on samples (MPQA→SS, FactBank→EV,
  VUA→TROP, Stanford Politeness→DS, Persuasive Essays→A); accept an axis at **≥70% of the dedicated
  SOTA F1**, else fall back to a purely architectural claim on that axis.
- **Compositional cases (≥50)** where intent emerges only from crossing 3+ dims (e.g. polite
  offensive irony = presupposition + trope + appraisal) — **the most valuable asset**, above raw volume.
- **Trust architecture** — separate LLM classification from deterministic server-side aggregation/
  validation (we already do this in the `collect` pipeline). Single output JSON Schema (16 fields).
- **Prompt overload** — multi-axis prompts degrade; consider blocks of correlated dims + deterministic
  aggregation.

## Honest caveats (from the doc)

Compositional differential is **hypothesis, not demonstrated fact** without the benchmark numbers +
the 50 cases. Silos likely win each isolated axis — don't sell depth-per-axis. "Tracking intention"
is a claim Speech Act Theory / DIT++ already make narrowly; ORAKTRON differentiates by inferring
*which formal-semantic intention generated this form* via multidimensional decomposition. Absence of a
direct competitor is strong but not conclusive (proprietary systems may not publish). **Priority
action: deposit a dated preprint before any commercial move — the vacuum isn't yours until it's dated.**
