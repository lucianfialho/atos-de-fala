---
type: concept
tags: [synthetic-data, class-imbalance, distillation, augmentation, ner, ptbr]
defined: 2026-06-07
---

# Synthetic Data Techniques (untried levers for the atos dataset)

Research sweep (arXiv/ACL) targeting our **measured** problems — not generic advice. Context:
span-level speech-act token classifier ([[bertimbau-lora-token-cls]]), trained on
teacher-distilled synthetic data ([[teacher-mixture-pipeline]]), with two confirmed failures:
**class imbalance** (balance 0.47; rare commissive/social acts starved) and **distribution gap**
to real text (zero-shot macro-F1 ~0.23 on Porttinari news). Already done: positive/negative
prompt steering, class weights, agreement-gating + adjudication.

## Lever 1 — imbalance, beyond class weights
- **Dice / self-adjusting Dice loss (DSC)** — optimizes soft-F1, down-weights easy negatives (the
  "O"-dominated BIOES regime). Drop-in loss; best single under-tried lever. (Li et al., ACL 2020,
  arXiv:1911.02855.)
- **Focal loss (token-level)** — `(1−p_t)^γ` onto hard/rare tokens; A/B vs Dice, don't stack. (arXiv:1708.02002; 2401.11431.)
- **Rejection-sampling generation quotas** — over-generate then accept/reject to hard-enforce per-act
  token counts at the source. Stronger than our soft steering (enforces posterior, not just prior).
  (EPIC, arXiv:2404.12404.)
- **Difficulty-aware curriculum** on noisy tokens (teacher-agreement/loss as difficulty). (arXiv:2402.14948.)
- ⚠️ SMOTE/embedding-interpolation **doesn't work** for span labels — skip.

## Lever 2 — closing the gap to real PT-BR (the dominant problem)
Loss functions don't touch this; it's a *distribution* gap.
- **Teacher-annotate REAL text instead of inventing it** (= the [[oraktron-pragmatic-os|annotate-corpus]]
  idea). Grounding in real examples gives the biggest faithfulness gain; "discard the conditioning
  label, let the teacher label existing text." **Use dialogic PT-BR** (subtitles, forum/Reddit-PT,
  support logs, transcribed speech) — **not news**, which lacks the social/commissive acts.
  (Generate-Annotate-Learn, TACL; DoPAMine, arXiv:2410.00260.)
- **Attributed/persona prompting** — sample over axes (register formal/coloquial/gíria, channel
  SMS/email/fala, region, persona, length) instead of single-axis steering; diversity is "pivotal",
  ~5% of cost, removes LLM-flavor + systematic bias. (AttrPrompt, NeurIPS 2023, arXiv:2306.15895.)
- **MELM** — mask the span, let BERTimbau itself regenerate novel same-act fillers; +6.3 F1 at
  100-sample level, label-preserving. Ideal for starved acts (oferecer/prometer/desculpar/despedir).
  (ACL 2022, arXiv:2108.13655.)
- Cheap baselines: label-wise token / mention(span) replacement. ⚠️ back-translation **not** for token
  labels (span re-projection errors). (arXiv:2010.11683.)

## Lever 3 — teacher/label quality
- **Two-teacher cross-agreement** (DeepSeek + Claude, varied prompts; keep agreed tokens) — strictly
  stronger than single-teacher gating; breaks single-teacher bias (a prime suspect for the flavor gap).
- **Span-level self-consistency** (sample k, majority boundary/label; entropy = difficulty signal).
- **Critic/verifier pass** ("is this span really act X?") — LLM label-error detection lifts downstream. (arXiv:2410.18889.)

## Pitfalls (honest)
- **Model collapse / tail-cutting**: synthetic-only training narrows to the head and erases tails —
  *literally our rare-act problem self-amplifying*. Keep real text in the mix; don't iterate
  teacher→student→teacher. (Curse of Recursion, arXiv:2305.17493.)
- **Diversity ≠ quality**: measure span-label fidelity too, not just lexical diversity.
- **Volume isn't the fix**: doubling synthetic gave 76% vs 88% for half the human-labeled count.
  Distribution + balance, not raw count.

## Evaluation under this regime
- Don't headline one news benchmark — report per-act F1 on **acts present**, treat absent acts as N/A,
  not 0 (Porttinari blindness, see [[overview]] per-act priorities).
- Build a small **real dialogic** gold eval (~200–400 spans, self-adjudicated) covering all 13 acts —
  the only honest measure of the transfer gap.
- Pre-training audit: α-Precision (fidelity) + β-Recall (coverage) + n-gram freq (LLM-flavor); rising
  flavor / dropping coverage across rounds = collapse early-warning. (arXiv:2102.08921.)

## Top 3 to try next
1. **Teacher-annotate real *dialogic* PT-BR spans** (Lever 2a) — attacks the 0.23 transfer gap and
   starves collapse. Highest payoff. (Refines [[oraktron-pragmatic-os|annotate-corpus]]: dialogic, not news.)
2. **Rejection-sampling per-act quotas + Dice loss** (1c + 1a) — hard-balance at the source + optimize
   F1 directly; both low effort, attack imbalance from data + objective sides.
3. **AttrPrompt persona axes + MELM for starved acts** (2b + 2c) — kill LLM-flavor cheaply + manufacture
   novel label-preserved rare-act spans (BERTimbau as the MLM).
Near-free add-on: switch single-teacher gating → two-teacher cross-agreement (Lever 3).
