---
type: entity
tags: [dataset, evaluation, fine-tuning, pii, medical, legal]
sources: 2
updated: 2026-05-03
---

# SPY Dataset

## What It Is

Dataset sintético de consultas médicas e questões legais usado pela OpenAI para avaliar fine-tuning efficiency do Privacy Filter. Está fora da distribuição de treinamento do modelo base — por isso é um bom teste de adaptação de domínio.

## Significance

A Table 2 do model card usa o SPY para mostrar que 10% dos dados de treino satura F1 em 0.962. É a referência para estimar quanto dado o Privacy Filter BR vai precisar.

## Key Facts

- **Domínio:** consultas médicas + questões legais (sintéticas)
- **Labels mapeados:** NAME/USERNAME → private_person, ADDRESS → private_address, EMAIL → private_email, PHONE_NUM → private_phone, URL → private_url, ID_NUM → account_number
- **Excluídos:** `secret` e `private_date` (não existem no SPY)
- **Fine-tuning results (Table 2):**

| Fração | Épocas | F1 |
|---|---|---|
| 0% | 0 | 0.545 |
| 1% | 13 | 0.879 |
| 10% | 39 | **0.962** |
| 50% | 18 | 0.983 |

## Implicação para Privacy Filter BR

Se 10% do SPY satura o benchmark, e o SPY tem categorias similares às nossas, então ~10k exemplos BR bem curados devem atingir F1 > 0.96 nas 13 categorias BR.

## Sources

- [OpenAI Privacy Filter Model Card](../sources/2026-05-03-openai-privacy-filter-model-card.md)
