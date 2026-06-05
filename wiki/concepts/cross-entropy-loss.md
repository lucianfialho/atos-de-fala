---
type: concept
tags: [loss, training, next-token-prediction]
sources: 1
updated: 2026-05-02
---

# Cross-Entropy Loss

## Definition

The training objective for language models. Measures how well the model's predicted probability distribution over the vocabulary matches the true next token. Minimizing cross-entropy is equivalent to maximizing the probability of the true next token.

## How It Works

After passing a batch through the model, we get a logits tensor of shape `(B, T, vocab_size)`. The loss is computed as:

```python
loss = F.cross_entropy(
    logits.view(-1, logits.size(-1)),  # flatten to (B*T, vocab_size)
    targets.view(-1),                  # flatten to (B*T,)
    ignore_index=-1
)
```

**What this computes:** For each of the `B*T` positions, it looks at the target token ID, finds the model's predicted probability for that token (after softmax), and takes the negative log: `loss = -log(p_correct)`. The total loss is the mean over all positions.

**Interpretation:** A loss of 2.39 (this model's final loss) means the model assigns average probability `e^(-2.39) ≈ 0.091` to the correct next token. A random model over 50k tokens would have loss `log(50257) ≈ 10.8`.

**Per-batch:** Each batch has `batch_size × block_size = 32 × 128 = 4096` next-token prediction tasks. The loss during gradient accumulation is divided by `gradient_accumulation_steps` before backprop:

```python
loss = loss / gradient_accumulation_steps
scaler.scale(loss).backward()
```

## Why It Matters

Cross-entropy is the canonical loss for classification — and next-token prediction is a 50,257-class classification at every position. It penalizes overconfident wrong predictions heavily (via the log), which pushes the model to assign high probability to the correct token.

## Related Concepts

- [Transformer Block](transformer-block.md)
- [Gradient Accumulation](gradient-accumulation.md)
- [Inference Loop](inference-loop.md)

## Sources

- [Building a Small Language Model from Scratch](../sources/2026-05-02-building-slm-from-scratch.md)
