---
type: concept
tags: [tagging, ner, spans, token-classification]
sources: 2
updated: 2026-05-02
---

# BIOES Tagging

## Definition

Um esquema de rotulagem para marcar spans multi-token em sequências. BIOES = **B**egin, **I**nside, **O**utside, **E**nd, **S**ingle. Produz limites de mascaramento mais limpos do que esquemas mais simples como BIO.

## How It Works

Para um span "maya.chen@example.com" rotulado como PRIVATE_EMAIL:

```
maya         → B-PRIVATE_EMAIL   (Begin)
.            → I-PRIVATE_EMAIL   (Inside)
chen         → I-PRIVATE_EMAIL   (Inside)
@            → I-PRIVATE_EMAIL   (Inside)
example      → I-PRIVATE_EMAIL   (Inside)
.            → I-PRIVATE_EMAIL   (Inside)
com          → E-PRIVATE_EMAIL   (End)
```

Para um span de token único "Jordan" rotulado como PRIVATE_PERSON:
```
Jordan       → S-PRIVATE_PERSON  (Single)
```

Para tokens fora de qualquer span:
```
Olá          → O                 (Outside)
,            → O
```

**Por que BIOES é melhor que BIO?** O tag `E` (End) e `S` (Single) tornam os limites do span explícitos — o decodificador sabe exatamente onde o span termina sem ambiguidade.

## Viterbi para Spans Coerentes

As previsões por token podem ser inconsistentes (ex: `B` seguido de outro `B` sem `E` no meio). O algoritmo de Viterbi resolve isso aplicando restrições de transição válidas — só permite sequências de tags que formam spans bem formados.

## Related Concepts

- [Token Classification](token-classification.md)
- [Viterbi Decoding](viterbi-decoding.md)

## Sources

- [OpenAI Privacy Filter](../sources/2026-05-02-openai-privacy-filter.md)
