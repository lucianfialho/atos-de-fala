---
type: concept
tags: [attention, architecture, transformer, causal]
sources: 1
updated: 2026-05-02
---

# Attention Mechanism (Causal Self-Attention)

## Definition

A mechanism that transforms each token's embedding into a context-aware representation by computing weighted sums over all previous tokens in the sequence. "Self" = attends to tokens within the same sequence. "Causal" = cannot see future tokens.

## How It Works

The `CausalSelfAttention` class applies multi-head attention. For each head:

1. **Project to Q, K, V:** A single linear layer projects the input to 3× width, then splits:
   ```python
   self.c_attn = nn.Linear(n_embd, 3 * n_embd)
   q, k, v = self.c_attn(x).split(n_embd, dim=2)
   # Reshape to (B, n_head, T, head_dim) where head_dim = n_embd / n_head = 64
   ```

2. **Compute attention scores:** Scaled dot product of Q and K:
   ```
   scores = (Q @ K^T) / sqrt(head_dim)  →  (B, n_head, T, T)
   ```

3. **Apply causal mask:** Set elements above the diagonal to `-inf` so softmax makes them 0:
   ```python
   # Manual fallback (when Flash Attention unavailable):
   att = att.masked_fill(self.bias[:,:,:T,:T] == 0, float('-inf'))
   att = F.softmax(att, dim=-1)
   ```

4. **Flash Attention shortcut** (used when `F.scaled_dot_product_attention` is available):
   ```python
   y = F.scaled_dot_product_attention(q, k, v, is_causal=True)
   ```

5. **Weighted sum over V:**
   ```python
   y = att @ v  # (B, n_head, T, head_dim)
   y = y.transpose(1,2).contiguous().view(B, T, n_embd)  # reassemble heads
   ```

6. **Output projection + dropout:**
   ```python
   y = self.resid_dropout(self.c_proj(y))
   ```

**Multi-head:** With `n_head=6` and `n_embd=384`, each head operates on `384/6=64` dimensions. Multiple heads allow the model to attend to different aspects of the context simultaneously.

## Why It Matters

Without attention, a language model has no way to connect distant tokens. Attention enables the model to learn that "it" refers to "dog" (or "ball") even 10 tokens earlier. The causal constraint is essential for autoregressive generation — at inference time, the model must predict the next token without access to future context.

## Related Concepts

- [Token Embedding](token-embedding.md)
- [Transformer Block](transformer-block.md)
- [Inference Loop](inference-loop.md)

## Sources

- [Building a Small Language Model from Scratch](../sources/2026-05-02-building-slm-from-scratch.md)
