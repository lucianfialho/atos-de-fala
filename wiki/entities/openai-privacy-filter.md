---
type: entity
tags: [model, pii, privacy, openai, open-weights]
sources: 2
updated: 2026-05-02
---

# OpenAI Privacy Filter

## What It Is

Modelo open-weights da OpenAI para detecção e mascaramento de PII em texto. Classificador bidirecional de tokens com 1.5B parâmetros totais e 50M ativos. Disponível sob licença Apache 2.0 no Hugging Face e GitHub.

## Significance

Exemplo concreto do princípio "domínio restrito → modelo menor → performance de fronteira". Com 50M parâmetros ativos, alcança F1 de 96% em detecção de PII — tarefa para a qual modelos gerais precisariam de muito mais parâmetros.

## Key Facts

- **Parâmetros totais:** 1.5B (checkpoint pré-treinado autorregressivo)
- **Parâmetros ativos:** 50M (cabeça de classificação especializada)
- **Contexto:** até 128.000 tokens
- **Benchmark:** F1 96% no PII-Masking-300k
- **Fine-tuning:** F1 vai de 54% → 96% com poucos dados de domínio
- **Arquitetura:** Bidirecional, classificação de tokens, decodificação BIOES + Viterbi
- **8 categorias:** private_person, private_address, private_email, private_phone, private_url, private_date, account_number, secret
- **Licença:** Apache 2.0
- **Disponível em:** Hugging Face, GitHub

## Sources

- [OpenAI Privacy Filter](../sources/2026-05-02-openai-privacy-filter.md)
