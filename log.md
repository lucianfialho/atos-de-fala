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
## [2026-06-05] ingest | Fase 0 — papers + taxonomia congelada
arXiv API/paper7 ficou bloqueado (429 sustentado >4h); fiz a ingestão via WebFetch/download direto. Paper-chave: ISO 24617-2 (Bunt et al., LREC 2012, PDF em raw/sources). Ingeridos também BERTimbau (Souza et al. 2020) e Chomsky-vs-pragmática. Achado importante: **não existe dataset PT-BR de speech act em nível de span** (confirma a necessidade do sintético). **Taxonomia v1 CONGELADA**: 13 atos → 53 labels, fundamentada nas general-purpose + social-obligations functions do ISO 24617-2 mapeadas em Searle, adaptada pra texto PT-BR aberto (dimensões de controle de diálogo fora de escopo). config/taxonomy.yaml atualizado; suíte 30 testes verde.
## [2026-06-05] ingest | Geertzen, Petukhova & Bunt (LREC 2008) — DA tagging naive vs expert
Paper extra (raw em raw/sources) que VALIDA o v1: reduzir granularidade do tagset (DIT++→LIRICS) aumenta concordância, sobretudo pra não-experts; Turn/Feedback são difíceis de anotar (justifica termos descartado); Social Obligations + Task grosso são confiáveis (são o que mantivemos); pares confundíveis (inform×answer×elaborate×explain; instruct×answer) confirmam nossas fusões e viram guia da rúbrica do Plano 2. Sem mudança na taxonomia. Novo conceito: dialogue-act-annotation-reliability.
## [2026-06-05] ingest | Porttinari speech-acts (PROPOR 2024) — prior work PT-BR
Paper mais próximo do projeto (raw em raw/sources): 1º corpus PT-BR de speech acts (Porttinari, 536 notícias/4091 sentenças, ISO 24617-2, CC, sentence-level). Valida o v1 (13 classes ISO, mapeiam nas nossas). **Corrige finding anterior**: existe corpus PT-BR (sentence-level), mas nenhum span-level → granularidade nossa segue inédita, e o Porttinari vira holdout real do Plano 3. **Argumento pró-sintético reforçado**: inform=91% em notícia → macro-F1 deles só 29.5%, classes raras F1=0; nosso pipeline controla a distribuição. Regras de rúbrica adotadas (rótulo mais específico; descrever ato ≠ realizar ato). Nova entidade: porttinari-corpus.

## [2026-06-05] build | Generation Pipeline (Plan 2)
Executado o Plano 2 (subagent-driven, 8 tasks): prompts + parse robusto de JSON do LLM, clients HTTP MiniMax e Claude (parsing testável via requests monkeypatched), orquestração pura da mistura teacher (process_example com callables injetados), writer JSONL com fsync + resume, e CLI (`python -m chomsky.gen.cli`). Rúbrica CONGELADA em config/rubric.md com os 13 atos + regras dos papers da Fase 0 (rótulo mais específico; descrever ≠ realizar; pedido indireto = pedir; fusões). Suíte: 55 testes verde, tudo offline; smoke ao vivo (1 step) fica manual pq precisa de MINIMAX_API_KEY + ANTHROPIC_API_KEY. Saída do pipeline = JSONL de spans em offset (tokenização/BIOES no Plano 3).

## [2026-06-05] build | Training & Eval (Plan 3)
Implementado treino + avaliação: load_jsonl, align_labels e decoder BIOES→spans (lógica pura testada), model builder BERTimbau + LoRA (nomes BERT: classifier, query/value), train.py com HF Trainer (+ smoke CPU em bert-tiny) e eval CLI span-F1 reusando o evaluator do Plano 1. Runbook de Colab A100 com sanity check anti-NaN. Treino real depende de data/dataset.jsonl (Plano 2) e da taxonomia congelada (Fase 0).
## [2026-06-05] build | Conversor Porttinari CSV→JSONL
chomsky.train.porttinari: mapeia o corpus Porttinari (CSV sentence-level) → JSONL do chomsky, com 1 span cobrindo a sentença inteira e os 17 rótulos ISO mapeados nos nossos 13 atos (answer/correction→informar; instruct→pedir; compliment/congratulation/sympathy→expressar_emocao; confirm→concordar; disconfirm→discordar). Todos os 4091 rows mapeiam (0 unmapped). 5 testes (incl. integração no corpus real). Caveat documentado: granularidade sentence vs span — eval_cli (span-F1 exato) contra isso é sinal sentence-level, não span-F1 estrito. Suíte 75 passed + 2 skipped.
## [2026-06-05] build | Cliente DeepSeek + balanceamento por cota de ato
Adicionado DeepSeekClient (OpenAI-compatible, espelha o MiniMax) como bulk teacher alternativo, selecionável via `--provider {minimax,deepseek}` na CLI. DeepSeek é baratíssimo (~$1-3 por 10k exemplos) — o custo real continua sendo o adjudicador Claude. Balanceamento por cota: balance.act_counts + under_target_acts (puros), build_generation_prompt ganha focus_acts, dataset.load_done_annotations pra recontar no resume; a CLI injeta os ~3 atos mais sub-representados (alvo ≈ n/13) como foco a cada geração, `--no-balance` desliga. Ataca o desbalanceamento que travou o macro-F1 do Porttinari (0.295). +12 testes (deepseek, balance, prompts focus, dataset annotations). Suíte 87 passed + 2 skipped.
## [2026-06-05] update | Treino migra do Colab pra máquina própria (Tailscale)
Decisão: treino/geração/eval rodam na minha máquina NVIDIA CUDA (Linux) via Tailscale SSH, não no Colab. Geração roda na própria remota (só o código vai, via rsync — repo sem git remote). Criado docs/remote/train_tailscale.md (runbook: rsync → venv .[ml] CUDA → gerar com DeepSeek → sanity anti-NaN → treinar → eval). eval_cli passa a usar GPU automaticamente (model.cuda() se disponível). Colab runbook vira fallback. /runs/ gitignored.
## [2026-06-05] update | DeepSeek-only: adjudicador configurável (sem Anthropic)
Decisão: usar só DeepSeek, sem Anthropic. CLI ganhou `--adjudicator {deepseek,claude,none}` (default deepseek) + `--adjudicator-model` (default deepseek-reasoner); o cliente do adjudicador só é instanciado se escolhido (deepseek/none não exige ANTHROPIC_API_KEY). DeepSeek-only = deepseek-chat no bulk + deepseek-reasoner adjudicando. Tradeoff honesto documentado: adjudicação na mesma família é mais fraca que cross-family (Claude); o validator duro (taxonomia/verbatim/non-overlap) é o backstop. `none` = validator-only. Box revalidada antes: 90/90 com transformers 4.57.6. Runbook/wiki atualizados.
## [2026-06-05] feat | Geração concorrente (--concurrency)
Geração I/O-bound rodava sequencial (10k ~6-12h). Adicionado `--concurrency N` (default 1): ondas de N requisições em paralelo via ThreadPoolExecutor; coleta/escrita/contagem no thread principal (sem locks), foco de balanceamento recomputado por onda, dedup e resume preservados, erros por-exemplo isolados. ~N× mais rápido (10k → ~1h com 8). Esclarecido: DeepSeek não tem Batch API e batch seria mais LENTO (assíncrono/24h) — concorrência é o lever certo de velocidade. +2 testes (chega no n com concorrência; resume). Runbook usa --concurrency 8.
