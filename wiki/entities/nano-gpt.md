---
type: entity
tags: [reference, gpt, karpathy, open-source]
sources: 1
updated: 2026-05-02
---

# nanoGPT

## What It Is

A minimal, clean reimplementation of GPT by Andrej Karpathy (former Tesla AI Director, OpenAI researcher). GitHub: `karpathy/nanoGPT`. Widely used as a pedagogical reference for understanding GPT architecture.

## Significance

The Vizuara tutorial explicitly credits nanoGPT as its primary inspiration. Specifically, the data preparation logic (`prepare.py`) and training loop structure are adapted from nanoGPT with modifications for readability and the TinyStories use case.

## Key Facts

- **Author:** Andrej Karpathy
- **Repo:** `https://github.com/karpathy/nanoGPT`
- **What was borrowed for this project:**
  - `process()` tokenization function (from `data/openwebtext/prepare.py`)
  - Memory-mapped `.bin` file format for token storage
  - `get_batch()` function structure (from `train.py`)
  - Overall model class structure (`GPT`, `Block`, `CausalSelfAttention`, `MLP`, `LayerNorm`)
- **Key differences from nanoGPT:** Smaller config (384 embd, 6 layers, 6 heads), TinyStories dataset, more explicit training loop with gradient accumulation exposed

## Sources

- [Building a Small Language Model from Scratch](../sources/2026-05-02-building-slm-from-scratch.md)
