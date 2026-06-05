---
type: concept
tags: [decoding, spans, sequence-labeling, inference]
sources: 2
updated: 2026-05-02
---

# Viterbi Decoding

## Definition

Um algoritmo de programação dinâmica para encontrar a sequência de estados mais provável num modelo de Markov oculto (HMM). No contexto de token classification, é usado para garantir que a sequência de tags produzida pelo modelo seja válida — sem transições impossíveis como `B → B` (começar um novo span sem terminar o anterior).

## How It Works

O classificador de tokens produz probabilidades independentes para cada posição:
```
token[0]: {O: 0.95, B-PII: 0.05}
token[1]: {O: 0.10, B-PII: 0.40, I-PII: 0.50}
token[2]: {O: 0.20, I-PII: 0.30, E-PII: 0.50}
```

Sem restrições, o argmax de cada posição poderia produzir sequências inválidas como `O → I-PII → E-PII` (Inside sem Begin).

O Viterbi aplica uma **matriz de transição** que define quais sequências são válidas:
```
O       → O, B-PII, S-PII        (OK)
B-PII   → I-PII, E-PII           (OK)
B-PII   → O, B-PII               (INVÁLIDO — span aberto)
I-PII   → I-PII, E-PII           (OK)
E-PII   → O, B-PII, S-PII        (OK)
S-PII   → O, B-PII, S-PII        (OK)
```

Então encontra o caminho de maior probabilidade que respeita essas restrições — garantindo spans bem-formados.

## Relevância

Para o nosso SLM gerador (TinyStories), não usamos Viterbi — geração autorregressiva não produz sequências de tags, então não há problema de coerência de spans. Mas se quisermos adaptar o modelo para tarefas de classificação estruturada no futuro, Viterbi é a técnica padrão para pós-processamento.

## Related Concepts

- [BIOES Tagging](bioes-tagging.md)
- [Token Classification](token-classification.md)
- [Inference Loop](inference-loop.md)

## Sources

- [OpenAI Privacy Filter](../sources/2026-05-02-openai-privacy-filter.md)
