---
type: entity
tags: [tokenizer, bpe, gpt2, tiktoken]
sources: 1
updated: 2026-05-02
---

# GPT2 Tokenizer

## What It Is

OpenAI's byte-pair encoding tokenizer, trained on WebText. Vocabulary of 50,257 tokens. Available via the `tiktoken` library. Used in this project to tokenize the TinyStories dataset.

## Significance

Using GPT2's tokenizer (rather than training a custom one) avoids the computational cost of BPE training on TinyStories. The vocabulary is slightly oversized for the domain (TinyStories uses simple words, so many tokens will be rare), but the tradeoff is acceptable.

## Key Facts

- **Vocabulary size:** 50,257 tokens
- **Algorithm:** Byte Pair Encoding (BPE)
- **Library:** `tiktoken` (OpenAI's fast tokenization library)
- **Usage in project:**
  ```python
  enc = tiktoken.get_encoding("gpt2")
  ids = enc.encode_ordinary(text)  # no special tokens
  text = enc.decode(token_ids)
  ```
- **Token ID range:** 0–50,256 (fits in `uint16`, max value 65,535)
- **Memory impact:** Token embedding matrix = `50257 × 384 ≈ 19M parameters`

## Sources

- [Building a Small Language Model from Scratch](../sources/2026-05-02-building-slm-from-scratch.md)
