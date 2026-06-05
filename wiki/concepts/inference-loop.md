---
type: concept
tags: [inference, generation, sampling, autoregressive]
sources: 1
updated: 2026-05-02
---

# Inference Loop (Autoregressive Generation)

## Definition

The process of generating new tokens one at a time by repeatedly feeding the model's own output back as input. Each call generates one token; the loop continues until the desired length is reached.

## How It Works

The `GPT.generate()` method:
```python
@torch.no_grad()
def generate(self, idx, max_new_tokens, temperature=1.0, top_k=None):
    for _ in range(max_new_tokens):
        # Crop context to block_size
        idx_cond = idx if idx.size(1) <= self.config.block_size else idx[:, -self.config.block_size:]
        
        # Forward pass (inference mode: only compute logits for last token)
        logits, _ = self(idx_cond)
        logits = logits[:, -1, :] / temperature  # (B, vocab_size)
        
        # Top-k filtering
        if top_k is not None:
            v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
            logits[logits < v[:, [-1]]] = -float('Inf')
        
        # Sample next token
        probs = F.softmax(logits, dim=-1)
        idx_next = torch.multinomial(probs, num_samples=1)
        
        # Append and continue
        idx = torch.cat((idx, idx_next), dim=1)
    return idx
```

**Efficiency:** During inference, the model only needs logits for the *last* token (the new one), not all tokens. The code handles this:
```python
# Training: compute logits for all positions
logits = self.lm_head(x)           # (B, T, vocab_size)
# Inference: compute logits only for last position
logits = self.lm_head(x[:, [-1], :])  # (B, 1, vocab_size)
```

**Temperature:** Dividing logits by temperature > 1.0 makes the distribution flatter (more random), < 1.0 makes it sharper (more deterministic).

**Top-k:** Restricts sampling to the top-k most likely tokens, setting all others to `-inf` before softmax. Prevents very unlikely tokens from being sampled. Typical values: top_k=40 or top_k=50.

**Example usage:**
```python
sentence = "Once upon a time there was a pumpkin."
context = torch.tensor(enc.encode_ordinary(sentence)).unsqueeze(0)
y = model.generate(context, max_new_tokens=200)
print(enc.decode(y.squeeze().tolist()))
```

## Why It Matters

Autoregressive generation is how all GPT-style models produce text. Each token depends on all previous tokens — the model is conditioned on its own past outputs. Temperature and top-k are the main knobs to control output diversity.

## Related Concepts

- [Attention Mechanism](attention-mechanism.md)
- [Cross-Entropy Loss](cross-entropy-loss.md)
- [GPT2 Tokenizer](../entities/gpt2-tokenizer.md)

## Sources

- [Building a Small Language Model from Scratch](../sources/2026-05-02-building-slm-from-scratch.md)
