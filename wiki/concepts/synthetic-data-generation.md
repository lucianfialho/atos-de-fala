---
type: concept
tags: [dataset, training-data, synthetic, ner, automation]
sources: 1
updated: 2026-05-06
---

# Synthetic Data Generation for NER Fine-tuning

## Definition

Programmatic creation of labeled training data by inserting known PII values into document templates and auto-labeling the spans. Avoids the cost and privacy issues of using real data while providing exact label accuracy.

## How It Works

The pipeline used in Privacy Filter BR:

```
Step 1: Generate synthetic PII values
  4devs API → CPF, CNPJ, RG, name, email, etc.
  (or any other deterministic generator)

Step 2: Compute format variants
  CPF "680.075.670-97" → also generate raw "68007567097",
                                       partial "680.075.***-**",
                                       spaced "680 075 670 97"

Step 3: Render document template
  Jinja2 template with {{cpf}}, {{name}}, {{address}}
  → produces document text with PII at known positions

Step 4: LLM rewrite for naturalness (optional)
  Claude Haiku rewrites the rigid template output into natural text
  Constraint: "preserve all PII values verbatim"

Step 5: Validation
  Verify each inserted PII value appears verbatim in output
  Discard examples where LLM paraphrased PII

Step 6: Auto-label with BIOES
  Find each known PII value's character span in the text
  Convert to token-level BIOES tags
  Output: {"text": "...", "entities": [{start, end, label}]}
```

## Why It Matters

- **Zero label noise**: you inserted the values, you know exactly where they are
- **Format diversity**: programmatically generate all variants (formatted/raw/partial)
- **Scale on demand**: 10k or 100k examples cost time, not money
- **Privacy compliance**: no real data, no LGPD issues with the dataset itself
- **Domain control**: choose exactly which document types to include

## Why It's Limited

- **Distribution mismatch with real data**: F1 0.97 on synthetic ≠ F1 on real-world
- **Template repetition**: model can memorize structural patterns instead of learning generalizable signals
- **LLM bias**: if Claude/Haiku has stylistic preferences, they leak into the dataset
- **No edge cases from production**: weird formatting, OCR artifacts, partial documents — only present if explicitly generated

## When To Use vs Real Data

| Use synthetic | Use real |
|---|---|
| Domain too sensitive for real data | Production-grade benchmarking |
| Cold start with no labeled data | Distribution generalization |
| Format variants need explicit coverage | Adversarial cases |
| Quick experimentation | Final model evaluation |

Best practice: train on synthetic, validate on a small set of real (anonymized) data.

## Related Concepts

- [Fine-tuning Efficiency](fine-tuning-efficiency.md)
- [BIOES Tagging](bioes-tagging.md)
- [Token Classification](token-classification.md)

## Sources

- [Privacy Filter BR Build](../sources/2026-05-06-privacy-filter-br-build.md)
