# Design — Classificador de Atos de Fala por Span (PT-BR)

**Projeto:** chomsky
**Data:** 2026-06-04
**Status:** Aprovado no brainstorming; pendente review do spec antes do plano de implementação.

## Objetivo

Construir um modelo que **decompõe um texto em PT-BR em segmentos e classifica a intenção
(ato de fala) de cada segmento** em uma única passada. Entrada: texto livre. Saída: spans
rotulados com atos de fala (ex.: *afirmar, perguntar, pedir, sugerir, prometer, concordar...*).

Exemplo conceitual:
```
"Bom dia! Você pode me enviar o relatório? Prometo revisar até amanhã."
 └─ SAUDAR ──┘ └──── PEDIR ───────────────┘ └──── PROMETER ──────────┘
```

## Não-objetivos (v1)

- **Spans sobrepostos / aninhados.** v1 usa BIO plano → spans não-sobrepostos. Atos aninhados
  no mesmo trecho ficam para v2 (multi-label / layered tagging).
- **Taxonomia ISO 24617-2 completa.** v1 usa um conjunto reduzido (~10-12 atos), congelado na Fase 1.
- **Inferência via LLM em produção.** O LLM é teacher/anotador, não o modelo final.
- **Fundamentação chomskyana no modelo.** Chomsky entra no wiki como contexto conceitual, não
  como sinal de treino — a base teórica do modelo é pragmática / atos de fala (Searle, Austin)
  e dialogue act classification.

## Abordagem: A + C (destilação)

- **A — Modelo final:** BERTimbau (`neuralmind/bert-base-portuguese-cased`) + cabeça de
  **token classification** + **LoRA**. Marca limite do span E o ato numa só forward pass.
  Mesma forma arquitetural do Privacy Filter BR (PII → atos de fala).
- **C — Teacher:** LLM gera e anota os dados; o BERTimbau (student) destila esse conhecimento.
  Teacher de qualidade = teto do aluno.

### Teacher: mistura Claude + MiniMax

| Papel | Modelo | Justificativa |
|---|---|---|
| Rúbrica de anotação + 30-50 exemplos gold (few-shot) | Claude | Precisão em pragmática PT-BR e em seguir taxonomia |
| Geração + anotação em volume (bulk) | MiniMax | Throughput e custo baixo |
| Adjudicação de divergências + holdout de eval | Claude | Árbitro de qualidade onde importa |

**Gate de concordância:** um subconjunto de overlap é anotado por ambos; mede-se concordância de
span/label; itens divergentes são descartados ou adjudicados por Claude. Só dados de alta
concordância (ou adjudicados) entram no treino. Cf. [Kill-My-Idea / validação](../../../wiki/concepts/competitive-research-discipline.md).

**Gotchas do MiniMax já documentados** — reusar, não redescobrir:
[multi-provider-generation](../../../wiki/concepts/multi-provider-generation.md)
(reasoning queima `max_tokens` em thinking; erros engolidos sem `DEBUG=1`; plano Starter sem highspeed).

## Esquema de labels (BIOES)

`O` ∪ `{B,I,E,S} × {atos}`. Para N atos → `4N + 1` classes. Com ~12 atos → ~49 classes
(coincide com a escala do Privacy Filter BR: head 33→53). Decodificação de sequência válida via
[Viterbi](../../../wiki/concepts/viterbi-decoding.md) opcional no pós-processamento.

## Taxonomia candidata (provisória — congelar na Fase 1 a partir dos papers)

Base Searle (assertivo / diretivo / compromissivo / expressivo / declarativo) expandida com atos
úteis do ISO 24617-2 reduzido. Ponto de partida (~12):
`afirmar, perguntar, pedir, sugerir, prometer, agradecer, concordar, discordar, saudar,
despedir, informar, expressar_emoção`. A lista final sai da Fase 0.

## Plano faseado

### Fase 0 — Pesquisa & ingestão (paper7 → wiki)
Buscar e ingerir no wiki (workflow do `SCHEMA.md`): speech act theory (Searle/Austin), dialogue
act classification neural, ISO 24617-2, RST / discourse segmentation, BERTimbau & NLP-PT,
span-based dialogue act, + Chomsky (contexto). Cada paper vira `raw/sources/` + `wiki/sources/`
+ conceitos/entidades + overview + index + log.
**Saída:** 6-10 source pages; taxonomia decidida com o usuário.
**Bloqueio atual:** arXiv retornando "Rate exceeded" no IP — re-tentar após cooldown.

### Fase 1 — Congelar taxonomia + esquema BIOES
**Saída:** `wiki/concepts/speech-act-label-scheme.md` com a lista de atos, definições, exemplos
PT-BR e o mapa de labels BIOES.

### Fase 2 — Pipeline sintético
`Claude (rúbrica + gold)` → `MiniMax (bulk: gera texto PT aberto + anota spans)` →
`validator (span verbatim + legalidade de label BIOES)` → `gate de concordância` →
`BIOES auto-labeler` → `JSONL (train/holdout)`. Reusa
[synthetic-data-generation](../../../wiki/concepts/synthetic-data-generation.md),
[br-pii-dataset-pipeline](../../../wiki/concepts/br-pii-dataset-pipeline.md),
[multi-provider-generation](../../../wiki/concepts/multi-provider-generation.md).
Disciplina de resume-from-disk com `flush()` por exemplo.
**Alvo MVP:** alguns milhares de exemplos (curados > volume, cf. lição do Privacy Filter BR).

### Fase 3 — Fine-tune
BERTimbau + token-classification head + LoRA no Colab A100. Reusar
[lora-fine-tuning-pitfalls](../../../wiki/concepts/lora-fine-tuning-pitfalls.md):
`.cuda()` antes de `get_peft_model()`; head em `dtype=float32`; nome exato da head em
`modules_to_save`; sanity check de NaN antes de treinar. Mixed precision + grad accumulation
conforme [overview](../../../wiki/overview.md).
**Saída:** modelo treinado + métricas.

### Fase 4 — Eval & iterar
**Span-level F1** (não token accuracy) + breakdown por ato, em holdout revisado por humano
(Claude-assisted). Matriz de confusão entre atos próximos (ex.: pedir vs sugerir). Iterar dados
nos atos fracos.

## Componentes e interfaces

| Unidade | Faz | Depende de |
|---|---|---|
| `annotation_rubric` | Define atos + regras + few-shot gold | taxonomia (Fase 1) |
| `generator` (MiniMax) | Produz texto PT + anotação de spans (JSON) | rúbrica, API MiniMax |
| `validator` | Checa span verbatim + label BIOES legal | esquema de labels |
| `agreement_gate` | Concordância dupla-anotação; adjudica via Claude | validator, Claude API |
| `bioes_labeler` | Converte spans → tags BIOES por token | tokenizer BERTimbau |
| `trainer` | Fine-tune LoRA token-cls | dataset JSONL, Colab |
| `evaluator` | Span-F1, breakdown, confusão | holdout |

## Riscos & mitigações

- **Teacher erra pragmática sutil** → gate de concordância + adjudicação Claude + holdout humano.
- **arXiv rate-limit** → cooldown / re-tentar; paper7 também suporta `--source pubmed`.
- **Atos próximos confundem (pedir/sugerir/perguntar)** → exemplos contrastivos na geração; medir na confusão.
- **Distribuição sintética ≠ texto real** → holdout com texto real (não-sintético) na Fase 4.
- **BIO plano não cobre aninhamento** → assumido fora de escopo v1; documentado.

## Integração com o wiki

O projeto roda dentro do wiki existente. Papers → `raw/` + `wiki/sources/`. Conceitos novos
(speech-act-theory, dialogue-act-classification, rst-discourse-segmentation, bertimbau,
speech-act-label-scheme) → `wiki/concepts/`. Build logs do dataset e do treino → `wiki/sources/`.
`overview.md`, `index.md`, `log.md` atualizados a cada passo, conforme `SCHEMA.md`.

## Critério de sucesso (v1)

Modelo BERTimbau que, dado texto PT-BR aberto, segmenta em spans não-sobrepostos e atribui um ato
de fala a cada um, com span-F1 razoável (alvo a definir após baseline) num holdout com texto real
revisado por humano.
