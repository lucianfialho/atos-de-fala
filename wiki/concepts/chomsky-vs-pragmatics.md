---
type: concept
tags: [atos-project, linguistics, pragmatics, generative-grammar, framing]
sources: 0
updated: 2026-06-05
---

# Chomsky vs Pragmatics

## Definition

The project is *named* after Chomsky, but its theory is the tradition he bracketed off. Chomsky's
program and speech-act/intent classification occupy almost separate intellectual worlds. Stating
this keeps the project intellectually honest.

## How It Works

**Chomsky's program** targets *linguistic competence* — the abstract, innate grammatical
knowledge (generative/transformational grammar, Universal Grammar), studied via grammaticality
judgments. Language *use* — context, intent, social function — is *performance*, deliberately
excluded from core linguistics.

**Speech-act theory** (Austin/Searle) targets exactly that excluded zone: what speakers *do* with
language. Intent classification is applied pragmatics. Methodologically, a BERT classifier is
corpus-trained and probabilistic — precisely what Chomsky criticized in the Norvig–Chomsky debate
("approximating unanalyzed data"). The project is, fittingly, its namesake's methodological opposite.

## Why It Matters

Avoids the trap of "using Chomsky's work" to build an intent classifier: his syntax-centric,
anti-statistical program does not operationalize into speech-act labels. The right grounding is
pragmatics (Searle) + the ISO 24617-2 standard. Chomsky is the name; pragmatics is the method.

## Related Concepts

- [Speech Act Theory](speech-act-theory.md)
- [Noam Chomsky](../entities/noam-atos.md)

## Sources

- Norvig, P. (2011). "On Chomsky and the Two Cultures of Statistical Learning." https://norvig.com/atos.html
- Chomsky, N. (1965). *Aspects of the Theory of Syntax*. MIT Press. [background]
- Stanford Encyclopedia of Philosophy — Pragmatics: https://plato.stanford.edu/entries/pragmatics/
