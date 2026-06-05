---
type: concept
tags: [synthetic-data, llm, parallelism, pipeline, cost-optimization]
sources: 1
updated: 2026-05-16
---

# Multi-Provider Synthetic Generation

## Definition

Padrão de geração de dataset sintético usando **múltiplos LLM providers em paralelo**, todos apendando ao mesmo arquivo de output. Combina latência/throughput de provedores diferentes pra acelerar geração sem dobrar consumo de um único provedor.

## Why It Works

Cada provider tem trade-off diferente:

| Provider | Velocidade | Custo | Quota |
|---|---|---|---|
| Claude CLI (subscription) | ~5-10s/call | $0/call (subscription) | 5h rolling window |
| Anthropic API (Sonnet) | ~3s/call | $$$ | Tokens |
| MiniMax M2.7 | ~30s/call (thinking) | $/$$ | Cota plano |
| Local GLM via proxy | ~76s/call (thinking) | $0 | RAM da máquina |

Rodar **2 providers em paralelo**:
- Dobra throughput sem dobrar custo de um único
- Adiciona diversidade de estilo no dataset
- Tolerância a falha (se um cai, outro continua)

## Implementation

### Provider-aware Generator

`HaikuGenerator` aceita flag `--provider` que escolhe entre Claude CLI ou MiniMax API:

```python
class HaikuGenerator:
    def __init__(self, provider: str = "claude", **kwargs):
        self.provider = (provider or os.getenv("PROVIDER", "claude")).lower()

    def generate(self, template_name, context):
        prompt = render_prompt(template_name, context)
        if self.provider == "minimax":
            return self._generate_minimax(prompt)
        return self._generate_claude(prompt)
```

### Parallel Execution (Same Output File)

Dois processos `nohup` apontando pra mesma `data/output.jsonl`. O `generate_dataset.py` usa `with open(..., "a")` (append) e file locks via threading:

```bash
# Terminal 1
nohup python3 scripts/generate_dataset.py --workers 3 --provider claude \
    --output data/dataset.jsonl > data/run_claude.log 2>&1 &

# Terminal 2
nohup python3 scripts/generate_dataset.py --workers 5 --provider minimax \
    --output data/dataset.jsonl > data/run_minimax.log 2>&1 &
```

### Resume Coordination

Ambos checam `wc -l data/dataset.jsonl` no início. Quando o arquivo atingir `--n` total, **ambos param** (independente de quem escreveu mais).

## Gotchas

### 1. Env var conflicts entre providers
Se `.env` tem `ANTHROPIC_API_KEY=placeholder`, **claude CLI quebra**. Solução: strip API keys do subprocess env quando rodando subscription-mode CLI.

### 2. Reasoning models gastam max_tokens em thinking
M2.7, GLM4.7, etc emitem `<think>...</think>` antes da resposta. Precisa:
- `max_tokens=4096` mínimo
- Strip blocks no post-processing
- Timeout maior (~120s)

### 3. Quotas diferentes
- Anthropic subscription: rolling 5h window
- API tokens: hard limit por mês
- MiniMax Starter: 0/0 pra modelos high-end
Monitor cada uma separadamente.

### 4. File lock no append paralelo
`open(file, "a")` + `f.flush()` é ATOMICAMENTE seguro pra writes < 4KB no Linux/macOS. Pra writes maiores, precisa de `fcntl.flock` explícito ou queue.

## When To Use

✅ Geração de dataset grande sob restrição de tempo
✅ Acesso a múltiplos providers (subscription + API)
✅ Tolerância a downtime de provider único
✅ Quando diversidade de estilo no dataset agrega

❌ Quando 1 provider dá conta do throughput
❌ Quando o output precisa de estilo consistente
❌ Quando coordenação adiciona mais complexidade que ganho

## Related Concepts

- [Synthetic Data Generation](synthetic-data-generation.md)
- [LoRA Fine-tuning Pitfalls](lora-fine-tuning-pitfalls.md)

## Sources

- [Privacy Filter BR v2 Execution](../sources/2026-05-16-privacy-filter-br-v2-execution.md)
