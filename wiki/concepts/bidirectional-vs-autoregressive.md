---
type: concept
tags: [architecture, attention, bert, gpt, direction]
sources: 2
updated: 2026-05-02
---

# Bidirectional vs Autoregressive

## Definition

Dois paradigmas opostos de como um transformer processa uma sequência. Autorregressivo (GPT-style) só vê tokens anteriores. Bidirecional (BERT-style) vê todos os tokens simultaneamente.

## How It Works

**Autorregressivo (nosso SLM, GPT):**
- A máscara causal garante que o token na posição `t` só pode atender aos tokens `0..t`
- Necessário para geração: não pode "trapacear" vendo o futuro
- Treinado com next-token prediction
```python
# máscara causal — diagonal inferior
att = att.masked_fill(self.bias[:,:,:T,:T] == 0, float('-inf'))
```

**Bidirecional (BERT, Privacy Filter):**
- Sem máscara causal — cada token atende a todos os outros
- Melhor para compreensão/classificação: contexto completo disponível
- Treinado com masked language modeling ou classificação supervisionada

**O padrão do Privacy Filter:**
Começa de um checkpoint autorregressivo (mantém o conhecimento de linguagem do pré-treinamento) e adapta para bidirecional ao remover a máscara causal e trocar o objetivo de treinamento. Isso é possível porque a compreensão de linguagem é transferível.

## Por Que Importa para Este Wiki

O Privacy Filter mostra um padrão emergente:
1. Pré-treinar um LLM autorregressivo em corpus grande (conhecimento geral de linguagem)
2. Adaptar para classificador bidirecional em tarefa específica (fine-tuning barato)

Isso é mais eficiente do que treinar um BERT do zero para cada tarefa. O pré-treinamento autorregressivo pode ser reutilizado.

## Related Concepts

- [Attention Mechanism](attention-mechanism.md)
- [Token Classification](token-classification.md)
- [Fine-tuning Efficiency](fine-tuning-efficiency.md)

## Sources

- [OpenAI Privacy Filter](../sources/2026-05-02-openai-privacy-filter.md)
