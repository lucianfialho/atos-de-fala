---
type: concept
tags: [training, optimization, memory, gpu]
sources: 1
updated: 2026-05-02
---

# Gradient Accumulation

## Definition

A technique to simulate a larger effective batch size by accumulating gradients over multiple forward-backward passes before updating model parameters. Used when the desired batch size doesn't fit in GPU memory.

## How It Works

```python
gradient_accumulation_steps = 32  # accumulate for 32 mini-batches
batch_size = 32                    # each mini-batch has 32 sequences

# effective batch size = 32 × 32 = 1024 sequences per update
```

Training loop:
```python
for epoch in range(max_iters):
    X, y = get_batch("train")
    with ctx:  # autocast
        logits, loss = model(X, y)
        loss = loss / gradient_accumulation_steps  # scale down
        scaler.scale(loss).backward()             # accumulate gradients

    if ((epoch + 1) % gradient_accumulation_steps == 0) or (epoch + 1 == max_iters):
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
        scaler.step(optimizer)   # parameter update
        scaler.update()
        optimizer.zero_grad(set_to_none=True)
```

**Why divide the loss?** Without dividing by `gradient_accumulation_steps`, the accumulated gradients would be 32× larger than a single-batch update — effectively multiplying the learning rate by 32. Dividing keeps the effective gradient magnitude consistent.

**Gradient clipping:** After accumulation, `clip_grad_norm_(max_norm=0.5)` prevents any single update from being too large, stabilizing training.

## Why It Matters

Without gradient accumulation, you'd need a GPU with enough memory for batch_size=1024. With accumulation, you can achieve the same effective batch size with batch_size=32 (32× less memory). Larger effective batches produce smoother gradient estimates, which generally improves training stability.

## Related Concepts

- [Mixed Precision Training](mixed-precision-training.md)
- [Cross-Entropy Loss](cross-entropy-loss.md)

## Sources

- [Building a Small Language Model from Scratch](../sources/2026-05-02-building-slm-from-scratch.md)
