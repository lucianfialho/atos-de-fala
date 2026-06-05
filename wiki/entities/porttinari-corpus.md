---
type: entity
tags: [corpus, portuguese, speech-acts, dataset, holdout, chomsky-project]
sources: 1
updated: 2026-06-05
---

# Porttinari speech-act corpus

## What It Is

The first Brazilian-Portuguese corpus annotated with speech acts (da Silva, Roman, Di Felippo,
PROPOR 2024): a 50% sample of Porttinari-base news — **536 news, 4,091 sentences** — each sentence
labeled with one ISO 24617-2 communicative function. Creative Commons license.
Repo: https://github.com/natalypatti/porttinari-base-speech-acts
Local copy (CC, vendored): `raw/porttinari-base-speech-acts/` — annotation CSV at
`data/porttinari-annotated-sample-paper-v1-20231211.csv` (columns: `sentence`, `speech_act`, …).

## Significance

- **Real (human-annotated) PT-BR holdout** for chomsky's Plan-3 evaluation — satisfies the spec's
  "real-text holdout" requirement without us having to annotate one from scratch.
- Validates the chomsky taxonomy (same ISO basis; ~13 ML classes; labels map onto ours).
- Documents the natural class distribution (inform 91%), which is *why* we generate balanced
  synthetic data instead of relying on natural text.

## Key Facts

- Genre: journalistic (news); standard-norm PT-BR; UD PoS tags available.
- Granularity: **sentence-level** (one act/sentence) — chomsky is span-level, so direct use is as
  a sentence-level eval (map our spans → sentence label) or as seed text for annotation.
- Class counts (Table 4): inform 3725, question 96, suggest 64, disagreement 62, disconfirm 26,
  compliment 24, answer 22, instruct 18, thanking 13, sympathy 11, request 7, confirm 6, promise 6,
  (correction/agreement/congratulation/apology ≤4).
- 13 classes usable after dropping rare ones for ML.
- Converter: `chomsky.train.porttinari` maps the CSV → chomsky JSONL (whole-sentence spans, labels
  mapped to our 13 acts; all 4091 rows map, 0 unmapped). Run:
  `python -m chomsky.train.porttinari --out data/porttinari-holdout.jsonl`. Eval against it reads as
  a sentence-level signal (our spans are finer than whole-sentence gold).

## Sources

- [Porttinari speech-acts (PROPOR 2024)](../sources/2024-porttinari-speech-acts-propor.md)
