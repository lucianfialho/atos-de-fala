---
type: concept
tags: [tokenization, bpe, preprocessing, nlp]
sources: 1
updated: 2026-05-02
---

# Tokenization

## Definition

Converting raw text into a sequence of integer token IDs that a language model can process. Tokenization is the first transformation in the data pipeline — the model never sees raw text, only token IDs.

## How It Works

Three strategies exist, each with trade-offs:

| Strategy | Unit | Problem |
|---|---|---|
| Word-based | Each word = 1 token | Vocabulary explosion (500k+ words); OOV for typos |
| Character-based | Each char = 1 token | Sequences too long; attention window fills up fast |
| **Subword (BPE)** | Mix of chars, words, subwords | **Best balance** — used in GPT2, this project |

**Byte Pair Encoding (BPE):** An algorithm that starts with individual characters and repeatedly merges the most frequent adjacent pairs until the vocabulary reaches a target size. Rare words get split into subwords (e.g. "tokenization" → "token" + "ization"); common words stay whole.

In this project: GPT2's BPE tokenizer via `tiktoken`:
```python
enc = tiktoken.get_encoding("gpt2")
ids = enc.encode_ordinary(text)  # ignores special tokens
```

Token IDs are stored as `uint16` (max value 50256 fits in 2 bytes) in memory-mapped `.bin` files:
```python
arr = np.memmap('train.bin', dtype=np.uint16, mode='w+', shape=(total_tokens,))
```

## Why It Matters

The vocabulary size (50,257 for GPT2) directly determines the size of:
- The token embedding matrix: `vocab_size × n_embd` = `50257 × 384` = ~19M parameters
- The output head (lm_head): same shape — but weight-tied to save parameters

A larger vocab means fewer tokens per sentence (efficient attention) but more parameters. GPT2's 50k is a practical sweet spot.

## Related Concepts

- [Token Embedding](token-embedding.md)
- [Transformer Block](transformer-block.md)

## Sources

- [Building a Small Language Model from Scratch](../sources/2026-05-02-building-slm-from-scratch.md)
