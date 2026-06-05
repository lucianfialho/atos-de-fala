---
type: concept
tags: [synthetic-data, teacher-student, distillation, speech-acts, chomsky-project]
sources: 0
updated: 2026-06-04
---

# Teacher-Mixture Generation Pipeline

## Definition

The synthetic-data pipeline for the speech-act classifier: MiniMax (bulk teacher) generates
PT-BR text + span annotations; Claude (adjudicator) re-annotates a sampled fraction and fixes
disagreements/invalid cases. Only validated, high-agreement-or-adjudicated examples reach the
training JSONL. The student (BERTimbau, Plan 3) distills the result.

## How It Works

Per example (pure function `chomsky.gen.pipeline.process_example`): resolve quotes→offsets →
validate against the taxonomy → if invalid, Claude adjudicates or the example is rejected →
on a sampled fraction, Claude cross-annotates and span-F1 agreement is measured → keep if
≥ threshold, else adjudicate or reject. API I/O is isolated in thin clients; orchestration is
pure (injected callables), so it is fully unit-tested offline.

## Why It Matters

Teacher quality is the ceiling on the student. The agreement gate + adjudication protect label
quality at low cost: cheap bulk from MiniMax, expensive Claude only where it matters. Reuses the
Privacy Filter BR lessons (resume-from-disk with fsync; MiniMax reasoning gotchas).

## Related Concepts

- [Synthetic Data Generation](synthetic-data-generation.md)
- [Multi-Provider Generation](multi-provider-generation.md)
- [Speech Act Label Scheme](speech-act-label-scheme.md)

## Sources

- Design spec: `docs/superpowers/specs/2026-06-04-speech-act-span-classifier-design.md`
- Plan: `docs/superpowers/plans/2026-06-04-generation-pipeline.md`
