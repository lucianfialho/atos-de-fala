---
type: source
tags: [dialogue-acts, iso-24617-2, diaml, speech-acts, taxonomy, atos-project]
sources: 1
updated: 2026-06-05
---

# ISO 24617-2: A semantically-based standard for dialogue annotation

**Authors:** Harry Bunt, Jan Alexandersson, Jae-Woong Choe, Alex Chengyu Fang, Koiti Hasida, Volha Petukhova, Andrei Popescu-Belis, David Traum
**Venue / Year:** LREC 2012
**Raw:** `raw/sources/2012-iso-24617-2-bunt-lrec.pdf`
**URL:** http://www.lrec-conf.org/proceedings/lrec2012/pdf/530_Paper.pdf

## Summary

Describes the final version of ISO standard 24617-2 ("Semantic annotation framework, Part 2:
Dialogue acts"). A dialogue act has two components: a **communicative function** (how the
addressee should use the content to update their information state) and **semantic content**.
The standard is multidimensional, built on the DIT++ taxonomy (Bunt) and the DAMSL lineage,
with a markup language (DiAML) and a formal information-state-update semantics.

## Key Takeaways

- **Unit of annotation = "functional segment":** a *minimal stretch of behaviour that has one or
  more communicative functions.* This is the theoretical grounding for our **span-level** approach.
- **9 semantic dimensions:** Task, Auto-Feedback, Allo-Feedback, Turn Management, Time Management,
  Discourse Structuring, Own Communication Management, Partner Communication Management, Social
  Obligations Management. A segment can carry one function per dimension (multidimensional /
  overlapping) — our v1 deliberately simplifies to single-label, non-overlapping spans.
- **Two function classes:** *general-purpose functions* (GPFs — combine with any dimension) and
  *dimension-specific functions* (only one dimension; often formulaic: "Olá", "Obrigado", "Tchau").
- **GPF sub-groups:**
  - *Information-providing:* Inform, Agreement, Disagreement, Correction, Answer, Confirmation, Disconfirmation.
  - *Information-seeking:* Question (propositionalQuestion / setQuestion / checkQuestion).
  - *Action-discussion:* Request, Instruct, Suggestion, Offer, Promise, AcceptOffer, DeclineOffer, AcceptSuggestion, AddressRequest.
- **Social Obligations Management functions:** Greeting, Self-introduction, Apology (+ AcceptApology), Thanking (+ AcceptThanking), Valediction.
- **Qualifiers** modulate GPFs: certainty (certain/uncertain), conditionality (conditional/unconditional), sentiment.
- **Rhetorical relations** between dialogue units (Cause, Explanation, Justification, Motivation…) link to RST — the standard does not fix a relation set.
- **Automatic annotation works:** incremental token-based classifiers reach high F per dimension
  (Social Obligations 98.6, Auto-Feedback ~97, Task ~86) — ISO 24617-2 is usable for automatic tagging.

## Concepts Introduced

- [ISO 24617-2 Dialogue Acts](../concepts/iso-24617-2-dialogue-acts.md)
- [Speech Act Theory](../concepts/speech-act-theory.md)
- [Speech Act Label Scheme](../concepts/speech-act-label-scheme.md)

## Entities Mentioned

- [ISO 24617-2 / DiAML](../entities/iso-24617-2.md)
- DIT++ taxonomy (Bunt); DAMSL (Allen & Core 1997)
