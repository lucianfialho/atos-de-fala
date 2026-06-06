---
type: concept
tags: [iso-24617-2, dialogue-acts, diaml, taxonomy, speech-acts, atos-project]
sources: 1
updated: 2026-06-05
---

# ISO 24617-2 Dialogue Acts

## Definition

The international standard for dialogue act annotation. A dialogue act = a **communicative
function** (how the addressee should update their information state) + **semantic content**.
The unit of annotation is the **functional segment**: a minimal stretch of text/behaviour that
carries one or more communicative functions — the theoretical basis for span-level tagging.

## How It Works

Multidimensional: **9 dimensions** — Task, Auto-Feedback, Allo-Feedback, Turn Management, Time
Management, Discourse Structuring, Own/Partner Communication Management, Social Obligations
Management. Functions are either **general-purpose** (combine with any dimension) or
**dimension-specific** (one dimension; often formulaic). GPF sub-groups:

- **Information-providing:** Inform, Agreement, Disagreement, Correction, Answer, Confirmation, Disconfirmation.
- **Information-seeking:** Question (propositional / set / check).
- **Action-discussion:** Request, Instruct, Suggestion, Offer, Promise, Accept/Decline Offer, Accept Suggestion, Address Request.
- **Social Obligations:** Greeting, Self-introduction, Apology, Thanking, Valediction.

Qualifiers modulate functions (certainty, conditionality, sentiment). Built on the DIT++ taxonomy
and the DAMSL lineage. Annotation is serialized in DiAML (XML) with information-state-update semantics.

## Why It Matters

It is the principled, standards-based source for our label set. For atos v1 we take the
general-purpose + social-obligation functions (mapped to Searle) and drop the dialogue-control
dimensions (turn/time/feedback), which are irrelevant to open, non-conversational PT-BR text.
The "functional segment" concept justifies tagging spans, not whole messages.

## Related Concepts

- [Speech Act Label Scheme](speech-act-label-scheme.md)
- [Speech Act Theory](speech-act-theory.md)
- [Token Classification](token-classification.md)

## Sources

- [ISO 24617-2 (Bunt et al., LREC 2012)](../sources/2012-iso-24617-2-bunt-lrec.md)
- [ISO 24617-2 / DiAML](../entities/iso-24617-2.md)
