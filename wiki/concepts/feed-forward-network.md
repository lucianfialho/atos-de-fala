---
type: concept
tags: [mlp, architecture, transformer, gelu]
sources: 1
updated: 2026-05-02
---

# Feed-Forward Network (MLP)

## Definition

A position-wise two-layer neural network applied to each token independently after the attention step. It expands the representation to 4× the embedding dimension, applies a nonlinearity, then projects back.

## How It Works

The `MLP` class:
```python
class MLP(nn.Module):
    def __init__(self, config):
        self.c_fc   = nn.Linear(n_embd, 4 * n_embd)  # 384 → 1536
        self.gelu   = nn.GELU()
        self.c_proj = nn.Linear(4 * n_embd, n_embd)  # 1536 → 384
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x):
        return self.dropout(self.c_proj(self.gelu(self.c_fc(x))))
```

**Expansion factor:** 4× is standard in transformer MLPs. It gives the network a higher-dimensional space to learn complex patterns before projecting back. For this model: `384 × 4 = 1536` hidden units.

**GELU activation:** Unlike ReLU (which is zero below 0), GELU has a smooth, differentiable curve at zero and allows small negative values. In practice, GELU consistently outperforms ReLU for language models.

**Position-wise:** The MLP is applied identically to every token position — there's no mixing of information between positions at this step (that happens in attention).

## Why It Matters

Empirically, transformers without the MLP perform much worse. The attention mechanism captures relationships *between* tokens; the MLP captures non-linear transformations *within* each token's representation. Together, they allow the model to both understand context and reason about individual token meanings.

## Related Concepts

- [Transformer Block](transformer-block.md)
- [Attention Mechanism](attention-mechanism.md)

## Sources

- [Building a Small Language Model from Scratch](../sources/2026-05-02-building-slm-from-scratch.md)
