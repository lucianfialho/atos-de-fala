---
type: source
tags: [slm, pii, privacy, token-classification, fine-tuning, architecture]
sources: 1
updated: 2026-05-02
---

# OpenAI Privacy Filter

**URL:** https://openai.com/index/privacy-filter/
**Author:** OpenAI
**Type:** Blog post / model release
**Date ingested:** 2026-05-02

## Summary

A OpenAI lançou o Privacy Filter: um modelo open-weights de 1.5B parâmetros (50M ativos) para detecção e mascaramento de PII em texto. É um classificador bidirecional de tokens, não um modelo gerador — rotula toda a sequência em uma única forward pass em vez de gerar token a token.

O que torna esse modelo relevante para este wiki: ele é outro exemplo do princípio "domínio restrito + modelo pequeno = performance de fronteira". O Privacy Filter consegue F1 de 96% num benchmark de PII com 50M parâmetros ativos — muito menor do que modelos gerais de linguagem que fariam a mesma tarefa.

## Key Takeaways

- **Domínio restrito → modelo menor**: 50M parâmetros ativos para uma tarefa específica alcançam performance de fronteira. O mesmo princípio do TinyStories aplicado a um problema diferente.
- **Autorregressivo → bidirecional**: O modelo começa de um checkpoint pré-treinado autorregressivo e é adaptado para classificador bidirecional de tokens. A cabeça de LM é substituída por uma cabeça de classificação.
- **Uma passada vs geração**: Token classification classifica todos os tokens simultaneamente em uma única forward pass — fundamentalmente diferente e muito mais rápido do que geração autorregressiva token a token.
- **Fine-tuning eficiente**: Com poucos dados de domínio específico, F1 sobe de 54% para 96%. Modelos pequenos fine-tunam rápido.
- **Viterbi para spans coerentes**: As previsões por token são decodificadas em spans coerentes via algoritmo de Viterbi restrito — garante que os limites de mascaramento façam sentido.
- **Decodificação BIOES**: Esquema de tagging (Begin, Inside, Outside, End, Single) para extrair spans multi-token limpos.

## Arquitetura (comparada com nosso SLM)

| Aspecto | Nosso SLM (TinyStories) | Privacy Filter |
|---|---|---|
| Tarefa | Geração (next-token prediction) | Classificação (token labeling) |
| Direção | Unidirecional causal | Bidirecional |
| Inferência | Autorregressiva (N forward passes) | Uma única forward pass |
| Parâmetros | ~15M | 1.5B total / 50M ativos |
| Saída | Sequência gerada | Labels + spans mascarados |
| Treinamento | Cross-entropy em next-token | Classificação supervisionada de tokens |

## Conexão com o que já aprendemos

O Privacy Filter confirma e estende o insight central do wiki:

> Restrição de domínio permite reduzir o modelo. A diferença aqui é que o "domínio" não é o dado de treinamento (como no TinyStories) — é a própria tarefa. Em vez de treinar um modelo geral para detectar PII, você treina um modelo minúsculo especializado só nisso.

Isso abre um padrão: **pré-treinar um LLM genérico, depois adaptar para uma tarefa estreita**. O modelo mantém o "entendimento de linguagem" do pré-treinamento e ganha especialização com fine-tuning barato.

## Conceitos Introduzidos

- [Token Classification](../concepts/token-classification.md)
- [Bidirectional vs Autoregressive](../concepts/bidirectional-vs-autoregressive.md)
- [Viterbi Decoding](../concepts/viterbi-decoding.md)
- [BIOES Tagging](../concepts/bioes-tagging.md)
- [Fine-tuning Efficiency](../concepts/fine-tuning-efficiency.md)

## Entidades Mencionadas

- [OpenAI Privacy Filter](../entities/openai-privacy-filter.md)
- [PII-Masking-300k Benchmark](../entities/pii-masking-300k.md)

## Exemplos de mascaramento

**Entrada:**
```
Olá Jordan, confirmar que o lançamento está previsto para 18 de setembro de 2026.
Responda em maya.chen@example.com ou ligue em +1 (415) 555-0124.
Maya Chen
```

**Saída:**
```
Olá [PRIVATE_PERSON], confirmar que o lançamento está previsto para [PRIVATE_DATE].
Responda em [PRIVATE_EMAIL] ou ligue em [PRIVATE_PHONE].
[PRIVATE_PERSON]
```
