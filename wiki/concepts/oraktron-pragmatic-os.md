---
type: concept
tags: [oraktron, pragmatics, intention, vision, world-models, architecture]
defined: 2026-06-06
---

# ORAKTRON 2.0 — Pragmatic Operating System

The north-star vision the **atos de fala** project is the first concrete piece of. ORAKTRON
aims to make **human intention** a first-class computational object — auditable, causal,
reconstructable — the way Chomsky formalized syntax and Montague formalized semantics.

## The four layers

1. **Syntax** — structure (parse trees, dependencies). *Largely solved; integrate existing tools.*
2. **Semantics** — meaning (semantic/logical graphs, KR). *Largely solved; integrate.*
3. **Pragmatics** — the intentional architecture: why it was said, intended effect, embedded
   assumptions, what's hidden, what behavior is induced → **speech acts + pragmatic vectors +
   intent decomposition**. *This is the unformalized gap and the buildable core.*
   **`atos de fala` lives here** — the speech-act / communicative-act axis (the most primitive
   intentionality layer). See [[layered-pragmatic-axes]], [[speech-act-theory]].
4. **Causal Pragmatics** — the missing layer: which pragmatic structures produce which outcomes
   (conversion, sentiment shift, compliance). Inspired by LeCun world models + causal inference.

Pipeline: `Text → Syntax Graph → Semantic Graph → Pragmatic Graph → Intent Model → Outcome Model`
— vs the LLM `Text → Tokens → Prediction`.

## Key constructs

- **Intent Vector** — interpretable multidimensional representation (Authority, Urgency, Certainty,
  Hedging, Trust, Directive Force, Manipulation, Presupposition Density, …). **No opaque latents;
  every dimension must have linguistic evidence.** (This is the orthogonal multi-axis decomposition
  of [[layered-pragmatic-axes]], framed toward influence/persuasion.)
- **Pragmatic Graph** — persistent (Neo4j) graph of intentions/beliefs/goals/strategies/outcomes;
  every relation explicit and inspectable (vs embeddings).
- **Graph of Thoughts** — text as an interconnected network of intentions (claim ↔ presupposition ↔
  speech act ↔ rhetorical device ↔ hidden goal ↔ intended outcome).
- **Bidirectional ops** — Decomposition (text→intent), Reconstruction (intent→text), Recomposition
  (same intent, new audience/format), Composition (many intents→one strategy).
- **Delta Intelligence** — measure preserved / altered / lost / introduced intentions across a
  transformation → a **Pragmatic Delta Score**. The system explains itself; the user never has to
  just trust it.
- **Outcome Graph** — link Intentions → Behaviors → Outcomes for causal analysis (Layer 4).

## Honest assessment (do not oversell)

- **Layers 1–2 are integration, not invention.** The novel, fundable work is Layer 3.
- **Layer 4 (causal/outcome) is a moonshot.** Predicting conversion/sentiment/compliance needs
  text→behavior outcome data nobody has, plus real causal-inference confound control. Treat as
  long-term vision, not roadmap; the [[2026-06-oraktron-competitive-differential]] doc already
  flags "tracking intention" as **hypothesis, not demonstrated fact**.
- **Self-supervised "audience reaction"** doesn't transfer from next-token: text is self-labeled,
  reactions are not — needs outcome-annotated corpora.
- **Fuzzy intent dimensions** (Trust, Status Signaling, Narrative Tension) risk low inter-annotator
  agreement (Geertzen et al. 2008); each dimension needs operationalization + a benchmark or it's
  narrative. See [[dialogue-act-annotation-reliability]].

The defensible near-term: build Layer 3 as interpretable orthogonal axes (atos first), add
Delta + bidirectional ops on top. Causal is the star to steer by, not to promise.
