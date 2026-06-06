---
type: synthesis
tags: [language-models, fine-tuning, training, speech-acts, ner, oraktron]
sources: 13
updated: 2026-06-06
---

# Overview — atos (atos de fala)

## Thesis (defined 2026-06-05)

**atos** (atos de fala) builds a span-level **speech-act classifier** for **PT-BR**: it decomposes
open text into non-overlapping spans and labels each with a speech act (intent). The model is
BERTimbau fine-tuned with LoRA as a BIOES token classifier, distilled from an LLM teacher mixture
(Claude rubric/gold + MiniMax bulk, agreement-gated). The taxonomy (13 acts → 53 labels) is
grounded in ISO 24617-2 + Searle (pragmatics), not in Chomsky's syntax. See
[Chomsky vs Pragmatics](concepts/chomsky-vs-pragmatics.md).

Below the thesis sits the portable, hard-won knowledge seeded from the `myFirstSmallModel` wiki
(SLM-from-scratch + Privacy Filter BR fine-tuning), which the architecture reuses 1:1
(token classification, BIOES, LoRA, synthetic data).

## Fase 0 — key findings (2026-06-05)

- **Unit of annotation is the "functional segment"** (ISO 24617-2): a minimal stretch carrying
  one or more communicative functions — the grounding for span-level tagging.
- **Taxonomy frozen at 13 acts / 53 labels** from ISO 24617-2 general-purpose + social-obligation
  functions, mapped to Searle, adapted for open text (dialogue-control dimensions dropped).
- **A PT-BR speech-act corpus exists but only at sentence level** — the Porttinari speech-act
  corpus (da Silva et al., PROPOR 2024; ISO-based, CC). No *span-level* PT-BR dataset exists, so our
  granularity is novel; and the Porttinari corpus becomes our **real-text holdout** for Plan-3 eval.
- **Class imbalance is the killer, and synthetic data is the answer:** in natural news, `inform`
  is 91% of sentences → Porttinari's BERTimbau hit 92% weighted-F1 but only **29.5% macro-F1**, with
  rare acts at F1=0. Our teacher pipeline *controls* the distribution, balancing rare acts that
  natural corpora cannot. This is the strongest justification for the synthetic approach.
- **PT-BR pragmatics notes for annotation:** indirect requests ("você poderia…?" = `pedir`) and
  diminutive softeners ("um minutinho") — captured in the rubric, not as labels.
- **Compact tagset is the reliable choice** (Geertzen et al. 2008): coarser DA tagsets get higher
  inter-annotator agreement; Turn/Feedback dimensions are unreliable. Confirms the 13-act v1 and
  the dropped dimensions. Known confusable pairs (inform×answer×elaborate×explain; instruct×answer)
  → seed the Plan-2 rubric's disambiguation guidance.

## Fase 2–3 — deployment & collection (2026-06-06)

- **Model shipped and merged.** LoRA adapter merged into BERTimbau → standalone token
  classifier, exported to **ONNX int8** (~109MB) and published to Hugging Face:
  model [`lucianfialho/atos-de-fala-ptbr`], dataset [`lucianfialho/atos-de-fala-ptbr-dataset`]
  (CC BY). Runs **in the browser** via Transformers.js/WebGPU (dtype q8), wasm fallback.
- **Dataset v1 (synthetic):** 5086 examples, 15816 spans, 3.11 spans/ex, 0 without spans,
  **balance_ratio 0.474**. Known skew: scaffolding acts over-represented — `pedir` 1996,
  `saudar` 1844, `agradecer` 1677. **Negative steering implemented** (`over_target_acts` +
  an "EVITE" avoid-list clause in the generation prompt + `--avoid-k`): once an act hits its
  per-act quota the teacher is told to skip gratuitous courtesy openings/closings, so it stops
  inflating scaffolding. Complements positive `focus`; a rebalanced regen run is the next step
  to actually move 0.47 → ~0.9.
- **First real eval against the benchmark (2026-06-06).** Measured on the **Porttinari holdout**
  (sentence-level, n=4091) — see spec `docs/superpowers/specs/2026-06-06-atos-layer-spec.md`:
  - **Zero-shot** (synthetic-only model, out-of-domain): macro-F1 **0.201** (coarse 0.407),
    acc 0.827 — `informar` 0.91, `perguntar` 0.62; rare/social acts near 0. ~68% of the paper's
    in-domain SOTA (0.295). Validates transfer; confirms the synthetic-distribution gap (scaffolding
    acts inflated in synthetic are near-absent in real news → `agradecer` recall 0.08).
  - **In-domain FT, no class weights:** acc 0.938 but macro-F1 0.214 (coarse 0.388) — **collapsed to
    the majority** (informar/perguntar ~0.96, rest 0.0). **Domain isn't the fix; imbalance is.**
  - **In-domain FT + `--class-weights`:** macro-F1 **0.262** (coarse **0.439**) — rare acts off the
    floor (sugerir 0.31, discordar 0.19); **~89% of the paper SOTA with only the loss fix, no data
    work.** Empirically confirms "class imbalance is the killer". The new `WeightedTrainer`
    (inverse-frequency loss) is the training-side lever, complementary to data-side steering.
  - **Shipped as v2 (2026-06-06):** the production model was retrained on the synthetic set with
    `--class-weights`; **zero-shot** Porttinari macro-F1 **0.201 → 0.233** (coarse 0.407 → 0.428),
    `perguntar` 0.62 → 0.71, rare acts off the floor (desculpar 0.25, concordar 0.20, …), nothing
    regressed — a Pareto win with **no regen and no API key**. Merged → ONNX int8 (export_onnx now
    quantizes) → published to HF `lucianfialho/atos-de-fala-ptbr`, live in the browser demo +
    `/assistir`. (Caveat: Transformers.js caches the model per-URL, so returning visitors may keep
    v1 until cache clears.)
- **In-browser inference gotchas (two):** (1) the Transformers.js token-classification pipeline
  returns `{entity, score, index, word}` with **no char offsets** — char spans must be
  reconstructed by walking the text and matching `word` tokens (handling WordPiece `##`);
  reading `tok.start/tok.end` yields garbage (whole sentence per token). (2) BERTimbau caps at
  **512 positions** — long transcript turns (e.g. 526 tokens) crash ONNX
  (`Add: cannot broadcast {1,526,768} vs {1,512,768}`); inputs must be **chunked** at
  sentence/space boundaries (~600 chars), annotated per chunk, then spans offset back and merged.
- **Data collection is live** (separate web repo, `atos-de-fala.vercel.app`, Next.js + Neon):
  the `/jogar` game (model proposes span→act, human votes/corrects → gold) and the new
  `/assistir` flow — [Human-in-the-Loop Distillation](concepts/human-in-the-loop-distillation.md)
  on **real interview transcripts** (Roda Viva / FAPESP, see
  [source](sources/2026-06-06-rodaviva-fapesp-transcripts.md)): the in-browser model proposes,
  the human corrects → `span_annotation`. Real text fixes the synthetic distribution at the source.
  `atos.collect export-spans` then turns those corrections into trainer-format JSONL
  (group by turn → majority-vote act per span → drop thin/overlapping), **closing the loop**
  collection → retrain → redeploy.
- **Active learning — fatia C implemented:** `atos.collect prioritize` writes `item.priority`
  = max over spans of `(1 − weighted_agreement)` [human disagreement, 0 if unvoted] + act
  rarity; `/api/next-item` serves highest-priority first (tie-break fewest votes, ε-greedy 0.15
  exploration). Disagreement is the reliable day-one signal (no model, no cold-start); rarity
  floats up under-represented/unvoted items. Model-uncertainty triage stays a later overlay
  (needs a human-gold retrain). Demographic disagreement is a research output, not noise.
- **Repo split:** model (Python, this repo) vs web (`atos-de-fala.vercel.app`). The DB schema
  is owned by the web repo (single source of truth); Python reads it via `TEST_SCHEMA_PATH`.

## ORAKTRON — the bigger frame (2026-06-06)

`atos de fala` is the **first concrete piece of [[oraktron-pragmatic-os]]** — a 4-layer vision
(syntax → semantics → **pragmatics** → causal pragmatics) that aims to make human *intention* a
computable, auditable object. Atos de fala is **Layer 3, axis 1** (the primitive speech-act /
intentionality axis). The plan is to build Layer 3 incrementally as **orthogonal axes** — one
[[bertimbau-lora-token-cls|LoRA adapter]] per axis, stacked on a frozen encoder, built in parallel
by the team, plus a **shared multi-axis pool** for the cross-axis synthesis ([[layered-pragmatic-axes]]).
The competitive vacuum (no unified multi-axis pragmatic engine) is documented in
[[2026-06-oraktron-competitive-differential]] (anchor: Ma et al., ACL 2025). **Honest:** the
compositional "intention" claim and the causal/outcome Layer 4 are hypotheses, not demonstrated —
near-term value is interpretable Layer-3 decomposition; causal is the star to steer by, not promise.

## Portable Theses

1. **Domain restriction enables size reduction.** A 15M-param GPT trained only on TinyStories
   learns correct English grammar — you don't need all of Wikipedia. Constraining the *data*
   shrinks the model.
2. **Task restriction also enables size reduction.** 50M active params hit F1 96% on PII
   detection. Constraining the *task* (not just data) buys frontier performance from a small model.
3. **Autoregressive → bidirectional via fine-tuning.** A pretrained AR checkpoint can become a
   bidirectional token classifier by swapping only the head + objective. Language knowledge transfers.
4. **Specialist + generalist beats one model.** No single model covers a niche + the general case
   well. Pipeline a narrow specialist (BR commercial docs: CNPJ, IE/27 states, CNH) alongside a
   broad generalist (arthrod, generic PT-BR PII).

## Reference Training Recipe (15M SLM on TinyStories)

| Hyperparameter | Value | Rationale |
|---|---|---|
| Dataset | TinyStories (2.1M stories) | Domain-constrained, ~100M tokens |
| Tokenizer | GPT2 BPE (50,257 vocab) | Reuse, no retraining needed |
| Context length | 128 tokens | Sufficient for short stories |
| Batch size | 32 (effective 1024 via grad-accum ×32) | GPU memory + stable gradients |
| Learning rate | 1e-4 peak, warmup 1000, cosine decay | Standard LR schedule |
| Optimizer | AdamW (β₂=0.95, wd=0.1) | LM standard |
| Iterations | 20,000 (~30 min on A100) | — |
| Final loss | Train 2.39 / Val 2.39 | No overfitting (domain = natural regularizer) |

## Key Findings — SLM from scratch (Source 1)

1. Next-token prediction alone is enough to learn both grammar and story structure.
2. Train/val losses track closely (2.39/2.39) → domain restriction acts as regularization.
3. At 20k iters grammar is correct but semantics loose; 40-60k likely improves coherence.
4. Production training needs: memory-mapped token files, bf16 mixed precision, grad accumulation, grad clipping.
5. Weight tying (token embedding ↔ lm_head) is parameter-efficient with no quality cost.

## Key Findings — OpenAI Privacy Filter (Sources 2 & 3)

6. Task restriction → small model: 50M active params, F1 96% on PII.
7. AR checkpoint → bidirectional token classifier by swapping head + objective; knowledge transfers.
8. Fine-tuning data efficiency: ~10% of the SPY dataset already saturates F1 at 0.962.
9. Token classification (all tokens in one forward pass) is radically faster than AR generation for understanding tasks.
10. `opf` CLI fine-tunes with `opf train dataset.jsonl` — no manual LoRA needed. Synthetic data via format-matching augmentation + insertion in natural context (= our pipeline).

## Key Findings — Privacy Filter BR build (Sources 4 & 5 & 6)

11. Built a fine-tuned BR Privacy Filter: 11k synthetic examples (4devs + Haiku), LoRA on q_proj/v_proj, head 33→53 classes, **F1 0.97** internal holdout, 5 epochs Colab A100.
12. **Search HuggingFace BEFORE building** — competitors (`arthrod/gliner-opf-ptbr-pii-v1` 914k/F1 0.885; `OpenMed/privacy-filter-multilingual`) were discovered late. 15 min of research first would have reframed the project.
13. **Synthetic quality > quantity in narrow domains**: 11k (1/83 of arthrod's 914k) gave higher F1 on own holdout. Curated small data suffices for narrow tasks.
14. **Format variants are critical**: 4 per identifier (formatado / raw / parcial / espaços) — without all 4 the model fails on real-world variants.
15. **PEFT/CUDA gotchas**: move base `.cuda()` BEFORE `get_peft_model()`; new head needs `dtype=float32` (bf16 → NaN logits); `modules_to_save` needs exact layer name (`score`, not `classifier`). See [LoRA Fine-tuning Pitfalls](concepts/lora-fine-tuning-pitfalls.md).
16. **Transformers API churn** breaks training loops (`evaluation_strategy`→`eval_strategy`, `tokenizer=`→`processing_class=`, `warmup_ratio` deprecated). Pin / install from main when config says `5.6.0.dev0`.
17. **Resume-from-disk > resume-from-memory**: write each generated example with `flush()`; a crash at 117 examples with no resume lost everything.
18. **v2 multi-provider generation** (Claude CLI + MiniMax in parallel): 6 real bugs documented — AI4Privacy PT is PT-PT, arthrod dataset went private, `ANTHROPIC_API_KEY` in env breaks claude CLI, MiniMax reasoning burns max_tokens on thinking, Starter plan has no highspeed, errors silently swallowed without `DEBUG=1`. See [Multi-Provider Generation](concepts/multi-provider-generation.md).

## Open Questions (carried over)

- At what iteration count does semantic coherence (not just grammar) emerge?
- How much does domain restriction matter vs. model size? Smallest model that learns grammar on a general corpus?
- Effect of context length 128 → 512 on coherence?
- Can fine-tuning a new domain work with a frozen backbone?
- Does the 11k-synthetic Privacy Filter BR generalize to real (non-synthetic) BR documents?
- Is a hybrid (arthrod 914k + our 11k) worth it?
- For an Analytics Copilot, is the specialized commercial-doc model better than the generic arthrod model?

## Sources

- [Building a Small Language Model from Scratch](sources/2026-05-02-building-slm-from-scratch.md)
- [OpenAI Privacy Filter](sources/2026-05-02-openai-privacy-filter.md)
- [OpenAI Privacy Filter — Model Card](sources/2026-05-03-openai-privacy-filter-model-card.md)
- [Privacy Filter BR — Build Process](sources/2026-05-06-privacy-filter-br-build.md)
- [Privacy Filter BR v2 — Plan](sources/2026-05-07-privacy-filter-br-v2-plan.md)
- [Privacy Filter BR v2 — Execution Log](sources/2026-05-16-privacy-filter-br-v2-execution.md)
- [Memória Roda Viva (FAPESP) — interview transcripts](sources/2026-06-06-rodaviva-fapesp-transcripts.md)
- [ORAKTRON — Competitive Differential (internal)](sources/2026-06-oraktron-competitive-differential.md)
