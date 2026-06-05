---
type: concept
tags: [training, optimization, gpu, performance]
sources: 1
updated: 2026-05-02
---

# Mixed Precision Training

## Definition

Training with a mix of float32 and lower-precision (float16/bfloat16) arithmetic. Lower-precision operations run 2-4× faster on modern GPUs and use half the memory, while float32 is retained for numerically sensitive operations.

## How It Works

```python
dtype = 'bfloat16' if torch.cuda.is_bf16_supported() else 'float16'
ptdtype = {'float32': torch.float32, 'bfloat16': torch.bfloat16, 'float16': torch.float16}[dtype]
ctx = torch.amp.autocast(device_type='cuda', dtype=ptdtype)

# Wrap forward pass in autocast context
with ctx:
    logits, loss = model(X, y)
```

**What gets cast to lower precision:** Matrix multiplications (attention scores, linear layers), activations, most element-wise ops. These are safe in float16/bfloat16.

**What stays in float32:** Softmax, cross-entropy loss, weight updates. These involve exponentials or logarithms that can overflow/underflow in float16.

**GradScaler** (for float16 only): Scales the loss up before backward pass to prevent float16 underflow in gradients, then unscales before the optimizer step:
```python
scaler = torch.cuda.amp.GradScaler(enabled=(dtype == 'float16'))
scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```
bfloat16 doesn't need a GradScaler because it has better dynamic range than float16 (same exponent bits as float32, fewer mantissa bits).

## Why It Matters

On an A100, bfloat16 matrix multiplications run ~2× faster than float32. For a 20,000-iteration training run, this halves wall-clock time (from ~60 min to ~30 min). Memory savings also allow larger batch sizes.

## Related Concepts

- [Gradient Accumulation](gradient-accumulation.md)
- [Google Colab](../entities/google-colab.md)

## Sources

- [Building a Small Language Model from Scratch](../sources/2026-05-02-building-slm-from-scratch.md)
