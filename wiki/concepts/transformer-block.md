---
type: concept
tags: [transformer, architecture, residual, layer-norm]
sources: 1
updated: 2026-05-02
---

# Transformer Block

## Definition

The core repeating unit of a GPT-style model. Each block applies layer normalization, causal self-attention, another layer normalization, and a feed-forward network — all with residual (skip) connections.

## How It Works

The `Block` class:
```python
class Block(nn.Module):
    def __init__(self, config):
        self.ln1  = LayerNorm(n_embd, bias=True)
        self.attn = CausalSelfAttention(config)
        self.ln2  = LayerNorm(n_embd, bias=True)
        self.mlp  = MLP(config)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))   # residual + attention
        x = x + self.mlp(self.ln2(x))    # residual + MLP
        return x
```

**Pre-LN architecture:** LayerNorm is applied *before* the attention and MLP (not after, as in the original "Attention Is All You Need" paper). Pre-LN stabilizes training for deeper models.

**Residual connections:** `x = x + f(x)` lets gradients flow directly from output back to input, bypassing the sub-layer. This prevents vanishing gradients in stacked layers.

**Stacking:** This model uses `n_layer=6` transformer blocks. The input embeddings pass through all 6 blocks sequentially, each refining the token representations:
```python
self.transformer.h = nn.ModuleList([Block(config) for _ in range(config.n_layer)])
for block in self.transformer.h:
    x = block(x)
```

**Output:** After 6 blocks, a final LayerNorm + lm_head projects each token to logits over the vocabulary:
```python
x = self.transformer.ln_f(x)        # (B, T, 384)
logits = self.lm_head(x)            # (B, T, 50257)
```

## Why It Matters

The transformer block is where all the learning happens. Each layer progressively builds more abstract representations — early layers capture syntax, later layers capture semantics. 6 layers is small by modern standards (GPT-3 has 96) but sufficient for the TinyStories domain.

## Related Concepts

- [Attention Mechanism](attention-mechanism.md)
- [Feed-Forward Network](feed-forward-network.md)
- [Cross-Entropy Loss](cross-entropy-loss.md)

## Sources

- [Building a Small Language Model from Scratch](../sources/2026-05-02-building-slm-from-scratch.md)
