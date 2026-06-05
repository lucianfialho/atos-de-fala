---
type: concept
tags: [embedding, architecture, representation]
sources: 1
updated: 2026-05-02
---

# Token Embedding

## Definition

A lookup table that maps each token ID to a dense vector of fixed dimension (`n_embd`). Each token gets a learnable vector representation that the model updates during training.

## How It Works

The token embedding matrix has shape `(vocab_size, n_embd)` = `(50257, 384)` in this project. Given a token ID (e.g. `42`), the embedding is just row 42 of this matrix — a `nn.Embedding` lookup:

```python
self.transformer.wte = nn.Embedding(config.vocab_size, config.n_embd)
tok_emb = self.transformer.wte(idx)  # idx: (B, T) → tok_emb: (B, T, 384)
```

All values are initialized as Gaussian noise (mean=0, std=0.02) and updated via backprop. Over training, semantically similar tokens cluster together in the 384-dimensional space.

**Weight tying:** In this implementation, the token embedding weight matrix is shared with the output head (lm_head):
```python
self.transformer.wte.weight = self.lm_head.weight
```
This means the same matrix is used both to look up input embeddings and to project hidden states to logits. It reduces parameters and forces the input and output representations to be consistent.

## Why It Matters

Token embeddings are the model's only way to assign meaning to raw token IDs before processing. The quality of these representations strongly affects downstream performance. They are the most parameter-heavy component: `50257 × 384 ≈ 19M` parameters, which is a large fraction of this model's ~15M total.

## Related Concepts

- [Tokenization](tokenization.md)
- [Positional Embedding](positional-embedding.md)
- [Transformer Block](transformer-block.md)

## Sources

- [Building a Small Language Model from Scratch](../sources/2026-05-02-building-slm-from-scratch.md)
