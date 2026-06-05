---
title: Chomsky Speech Acts PT-BR
emoji: 🗣️
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# chomsky — classificador de atos de fala (PT-BR)

Decompõe um texto em português e classifica a **intenção (ato de fala)** de cada trecho.

- **Modelo:** BERTimbau (`neuralmind/bert-base-portuguese-cased`) + LoRA, treinado como
  token-classifier BIOES.
- **Dados:** sintéticos, destilados de um teacher LLM (DeepSeek chat + reasoner), balanceados por ato.
- **Taxonomia (13 atos):** ISO 24617-2 + Searle — informar, perguntar, concordar, discordar,
  pedir, sugerir, oferecer, prometer, saudar, agradecer, desculpar, despedir, expressar_emocao.

O adapter LoRA está embutido em `adapter/`; o BERTimbau base é baixado do Hub em runtime.

## Rodar local
```bash
pip install -r requirements.txt
python app.py
```
