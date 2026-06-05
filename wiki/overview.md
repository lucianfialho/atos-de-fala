---
type: synthesis
tags: [language-models, fine-tuning, training, speech-acts, ner]
sources: 10
updated: 2026-06-05
---

# Overview — chomsky

## Thesis (defined 2026-06-05)

**chomsky** builds a span-level **speech-act classifier** for **PT-BR**: it decomposes open text
into non-overlapping spans and labels each with a speech act (intent). The model is BERTimbau
fine-tuned with LoRA as a BIOES token classifier, distilled from an LLM teacher mixture
(Claude rubric/gold + MiniMax bulk, agreement-gated). The taxonomy (13 acts → 53 labels) is
grounded in ISO 24617-2 + Searle, not in Chomsky's syntax — the name is a nod; the method is
pragmatics. See [Chomsky vs Pragmatics](concepts/chomsky-vs-pragmatics.md).

Below the thesis sits the portable, hard-won knowledge seeded from the `myFirstSmallModel` wiki
(SLM-from-scratch + Privacy Filter BR fine-tuning), which the architecture reuses 1:1
(token classification, BIOES, LoRA, synthetic data).

## Fase 0 — key findings (2026-06-05)

- **Unit of annotation is the "functional segment"** (ISO 24617-2): a minimal stretch carrying
  one or more communicative functions — the grounding for span-level tagging.
- **Taxonomy frozen at 13 acts / 53 labels** from ISO 24617-2 general-purpose + social-obligation
  functions, mapped to Searle, adapted for open text (dialogue-control dimensions dropped).
- **No public PT-BR span-level speech-act dataset exists** — confirms the synthetic teacher
  approach. (PROPOR 2024 "Bringing Pragmatics to Porttinari" annotates news, not at our granularity.)
- **PT-BR pragmatics notes for annotation:** indirect requests ("você poderia…?" = `pedir`) and
  diminutive softeners ("um minutinho") — captured in the rubric, not as labels.
- **Compact tagset is the reliable choice** (Geertzen et al. 2008): coarser DA tagsets get higher
  inter-annotator agreement; Turn/Feedback dimensions are unreliable. Confirms the 13-act v1 and
  the dropped dimensions. Known confusable pairs (inform×answer×elaborate×explain; instruct×answer)
  → seed the Plan-2 rubric's disambiguation guidance.

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
