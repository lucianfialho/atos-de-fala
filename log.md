# Log

Append-only history of sessions. Each entry: `## [YYYY-MM-DD] <type> | <title>`

## [2026-06-04] update | Wiki seeded from myFirstSmallModel (fine-tuning subset)
Instanciado o padrão LLM-Wiki (Karpathy) no projeto chomsky. Portado de `myFirstSmallModel` o subconjunto de finetuning/language-models: 21 conceitos (arquitetura transformer, training, fine-tuning, datasets), 12 entidades (datasets/modelos/tools de treino) e 6 sources (SLM-from-scratch + Privacy Filter BR build/plan/execution). Deixado de fora todo o tooling de agente (skills, atomic-gates, MCP, dev-pipeline). Criados SCHEMA.md, index.md, log.md e wiki/overview.md novos, adaptados ao chomsky. Workflow de ingestão de papers documentado no SCHEMA. Thesis específica do chomsky ainda TBD; overview preserva as theses portáveis e perguntas em aberto.

<!-- Original ingest history from myFirstSmallModel (for provenance) -->
## [2026-05-02] ingest | Building a Small Language Model from Scratch
Ingested video transcript + Colab notebook + Python file. 15M param GPT em TinyStories.
## [2026-05-02] ingest | OpenAI Privacy Filter
Blog post sobre o Privacy Filter da OpenAI. Restrição de tarefa habilita modelos menores com performance de fronteira.
## [2026-05-03] ingest | OpenAI Privacy Filter Model Card (PDF)
Paper técnico oficial (21 págs). 10% dos dados satura F1 0.962; opf CLI faz fine-tuning sem LoRA manual.
## [2026-05-06] build | Privacy Filter BR — Pipeline + Fine-tuning + Late competitor discovery
Fork BR do Privacy Filter: 11k sintéticos, LoRA head 33→53, F1 0.97 holdout interno. Concorrentes descobertos tarde (arthrod, OpenMed). Lições em 4 conceitos novos.
## [2026-05-07] plan | Privacy Filter BR v2 — B2B Specialization
Reposicionar v2 como especialista B2B; dataset arthrod (914k) + 50-100k B2B novos via MiniMax.
## [2026-05-16] build | Privacy Filter BR v2 — Execução com bugs + multi-provider
13→19 categorias, 14→18 templates. Multi-provider Claude CLI + MiniMax paralelos. 6 bugs documentados.

## [2026-06-04] build | Annotation Core (Plan 1)
Implementado o núcleo de anotação do classificador de atos de fala: schema (Span/Annotation), taxonomy + BIOES labels (config-driven), resolve de quotes→offsets, validator, BIOES tagger, agreement gate e span-F1 evaluator. ~27 testes, lógica pura sem APIs/GPU. Taxonomia provisória de 12 atos (49 labels) em config/taxonomy.yaml, a congelar na Fase 1.
