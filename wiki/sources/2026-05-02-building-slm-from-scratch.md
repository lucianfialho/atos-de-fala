---
type: source
tags: [slm, architecture, training, tokenization, attention, gpt]
sources: 1
updated: 2026-05-02
---

# Building a Small Language Model from Scratch

**URL:** https://www.youtube.com/watch?v=pOFcwcwtv3k
**Author:** Dr. Raj Gandekar (PhD MIT), Vizuara AI Labs
**Type:** video (2.5 hours) + Colab notebook + Python file
**Date ingested:** 2026-05-02

## Summary

A full end-to-end tutorial for building a 15M parameter GPT-style language model from scratch using the TinyStories dataset. The video covers every component of the pipeline: dataset loading, tokenization, input/output batch creation, model architecture (transformer blocks with causal self-attention), loss function, training loop with production-grade optimizations, and inference.

The model uses GPT2's BPE tokenizer (vocab_size=50257), a context window of 128 tokens, 6 transformer blocks, 6 attention heads, and an embedding dimension of 384. Trained for 20,000 iterations on an A100 GPU (25-30 min), it achieves a training loss of ~2.39 and can generate coherent short stories from a prompt.

The notebook is explicitly inspired by Andrej Karpathy's nanoGPT repository, particularly the data preparation and training loop sections.

## Key Takeaways

- Small language models work when the training data is domain-constrained — TinyStories covers full English grammar with ~2M stories for 3-4 year olds.
- A 15M parameter model can generate grammatically coherent (though not always semantically perfect) stories after 20k iterations.
- Production-quality training requires: memory-mapped `.bin` files (avoids RAM overload), mixed precision (bfloat16/float16), gradient accumulation (effective batch of 1024 with GPU fitting only 32), and a warmup+cosine LR schedule.
- Weight tying between `wte` (token embedding) and `lm_head` (output projection) reduces parameters and improves training stability.
- Causal self-attention prevents the model from looking at future tokens — elements above the diagonal in the attention matrix are set to `-inf` before softmax.
- The training objective is purely next-token prediction (cross-entropy loss), yet the model learns grammar and story structure as a byproduct.

## Model Config (exact values from code)

```python
GPTConfig(
    vocab_size=50257,
    block_size=128,
    n_layer=6,
    n_head=6,
    n_embd=384,
    dropout=0.1,
    bias=True
)
```

## Training Config (exact values)

```python
learning_rate = 1e-4
max_iters = 20000
warmup_steps = 1000
min_lr = 5e-4
eval_iters = 500
batch_size = 32
block_size = 128
gradient_accumulation_steps = 32
optimizer = AdamW(betas=(0.9, 0.95), weight_decay=0.1, eps=1e-9)
```

## Pipeline Steps

1. Load TinyStories dataset from HuggingFace (`roneneldan/TinyStories`)
2. Tokenize with GPT2 BPE tokenizer (tiktoken), store as `train.bin` / `validation.bin` (memory-mapped numpy uint16)
3. `get_batch()` samples random chunks of `block_size` tokens → input `x` and `y = x shifted right by 1`
4. Model: token emb + positional emb → dropout → N transformer blocks → LayerNorm → lm_head → logits
5. Loss: cross-entropy between logits and targets (flattened)
6. Training loop: forward → loss/gradient_accumulation_steps → backward → accumulate N steps → clip grads (max_norm=0.5) → optimizer step → scheduler step
7. Inference: `model.generate()` with temperature scaling and top-k sampling

## Concepts Introduced

- [Tokenization (BPE)](../concepts/tokenization.md)
- [Token Embedding](../concepts/token-embedding.md)
- [Positional Embedding](../concepts/positional-embedding.md)
- [Attention Mechanism](../concepts/attention-mechanism.md)
- [Feed-Forward Network](../concepts/feed-forward-network.md)
- [Transformer Block](../concepts/transformer-block.md)
- [Cross-Entropy Loss](../concepts/cross-entropy-loss.md)
- [Gradient Accumulation](../concepts/gradient-accumulation.md)
- [Mixed Precision Training](../concepts/mixed-precision-training.md)
- [Inference Loop](../concepts/inference-loop.md)

## Entities Mentioned

- [TinyStories Dataset](../entities/tiny-stories-dataset.md)
- [GPT2 Tokenizer](../entities/gpt2-tokenizer.md)
- [nanoGPT](../entities/nano-gpt.md)
- [AdamW Optimizer](../entities/adamw-optimizer.md)
- [Google Colab](../entities/google-colab.md)
- [Vizuara AI Labs](../entities/vizuara-ai-labs.md)

## Notable Code

```python
# Weight tying — lm_head reuses token embedding weights
self.transformer.wte.weight = self.lm_head.weight

# Causal mask via Flash Attention (or manual triangular mask fallback)
if self.flash:
    y = F.scaled_dot_product_attention(q, k, v, is_causal=True)
else:
    att = att.masked_fill(self.bias[:,:,:T,:T] == 0, float('-inf'))
    att = F.softmax(att, dim=-1)
    y = att @ v

# Gradient accumulation + grad clipping
loss = loss / gradient_accumulation_steps
scaler.scale(loss).backward()
if ((epoch + 1) % gradient_accumulation_steps == 0):
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
    scaler.step(optimizer)
```
