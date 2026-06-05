# Wiki Schema

Read this file at the start of every session before performing any wiki operation.

## Purpose

Personal knowledge wiki for the **chomsky** project — research, papers, and accumulated
learnings on building and fine-tuning language models. Knowledge base seeded from the
`myFirstSmallModel` wiki (SLM-from-scratch + Privacy Filter BR fine-tuning campaigns).

The wiki is a **persistent, compounding artifact** (Karpathy's LLM-Wiki pattern): the LLM
incrementally builds and maintains interlinked markdown instead of re-deriving knowledge
from raw sources on every query.

## Directory Layout

- `raw/sources/` — immutable source files (papers, transcripts, notebooks, code). Never modify.
- `wiki/sources/` — one summary page per source.
- `wiki/concepts/` — technical concept pages (architecture, training, datasets, fine-tuning).
- `wiki/entities/` — named things (datasets, tools, people, models).
- `wiki/overview.md` — running synthesis of everything learned.
- `index.md` — catalog of all wiki pages (read first when answering queries).
- `log.md` — append-only session history.

## Frontmatter (required on all wiki pages)

```yaml
---
type: source | concept | entity | synthesis
tags: [tag1, tag2]
sources: <int>
updated: YYYY-MM-DD
---
```

## Page Templates

### Source page
```
# [Title]
**URL/path:** ...
**Type:** paper | video | notebook | code | build-log
**Date ingested:** YYYY-MM-DD

## Summary
## Key Takeaways
## Concepts Introduced
## Entities Mentioned
## Notable Quotes / Code
```

### Concept page
```
# [Concept]
## Definition
## How It Works
## Why It Matters
## Related Concepts
## Sources
```

### Entity page
```
# [Entity]
## What It Is
## Significance
## Key Facts
## Sources
```

## Ingestion Workflow (papers & sources)

When a new source arrives:
1. Store raw in `raw/sources/YYYY-MM-DD-<slug>.<ext>` (download the PDF/notebook locally — never modify it).
2. Read it fully; discuss takeaways with the user.
3. Write summary in `wiki/sources/YYYY-MM-DD-<slug>.md`
4. Create/update concept pages (`wiki/concepts/`)
5. Create/update entity pages (`wiki/entities/`)
6. Update `wiki/overview.md` (add a "Key Findings (Source N)" block; revise the thesis)
7. Update `index.md`
8. Append entry to `log.md`

One source typically touches 10-15 wiki pages.

## Query Workflow

1. Read `index.md` to find relevant pages
2. Read the full content of relevant pages
3. Synthesize answer with wiki citations
4. If the answer is valuable, save it back as a new page (explorations compound like sources)

## Lint Workflow

Check for:
- Orphan pages (not linked from index.md)
- Dangling links (links to pages that don't exist)
- Stale claims contradicted by newer sources
- Concepts mentioned but lacking dedicated pages
- Missing cross-links between related pages

## Links

Use plain markdown links: `[text](../concepts/lora-fine-tuning-pitfalls.md)`
No wikilink syntax.

## Log Entry Format

```
## [YYYY-MM-DD] <type> | <title>
<one-line summary>
```

Types: `ingest`, `query`, `lint`, `update`, `build`, `plan`
