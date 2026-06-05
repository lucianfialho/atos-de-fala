---
type: entity
tags: [optimizer, training, regularization]
sources: 1
updated: 2026-05-02
---

# AdamW Optimizer

## What It Is

An extension of the Adam optimizer that decouples weight decay from the gradient update, providing better regularization. Standard choice for training language models.

## Significance

Used in this project's training loop with a warmup + cosine decay learning rate schedule. The specific hyperparameters (betas, weight decay, eps) match nanoGPT's recommended settings.

## Key Facts

- **Config in this project:**
  ```python
  optimizer = torch.optim.AdamW(
      model.parameters(),
      lr=1e-4,
      betas=(0.9, 0.95),   # beta2=0.95 (vs Adam default 0.999)
      weight_decay=0.1,
      eps=1e-9
  )
  ```
- **beta2=0.95:** Lower than Adam's default (0.999). Less memory of past gradients — better for language models where gradient landscapes change fast.
- **weight_decay=0.1:** L2 regularization. Prevents parameters from growing too large.
- **LR schedule:**
  ```python
  scheduler_warmup = LinearLR(optimizer, total_iters=1000)
  scheduler_decay  = CosineAnnealingLR(optimizer, T_max=19000, eta_min=5e-4)
  scheduler = SequentialLR([scheduler_warmup, scheduler_decay], milestones=[1000])
  ```
  Ramps from 0 to `1e-4` over 1000 steps, then cosine-decays to `5e-4` over the remaining 19000 steps.

## Sources

- [Building a Small Language Model from Scratch](../sources/2026-05-02-building-slm-from-scratch.md)
