---
type: concept
tags: [embedding, architecture, position, sequence]
sources: 1
updated: 2026-05-02
---

# Positional Embedding

## Definition

A learned vector added to each token embedding to give the model information about the position of each token in the sequence. Without positional information, the attention mechanism would treat all token orderings as equivalent.

## How It Works

The positional embedding matrix has shape `(block_size, n_embd)` = `(128, 384)`. Position `t` gets embedding `wpe[t]`:

```python
self.transformer.wpe = nn.Embedding(config.block_size, config.n_embd)

pos = torch.arange(0, t, dtype=torch.long, device=device)  # [0, 1, ..., t-1]
pos_emb = self.transformer.wpe(pos)  # (T, 384)

x = self.transformer.drop(tok_emb + pos_emb)  # element-wise addition
```

Both token embeddings and positional embeddings are Gaussian-initialized and learned end-to-end. This is the same approach used in GPT-2 (learned positional embeddings). An alternative is sinusoidal fixed positions (original Transformer), but learned positions generally perform better at fixed context lengths.

## Why It Matters

The self-attention mechanism computes relationships between all pairs of tokens but is inherently permutation-invariant — it doesn't know which token comes first. Positional embeddings break this symmetry, letting the model learn that position 0 is different from position 50.

The `block_size=128` sets the maximum context length. The model cannot attend beyond 128 tokens at inference time.

## Related Concepts

- [Token Embedding](token-embedding.md)
- [Attention Mechanism](attention-mechanism.md)

## Sources

- [Building a Small Language Model from Scratch](../sources/2026-05-02-building-slm-from-scratch.md)
