# Remote Runbook — Train on your own NVIDIA box over Tailscale

This is the **primary** training path for chomsky (replaces the Colab runbook). Everything —
synthetic generation, training, and evaluation — runs on a remote **NVIDIA CUDA Linux** machine
reached over Tailscale SSH. Only the code is pushed from the laptop; the dataset is generated on
the box.

Set your Tailscale host once (MagicDNS name or 100.x IP):

```bash
REMOTE=user@your-box.tailnet-name.ts.net      # e.g. lucian@gpu.tailnet.ts.net
REMOTE_DIR=~/chomsky
```

## 1. Push the code (rsync over Tailscale SSH)

The repo has no git remote, so sync the working tree. Excludes the venv, caches, and any local
generated data (the dataset is regenerated on the box). `raw/` (incl. the Porttinari holdout) and
`config/` ARE sent — they're needed for eval and the rubric/taxonomy.

```bash
# run from the repo root on the laptop
rsync -avz --delete \
  --exclude '.venv/' --exclude '.git/' --exclude '__pycache__/' \
  --exclude '*.egg-info/' --exclude '.pytest_cache/' --exclude 'data/' \
  ./ "$REMOTE:$REMOTE_DIR/"
```

## 2. One-time environment setup (on the box)

```bash
ssh "$REMOTE"
cd ~/chomsky
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
# On Linux+NVIDIA the default PyPI torch wheels are CUDA builds:
pip install -e ".[dev,gen,ml]"
# sanity:
python -c "import torch; print('cuda available:', torch.cuda.is_available(), torch.version.cuda)"
pytest -q   # expect the full suite green; model/train smokes now RUN (torch present)
```
If `cuda available` is False, install a matching CUDA wheel, e.g.:
`pip install torch --index-url https://download.pytorch.org/whl/cu124`.

## 3. Generate the dataset (on the box; needs API keys + internet)

```bash
export DEEPSEEK_API_KEY=...        # bulk teacher (cheap)
export ANTHROPIC_API_KEY=...       # Claude adjudicator
python -m chomsky.gen.cli \
  --provider deepseek --n 10000 \
  --out data/dataset.jsonl \
  --cross-check-rate 0.15 --debug
```
Per-act balancing is on by default (steers toward ~n/13 of each act). Resume-safe: re-run the same
command to continue if interrupted. Tip: run under `tmux`/`nohup` so it survives SSH drops —
`nohup python -m chomsky.gen.cli ... > gen.log 2>&1 < /dev/null &` (lesson from Privacy Filter BR:
redirect stdin/stdout and watch disk).

## 4. Anti-NaN sanity check before training (wiki: lora-fine-tuning-pitfalls #5)

```bash
python - <<'PY'
import torch
from chomsky.train.model import build_model, apply_lora
from chomsky.taxonomy import load_taxonomy
tax = load_taxonomy("config/taxonomy.yaml")
m, tok = build_model("neuralmind/bert-base-portuguese-cased", tax)
m = m.cuda()                      # .cuda() BEFORE apply_lora (pitfall #1)
m = apply_lora(m)
m.eval()
with torch.no_grad():
    x = tok("teste de sanidade", return_tensors="pt").to("cuda")
    assert not torch.isnan(m(**x).logits).any(), "NaN logits — fix before training"
print("sanity OK")
PY
```

## 5. Train (uses CUDA automatically)

```bash
python -m chomsky.train.train \
  --train data/dataset.jsonl --out runs/sa-lora \
  --epochs 5 --batch-size 16 --lr 2e-4
```
`train.py` picks `cuda` when available (no `--cpu`). For bf16 on Ampere+ you can extend
TrainingArguments with `bf16=True` if desired. Watch disk for logs.

## 6. Evaluate on the real Porttinari holdout (span-F1; uses GPU if present)

```bash
python -m chomsky.train.porttinari --out data/porttinari-holdout.jsonl
python -m chomsky.train.eval_cli --model runs/sa-lora --holdout data/porttinari-holdout.jsonl
```
`eval_cli` now moves the model to CUDA automatically. **Caveat:** Porttinari gold is sentence-level
while the model predicts finer spans, so exact span-F1 understates quality — read it as a
sentence-level signal (a dedicated sentence-level eval mode is a sensible follow-up).

## 7. Pull artifacts back to the laptop (optional)

```bash
# from the laptop
rsync -avz "$REMOTE:$REMOTE_DIR/runs/sa-lora/" ./runs/sa-lora/
rsync -avz "$REMOTE:$REMOTE_DIR/data/dataset.jsonl" ./data/
```
`runs/` and `data/` are gitignored (the model + dataset are artifacts, not source).

## Notes

- The laptop is disk-constrained, which is why ml deps are NOT installed locally; the box owns the
  heavy stack. Pure-logic + offline tests still run on the laptop.
- Generation can also run on the laptop (light, network-only) if you'd rather keep keys there and
  only rsync `data/dataset.jsonl` up — but running it on the box keeps everything in one place.
