---
type: concept
tags: [distillation, active-learning, data-collection, human-in-the-loop]
defined: 2026-06-06
---

# Human-in-the-Loop Distillation

The data-collection strategy for v2: the **local model proposes, the human corrects**, and
the correction is the training signal — distillation where the human, not a larger teacher,
provides the gold.

## The trap it avoids

Running the model over text and *keeping its own predictions* is self-training: the model
already agrees with what it predicted, so the signal is ~zero and its errors propagate.
What's valuable is the **disagreement** — where the human overrides the model. So the flow
must capture corrections, not just predictions.

## The flow (`/assistir`, web repo)

1. Load a real transcript turn (Roda Viva / FAPESP — see
   [[2026-06-06-rodaviva-fapesp-transcripts]]).
2. The in-browser model (BERTimbau+LoRA → ONNX q8, Transformers.js/WebGPU) proposes
   spans→acts on the turn.
3. The human **confirms / changes the act / removes a wrong span / adds a missed one**.
4. Each action is stored in `span_annotation` with the model's original proposal
   (`model_act`) + the human's verdict (`confirmed | corrected | added`) → both the gold
   label *and* the where-the-model-failed signal.
5. `atos.collect export-spans` turns the rows into trainer-format JSONL (group by turn,
   majority-vote the act per span, drop thin/overlapping) → feeds the next retrain. This is
   the step that closes the loop back to the model.

## Why on real informal text

The model is weak exactly on real, informal dialogue (slang, irony, crosstalk) because v1
is synthetic. Those are the high-information corrections — they fix the synthetic
distribution and feed active-learning triage (prioritize where humans disagree with the
model, and where demographic profiles disagree with each other). See
[[bertimbau-lora-token-cls]], [[bioes-tagging]].
