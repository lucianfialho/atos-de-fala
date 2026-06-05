---
type: concept
tags: [synthetic-data, teacher-student, distillation, speech-acts, chomsky-project]
sources: 0
updated: 2026-06-05
---

# Teacher-Mixture Generation Pipeline

## Definition

The synthetic-data pipeline for the speech-act classifier: a **bulk teacher** (MiniMax *or*
DeepSeek, via `--provider`) generates PT-BR text + span annotations; an **adjudicator**
(`--adjudicator`: DeepSeek-reasoner, Claude, or `none`) re-annotates a sampled fraction and fixes
disagreements/invalid cases. Only validated,
high-agreement-or-adjudicated examples reach the training JSONL. The student (BERTimbau, Plan 3)
distills the result.

## Per-act balancing

Unsteered generation skews to common acts (`informar`), starving rare ones. The CLI counts spans
per act so far (`chomsky.gen.balance.act_counts`) and, each round, injects the most
under-represented acts (`under_target_acts`, target ≈ n/num_acts) as a FOCUS hint in the
generation prompt — pushing the dataset toward an even per-act distribution. Disable with
`--no-balance`. This directly counters the imbalance that capped Porttinari's macro-F1 at 0.295.

## How It Works

Per example (pure function `chomsky.gen.pipeline.process_example`): resolve quotes→offsets →
validate against the taxonomy → if invalid, Claude adjudicates or the example is rejected →
on a sampled fraction, Claude cross-annotates and span-F1 agreement is measured → keep if
≥ threshold, else adjudicate or reject. API I/O is isolated in thin clients; orchestration is
pure (injected callables), so it is fully unit-tested offline. Generation runs in concurrent waves
(`--concurrency N`, default 1): N requests in flight, results collected on the main thread (writes +
counters serialized, no locks). I/O-bound, so ~N× faster wall-clock; balancing focus is recomputed
per wave.

## Why It Matters

Teacher quality is the ceiling on the student. The agreement gate + adjudication protect label
quality at low cost: cheap bulk (DeepSeek is ~$1-3 for 10k examples; MiniMax also cheap), a
stronger adjudicator only where it matters. **DeepSeek-only** (chat bulk + reasoner adjudicator)
needs no Anthropic key — cheaper but a same-family check is weaker than a cross-family one (Claude);
the hard validator (taxonomy/verbatim/non-overlap) backstops either way. Reuses the Privacy Filter
BR lessons (resume-from-disk with fsync; reasoning-model gotchas).

## Related Concepts

- [Synthetic Data Generation](synthetic-data-generation.md)
- [Multi-Provider Generation](multi-provider-generation.md)
- [Speech Act Label Scheme](speech-act-label-scheme.md)

## Sources

- Design spec: `docs/superpowers/specs/2026-06-04-speech-act-span-classifier-design.md`
- Plan: `docs/superpowers/plans/2026-06-04-generation-pipeline.md`
