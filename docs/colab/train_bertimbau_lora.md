# Colab Runbook — BERTimbau LoRA (speech-act span classifier)

> **Primary path is now `docs/remote/train_tailscale.md`** (train on our own NVIDIA box over
> Tailscale; dataset generated there too). Keep this Colab runbook as a fallback.

Target: Colab A100. Mirrors the Privacy Filter BR setup; applies wiki lora-fine-tuning-pitfalls.

## Steps
1. Runtime → Change runtime type → A100 GPU.
2. Clone the repo and install:
   ```bash
   pip install -q -e ".[ml]"
   ```
3. Upload `data/dataset.jsonl` (from Plan 2) and a `data/holdout.jsonl`.
4. Sanity check BEFORE training (avoid NaN — pitfall #5):
   ```python
   import torch
   from chomsky.train.model import build_model, apply_lora
   from chomsky.taxonomy import load_taxonomy
   tax = load_taxonomy("config/taxonomy.yaml")
   m, tok = build_model("neuralmind/bert-base-portuguese-cased", tax)
   m = m.cuda(); m = apply_lora(m)  # .cuda() BEFORE apply_lora (pitfall #1)
   m.eval()
   with torch.no_grad():
       x = tok("teste", return_tensors="pt").to("cuda")
       assert not torch.isnan(m(**x).logits).any(), "NaN logits — fix before training"
   ```
5. Train:
   ```bash
   python -m chomsky.train.train \
     --train data/dataset.jsonl --out runs/sa-lora \
     --epochs 5 --batch-size 16 --lr 2e-4
   ```
6. Evaluate (span-F1):
   ```bash
   python -m chomsky.train.eval_cli --model runs/sa-lora --holdout data/holdout.jsonl
   ```
7. Watch for the documented gotchas: Transformers API churn (`eval_strategy`, `processing_class`),
   disk filling from logs (redirect + rotate), and head/target names (`classifier`, `query`/`value`).
