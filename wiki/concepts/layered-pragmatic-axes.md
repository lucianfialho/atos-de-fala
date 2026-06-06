---
type: concept
tags: [oraktron, pragmatics, multi-axis, lora, orthogonal-annotation, strategy]
defined: 2026-06-06
---

# Layered Pragmatic Axes (the build strategy)

How [[oraktron-pragmatic-os]]'s Layer 3 gets built incrementally, starting from `atos de fala`.

## "Layer" = orthogonal axis, NOT more classes

The trap: piling more labels into the single, mutually-exclusive speech-act classifier
(13 → 30 exclusive acts). That recreates the **SWBD-DAMSL** scheme the competitive analysis
([[2026-06-oraktron-competitive-differential]]) flags as the *opposite* of the goal — a span
can't be `pedir` AND `ironic` if the label set is exclusive, so the compositional differential is lost.

Correct: each layer is an **independent orthogonal axis** with its own label space. One sentence
gets a value on **every** axis simultaneously (the DIT++ "orthogonal dimensions" logic, not exclusive tags).
`atos de fala` is axis 1 — the primitive intentionality layer.

## Architecture: frozen encoder + one adapter per axis

Shared **BERTimbau encoder (frozen)** + one **LoRA adapter (or head) per axis**:
- acts → adapter 1, evidentiality → adapter 2, appraisal → adapter 3, politeness → adapter 4, …
- **Adding a piece = train a new adapter; the others don't retrain** → literal stackable "layers",
  and it sidesteps catastrophic forgetting (each axis isolated in its adapter). Reuses the existing
  [[bertimbau-lora-token-cls]] recipe per axis.

## Team in parallel (axes are independent)

Because axes are orthogonal, contributors can build different-axis datasets **simultaneously,
without blocking each other** (parallel beats sequential here). Each finished dataset → one adapter
→ added to the stack.

## The crown jewel: the shared multi-axis pool

If everyone annotates their axis on **different** sentences, you train each adapter but can **never
cross the axes** — and the crossing is the entire differential. So the dataset has two parts:
1. **Per-axis, parallel** (own sentences) → trains each adapter; provides volume.
2. **Shared pool** — the **same sentences annotated on ALL axes** → enables the cross-axis synthesis
   and is the proof of the differential (the "≥50 compositional cases" the competitive doc calls the
   most valuable asset, above raw volume). Needs coordination (everyone annotates the same sentences).

## Intention is a synthesis stage, not a formula

There is no formula where N axis-values "sum" to intention. The combination is a learned/reasoned
**cross-dimensional synthesis** (a model over the multi-axis vector, or an agent reasoning over the
structured output). The axis vector is the **input** to intent inference, not the intent itself — and
per the competitive doc this synthesis is the **unproven, hardest, most-valuable** part. Breadth
(many axes) is the easy win; cross-axis intention is the bet, validated only by the compositional cases.
