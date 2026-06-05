---
type: entity
tags: [cli, privacy-filter, fine-tuning, inference, tool]
sources: 2
updated: 2026-05-03
---

# opf CLI

## What It Is

CLI oficial do OpenAI Privacy Filter. Ferramenta de linha de comando para rodar inferência, fine-tuning e calibração do modelo. Instalado junto com o Privacy Filter via HuggingFace/pip.

## Significance

Elimina a necessidade de implementar o loop de fine-tuning manualmente para o Privacy Filter BR. O `opf train` aceita um arquivo `dataset.jsonl` e executa o fine-tuning com LoRA automaticamente.

## Key Facts

```bash
# Redação básica
opf redact "João Silva (CPF 123.456.789-09) mora em São Paulo"
# → "[PRIVATE_PERSON] (CPF [ACCOUNT_NUMBER]) mora em São Paulo"

# Output anotado com labels coloridos
opf redact --output-mode annotated "texto..."

# Colapsa todos os labels em um só
opf redact --output-mode redacted "texto..."

# Fine-tuning em dataset customizado
opf train --output-dir finetuned/ dataset.jsonl

# Ajuste do operating point (tradeoff precision/recall via Viterbi)
opf redact --help
opf train --help
```

**Formato do dataset.jsonl:** a estrutura exata para `opf train` precisa ser confirmada via `opf train --help`. Baseado no modelo card, deve seguir BIOES span annotations.

## Implicação para Privacy Filter BR

Fase 2 do projeto (fine-tuning) se resume a:
1. Gerar `dataset_br.jsonl` com o pipeline 4devs + Haiku (Fase 1)
2. Rodar `opf train --output-dir privacy-filter-br/ dataset_br.jsonl`
3. Distribuir o diretório `privacy-filter-br/` como o adapter BR

## Sources

- [OpenAI Privacy Filter Model Card](../sources/2026-05-03-openai-privacy-filter-model-card.md)
- [OpenAI Privacy Filter](../sources/2026-05-02-openai-privacy-filter.md)
