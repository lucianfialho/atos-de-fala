---
type: entity
tags: [infrastructure, gpu, cloud, training]
sources: 1
updated: 2026-05-02
---

# Google Colab

## What It Is

Google's hosted Jupyter notebook service with free and paid GPU access. Used in this project as the training environment.

## Significance

The tutorial was designed and tested on Google Colab. Understanding the GPU tiers matters for estimating training time.

## Key Facts

| GPU | Plan | Training time (20k iters) |
|---|---|---|
| A100 | Pro (~$10/month) | ~25-30 minutes |
| L4 | Pro | ~25-30 minutes |
| T4 | Free | ~6-8 hours |
| CPU | — | Will fail (OOM) |

- **Colab link:** `https://colab.research.google.com/drive/1k4G3G5MxYLxawmPfAknUN7dbbmyqldQv`
- **Runtime config:** Change runtime type to T4/A100 under Runtime → Change runtime type
- **Memory note:** Training produces `train.bin` (~200MB) and `validation.bin` (~2MB). These are stored on Colab's ephemeral disk.
- **Model save:** Best model parameters saved to `best_model_params.pt` during training for later reload.

## Sources

- [Building a Small Language Model from Scratch](../sources/2026-05-02-building-slm-from-scratch.md)
