# Wiki Index

Seeded from `myFirstSmallModel` on 2026-06-04 — fine-tuning / language-model subset only.

## Sources
- [Building a Small Language Model from Scratch](wiki/sources/2026-05-02-building-slm-from-scratch.md) — End-to-end tutorial for a 15M param GPT on TinyStories (Vizuara AI Labs, 2026)
- [OpenAI Privacy Filter](wiki/sources/2026-05-02-openai-privacy-filter.md) — Open-weights PII detection model; 50M active params, F1 96%; bidirectional token classifier
- [OpenAI Privacy Filter — Model Card](wiki/sources/2026-05-03-openai-privacy-filter-model-card.md) — Paper técnico: arquitetura, training procedure, fine-tuning efficiency (10% dados → F1 0.962), opf CLI
- [Privacy Filter BR Build Process](wiki/sources/2026-05-06-privacy-filter-br-build.md) — Build log: 11k synthetic, F1 0.97, late-discovered competitors, lições
- [Privacy Filter BR v2 Plan](wiki/sources/2026-05-07-privacy-filter-br-v2-plan.md) — Plano v2 B2B-focused: arthrod dataset + B2B docs novos via MiniMax
- [Privacy Filter BR v2 Execution Log](wiki/sources/2026-05-16-privacy-filter-br-v2-execution.md) — Bugs encontrados, multi-provider parallel, lições da execução real

## Concepts

### Architecture
- [Tokenization](wiki/concepts/tokenization.md) — BPE subword tokenization; text → uint16 token IDs em .bin
- [Token Embedding](wiki/concepts/token-embedding.md) — Lookup table token ID → 384-dim; weight-tied com lm_head
- [Positional Embedding](wiki/concepts/positional-embedding.md) — Learned position vectors; block_size=128
- [Attention Mechanism](wiki/concepts/attention-mechanism.md) — Causal multi-head self-attention (6 heads, 64 dim/head)
- [Feed-Forward Network](wiki/concepts/feed-forward-network.md) — Position-wise MLP: 384→1536→384 GELU
- [Transformer Block](wiki/concepts/transformer-block.md) — Pre-LN block: LN→Attn→LN→MLP + residual; 6 blocks
- [Cross-Entropy Loss](wiki/concepts/cross-entropy-loss.md) — Next-token prediction loss; final ~2.39
- [Inference Loop](wiki/concepts/inference-loop.md) — Autoregressive generation com temperature e top-k

### Training
- [Gradient Accumulation](wiki/concepts/gradient-accumulation.md) — Accumula 32 steps; effective batch=1024
- [Mixed Precision Training](wiki/concepts/mixed-precision-training.md) — bf16/fp16 autocast + GradScaler; ~2× em A100

### Fine-tuning & Task Adaptation
- [Fine-tuning Efficiency](wiki/concepts/fine-tuning-efficiency.md) — Adaptar modelos pré-treinados a tarefas estreitas com pouco dado
- [LoRA Fine-tuning Pitfalls](wiki/concepts/lora-fine-tuning-pitfalls.md) — PEFT gotchas: CUDA wrapping, dtype mismatch, modules_to_save naming
- [Specialization vs Generalization](wiki/concepts/specialization-vs-generalization.md) — Quando treinar especialista (1-10k) vs generalista (100k+)
- [Token Classification](wiki/concepts/token-classification.md) — Rotular cada token numa forward pass; contraste com next-token prediction
- [Bidirectional vs Autoregressive](wiki/concepts/bidirectional-vs-autoregressive.md) — BERT-style vs GPT-style; quando usar cada
- [BIOES Tagging](wiki/concepts/bioes-tagging.md) — Span tagging scheme pra extração de entidades multi-token
- [Viterbi Decoding](wiki/concepts/viterbi-decoding.md) — DP pra decodificação de sequência de tags válida
- [Speech Act Label Scheme](wiki/concepts/speech-act-label-scheme.md) — BIOES label set (O ∪ {B,I,E,S}×atos) derivado de config/taxonomy.yaml; 12 atos provisórios → 49 labels

### Datasets & Data Generation
- [Synthetic Data Generation](wiki/concepts/synthetic-data-generation.md) — 4devs + LLM rewrite + auto-labeling pra NER em domínio estreito
- [BR PII Dataset Pipeline](wiki/concepts/br-pii-dataset-pipeline.md) — Pipeline 4devs → variants → templates → LLM → validate → label, com custos reais
- [Multi-Provider Generation](wiki/concepts/multi-provider-generation.md) — Claude CLI + MiniMax paralelos pro mesmo dataset, gotchas comuns
- [Competitive Research Discipline](wiki/concepts/competitive-research-discipline.md) — Sempre buscar HF/GitHub ANTES de construir modelo novo

## Entities
- [TinyStories Dataset](wiki/entities/tiny-stories-dataset.md) — 2.1M GPT-4 generated children's stories; domain-restricted corpus
- [GPT2 Tokenizer](wiki/entities/gpt2-tokenizer.md) — BPE tokenizer via tiktoken; vocab_size=50,257
- [nanoGPT](wiki/entities/nano-gpt.md) — Karpathy's minimal GPT; primary code inspiration
- [AdamW Optimizer](wiki/entities/adamw-optimizer.md) — AdamW β₂=0.95, wd=0.1; warmup+cosine
- [Google Colab](wiki/entities/google-colab.md) — Training env; A100=30min, T4=6-8h
- [Vizuara AI Labs](wiki/entities/vizuara-ai-labs.md) — Tutorial author (Dr. Raj Gandekar, MIT PhD)
- [OpenAI Privacy Filter](wiki/entities/openai-privacy-filter.md) — 1.5B total / 50M active PII model; Apache 2.0
- [opf CLI](wiki/entities/opf-cli.md) — CLI oficial; `opf train` fine-tuna, `opf redact` infere
- [SPY Dataset](wiki/entities/spy-dataset.md) — Dataset sintético médico/legal do eval; 10% → F1 0.962
- [4devs API](wiki/entities/4devs-api.md) — Gerador BR de PII sintético (CPF/CNPJ/RG/IE/etc)
- [arthrod/gliner-opf-ptbr-pii-v1](wiki/entities/arthrod-privacy-filter-ptbr.md) — Concorrente PT-BR, 914k samples, F1 0.885, sem CNPJ/IE específicos
- [OpenMed Privacy Filter Multilingual](wiki/entities/openmed-privacy-filter-multilingual.md) — Privacy Filter multilingual (16 línguas, PT incluso)

## Synthesis
- [Overview](wiki/overview.md) — Portable theses, reference recipe, open questions
