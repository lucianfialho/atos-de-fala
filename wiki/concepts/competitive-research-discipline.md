---
type: concept
tags: [process, lessons-learned, research, ml-engineering]
sources: 1
updated: 2026-05-06
---

# Competitive Research Discipline

## Definition

The discipline of searching for prior art (similar models, datasets, libraries) BEFORE starting an ML project, not after. Established as a hard rule after the Privacy Filter BR project discovered competitors only after 3 days of building.

## Why It Matters

In the Privacy Filter BR project, the build started immediately after seeing the OpenAI Privacy Filter announcement. Three days into building, search revealed:
- `arthrod/gliner-opf-ptbr-pii-v1` — already published, 914k samples, F1 0.885
- `OpenMed/privacy-filter-multilingual` — 16 languages including PT
- `OpenMed/OpenMed-PII-Portuguese-*` — 11+ Portuguese-specific models

If this search happened on day zero, the decision would have been:
- Use `arthrod` for general PT-BR PII
- Build only the BR-specific commercial document categories (CNPJ/IE/CNH) as a complement
- Save 80% of the build time

## The Rule

Before any new ML model project:

```
Spend 30 minutes searching:
  - HuggingFace: search for the model type + language/domain
  - GitHub: same query, sort by recently updated
  - Papers: arxiv-sanity, semantic scholar
  - Twitter/X: ML announcements

Output a one-page comparison:
  - What exists
  - What's missing
  - Where YOUR project fits in (differentiation or alternative)

Only then start building.
```

## What Counts as "Already Solved"

- Same architecture (e.g., Privacy Filter fine-tune for PT-BR)
- Similar accuracy on similar benchmarks
- Open-source license that matches your needs
- Active maintenance (commits in last 6 months)

If all 4 are true, **use the existing model** and contribute back if needed.

## What Counts as "Still Worth Building"

- Different training data domain (commercial docs vs general text)
- Different target language variant (PT-BR vs PT-PT)
- Different categorical granularity (specific labels needed)
- Privacy/security constraint (must run locally, not on third-party model)
- Performance gap (real measurable difference)

## Application to Future Projects

For the upcoming **ETL SLM** for Analytics Copilot:

1. Search HF for: "SQL generation model", "text-to-SQL", "BR e-commerce models"
2. Check existing tools: LangChain SQL agents, LlamaIndex query engines
3. Compare: do they support `gmp-cli` syntax? VTEX? GA4 specifically?
4. Decide: train from scratch only if no existing solution covers the use case

## Related Concepts

- [Fine-tuning Efficiency](fine-tuning-efficiency.md)
- [Specialization vs Generalization](specialization-vs-generalization.md)

## Sources

- [Privacy Filter BR Build](../sources/2026-05-06-privacy-filter-br-build.md)
