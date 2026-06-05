---
type: concept
tags: [architecture, classification, nlp, token-labeling]
sources: 2
updated: 2026-05-02
---

# Token Classification

## Definition

Uma tarefa de NLP onde cada token de uma sequência recebe um rótulo de uma taxonomia fixa. Diferente de next-token prediction (gera o próximo token), token classification atribui uma classe a cada token existente na entrada.

## How It Works

A arquitetura substitui a cabeça de modelagem de linguagem (lm_head) por uma cabeça de classificação:

```
# Modelo gerador (nosso SLM):
hidden_states (B, T, n_embd) → lm_head → logits (B, T, vocab_size)
# next token = argmax do último logit

# Modelo classificador (Privacy Filter):
hidden_states (B, T, n_embd) → classification_head → labels (B, T, n_classes)
# cada token recebe um rótulo: PRIVATE_PERSON, PRIVATE_EMAIL, O (Outside), etc.
```

**Passada única:** Todos os tokens são classificados simultaneamente em uma forward pass. Não há loop de geração — é fundamentalmente mais rápido.

**Vantagem de ser bidirecional:** O classificador pode ver toda a sequência antes de rotular cada token. O contexto à direita ajuda a decidir se "João" é um nome privado ou parte de um nome de lugar público.

## Aplicações Relevantes

- Detecção de PII (Privacy Filter)
- Named Entity Recognition (NER)
- Part-of-speech tagging
- Chunking de texto

## Contraste com Next-Token Prediction

| | Next-Token Prediction | Token Classification |
|---|---|---|
| Objetivo | Gerar sequência | Rotular sequência |
| Passes | N passes (um por token gerado) | 1 pass |
| Direção | Unidirecional (causal) | Bidirecional |
| Saída | Texto gerado | Labels por token |
| Uso | Chatbots, geração | NER, PII, PoS |

## Related Concepts

- [Attention Mechanism](attention-mechanism.md)
- [Bidirectional vs Autoregressive](bidirectional-vs-autoregressive.md)
- [BIOES Tagging](bioes-tagging.md)
- [Inference Loop](inference-loop.md)

## Sources

- [OpenAI Privacy Filter](../sources/2026-05-02-openai-privacy-filter.md)
