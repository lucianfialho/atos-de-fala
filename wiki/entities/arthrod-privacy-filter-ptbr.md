---
type: entity
tags: [model, competitor, pii, brazilian, privacy-filter, fork]
sources: 1
updated: 2026-05-06
---

# arthrod/gliner-opf-ptbr-pii-v1

## What It Is

Open-source fine-tune of OpenAI Privacy Filter for PT-BR PII detection. Published 2026-04-23 on HuggingFace by `arthrod`. Apache 2.0.

## Significance

The primary competitor discovered late in the Privacy Filter BR project. First major PT-BR-specific Privacy Filter fine-tune available publicly. Trained on 90× more data than the in-house Privacy Filter BR project but covers different categories.

## Key Facts

- **Base:** openai/privacy-filter (1.5B / 50M active)
- **Training data:** 914,452 rows of natural-text PT-BR (`arthrod/oai-pf-ptbr-chunked-v2`)
- **Schedule:** 3 epochs × 3 saves per epoch
- **Optimizer:** AdamW, lr 1e-5, wd 0.01, max-grad-norm 1.0
- **Batch:** 32 windows × grad-accum 4 (effective 128)
- **Context:** n-ctx 256, bf16
- **Hardware:** AMD MI300X / ROCm 7.2
- **License:** Apache 2.0
- **Performance:** detection.span typed F1 0.885 (P 0.894 / R 0.876) on 5k PT-BR val

## Categories Covered (24 PT-BR canonical)

- `cpf_document_number`, `rg_document_number`, `pis_document_number`
- `credit_card`, `phone_number`, `email_address`
- `first_name`, `middle_name`, `last_name`
- `dob`
- Location: `street`, `building_number`, `neighborhood`, `city`, `state`, `state_abbreviation`, `zip`, `full_address`
- LGPD sensitive: `personal_description_of_ethnicity`, `_medical_conditions`, `_organizational_affiliation`, `_political_opinion`, `_religious_convictions`, `_sexual_information`

Plus 47 cross-source labels (general PII).

## Categories MISSING (vs privacy-filter-br)

- ❌ CNPJ (corporate tax ID)
- ❌ Inscrição Estadual (state-level tax registration, 27 formats)
- ❌ CNH (driver's license, separate from `driver_license_number`)
- ❌ Título de Eleitor
- ❌ Certidão (birth/marriage/death certificate numbers)

These are critical for **commercial document** processing (NF-e, contracts, holerite).

## Strategic Position

Generalist for **personal PT-BR PII** with strong granularity on names and addresses. Weak coverage of **commercial/business document** PII (CNPJ, IE, CNH).

Recommended use: pair with `privacy-filter-br` for full coverage:
- arthrod handles personal PII (names, addresses, contact info)
- privacy-filter-br handles commercial document PII (CNPJ, IE, CNH, etc.)

## Sources

- [Privacy Filter BR Build](../sources/2026-05-06-privacy-filter-br-build.md)
- HuggingFace: https://huggingface.co/arthrod/gliner-opf-ptbr-pii-v1
- Demo: https://huggingface.co/spaces/arthrod/gliner-opf-ptbr-pii-demo
