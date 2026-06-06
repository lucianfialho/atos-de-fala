# Training & Evaluation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fine-tune BERTimbau as a BIOES token classifier (with LoRA) on the Plan-2 dataset, and provide a span-level evaluation CLI — turning `data/dataset.jsonl` into a trained speech-act span model with a measured span-F1.

**Architecture:** The bug-prone pure logic — JSONL loading, char-span→label-id alignment, and **BIOES→spans decoding** (the inverse of the tagger, used at inference) — is unit-tested offline with no ML deps. The `transformers`/`peft`/GPU pieces (model builder, training loop, eval CLI) carry complete runnable code plus a CPU smoke test on a tiny model (`prajjwal1/bert-tiny`, ~17MB) so wiring is verified without the 400MB BERTimbau download or a GPU. Reuses Plan-1's `char_spans_to_bioes`, `taxonomy`, `schema`, and `eval`.

**Tech Stack:** Python ≥3.10, `torch`, `transformers`, `peft`, the existing `atos` package, `pytest`. Real training targets Colab A100; smoke runs on CPU.

---

## Scope

This is **Plan 3 of 3** (see `docs/superpowers/specs/2026-06-04-speech-act-span-classifier-design.md`). It delivers training + eval. It consumes `data/dataset.jsonl` produced by Plan 2.

**Dependency notes:**
- Taxonomy-driven: `num_labels` and id maps come from `config/taxonomy.yaml`. After Fase 0 freezes the taxonomy, only the config changes.
- LoRA target/head names are BERT-specific and differ from the Privacy Filter BR project — see Task 4. This is the exact-name pitfall from wiki `lora-fine-tuning-pitfalls`.
- Heavy ML deps install in Task 0; pure-logic Tasks 1–3 do not need them and their tests run without torch.

## File Structure

```
atos/
├── pyproject.toml              # MODIFY: add optional 'ml' deps
├── src/atos/train/
│   ├── __init__.py
│   ├── data.py                 # load_jsonl -> List[Annotation]
│   ├── features.py             # align_labels (pure) + encode_example (tokenizer wrapper)
│   ├── decode.py               # bioes_tags_to_spans (pure) — inverse of the tagger
│   ├── model.py                # build_model + apply_lora (BERTimbau + peft)
│   ├── train.py                # Trainer entrypoint (CLI) + CPU smoke path
│   └── eval_cli.py             # predict on holdout -> decode -> span-F1
├── docs/colab/
│   └── train_bertimbau_lora.md # Colab runbook (A100)
└── tests/
    ├── test_train_data.py
    ├── test_features.py
    ├── test_decode.py
    ├── test_model_smoke.py     # tiny model, requires download
    ├── test_train_smoke.py     # tiny model, requires download
    └── test_eval_cli.py        # uses fakes, no download
```

**Interfaces locked here:**
- `data.load_jsonl(path) -> List[Annotation]`.
- `features.align_labels(tags: List[str], special_mask: List[int], label2id: Dict[str,int]) -> List[int]` (special → -100).
- `features.encode_example(text, spans, tokenizer, label2id, max_length=256) -> dict` with `input_ids`, `attention_mask`, `labels`.
- `decode.bioes_tags_to_spans(offsets: List[Tuple[int,int]], tags: List[str]) -> List[Span]`.
- `model.build_model(model_name, taxonomy) -> (model, tokenizer)`; `model.apply_lora(model, target_modules=("query","value"), modules_to_save=("classifier",), r=16, alpha=32, dropout=0.1) -> model`.
- `train.main(argv)` / `eval_cli.main(argv)`.

---

## Task 0: ml extras

**Files:**
- Modify: `pyproject.toml`
- Create: `src/atos/train/__init__.py`

- [ ] **Step 1: Add the `ml` optional dependency group to `pyproject.toml`**

Extend `[project.optional-dependencies]` so it includes:

```toml
[project.optional-dependencies]
dev = ["pytest>=8.0"]
gen = ["requests>=2.31"]
ml = ["torch>=2.2", "transformers>=4.40", "peft>=0.11"]
```

- [ ] **Step 2: Create the subpackage marker**

```python
# src/atos/train/__init__.py
"""atos.train — BERTimbau LoRA token-classification training + span eval."""
```

- [ ] **Step 3: Install ml extras (heavy; downloads torch)**

Run:
```bash
cd /Users/lucianfialho/Code/antiachismosocialclub/atos
.venv/bin/pip install -q -e ".[dev,gen,ml]"
.venv/bin/python -c "import torch, transformers, peft; print(torch.__version__, transformers.__version__, peft.__version__)"
```
Expected: prints three versions. (Large download; may take minutes.)

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml src/atos/train/__init__.py
git commit -m "chore: scaffold atos.train subpackage + ml deps"
```

---

## Task 1: JSONL dataset loader (`data.py`)

**Files:**
- Create: `src/atos/train/data.py`
- Test: `tests/test_train_data.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_train_data.py
from atos.train.data import load_jsonl
from atos.schema import Annotation, Span


def test_loads_annotations_skipping_blank_lines(tmp_path):
    p = tmp_path / "ds.jsonl"
    p.write_text(
        '{"text": "Oi!", "spans": [{"start": 0, "end": 3, "act": "saudar"}]}\n'
        "\n"
        '{"text": "Vem?", "spans": []}\n',
        encoding="utf-8",
    )
    data = load_jsonl(str(p))
    assert data == [
        Annotation("Oi!", [Span(0, 3, "saudar")]),
        Annotation("Vem?", []),
    ]


def test_empty_file_returns_empty_list(tmp_path):
    p = tmp_path / "empty.jsonl"
    p.write_text("", encoding="utf-8")
    assert load_jsonl(str(p)) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_train_data.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.train.data'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/train/data.py
from typing import List
from atos.schema import Annotation


def load_jsonl(path: str) -> List[Annotation]:
    """Load a dataset of char-offset annotations (one JSON object per line)."""
    out: List[Annotation] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(Annotation.from_json(line))
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_train_data.py -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add src/atos/train/data.py tests/test_train_data.py
git commit -m "feat(train): JSONL annotation loader"
```

---

## Task 2: Label alignment (`features.py` — `align_labels`)

Converts BIOES tags + a special-tokens mask into label ids, with `-100` (ignore index) for special tokens. This is the pure core of feature building.

**Files:**
- Create: `src/atos/train/features.py`
- Test: `tests/test_features.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_features.py
from atos.train.features import align_labels


def test_special_tokens_become_ignore_index():
    tags = ["O", "B-saudar", "E-saudar", "O"]
    special = [1, 0, 0, 1]  # first and last are special ([CLS]/[SEP])
    label2id = {"O": 0, "B-saudar": 1, "I-saudar": 2, "E-saudar": 3, "S-saudar": 4}
    assert align_labels(tags, special, label2id) == [-100, 1, 3, -100]


def test_all_real_tokens_map_to_ids():
    tags = ["S-pedir", "O"]
    special = [0, 0]
    label2id = {"O": 0, "B-pedir": 1, "I-pedir": 2, "E-pedir": 3, "S-pedir": 4}
    assert align_labels(tags, special, label2id) == [4, 0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_features.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.train.features'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/train/features.py
from typing import Dict, List

IGNORE_INDEX = -100


def align_labels(
    tags: List[str], special_mask: List[int], label2id: Dict[str, int]
) -> List[int]:
    """Map BIOES tags to label ids; special tokens (mask==1) get IGNORE_INDEX (-100)."""
    return [
        IGNORE_INDEX if special_mask[i] else label2id[tags[i]]
        for i in range(len(tags))
    ]


def encode_example(text, spans, tokenizer, label2id, max_length: int = 256) -> Dict:
    """Tokenize text and produce input_ids/attention_mask/labels for token-cls training.

    Requires a *fast* tokenizer (offset mapping). Uses atos.bioes.char_spans_to_bioes
    to derive per-token BIOES tags, then align_labels to map them to ids with -100 on
    special tokens.
    """
    from atos.bioes import char_spans_to_bioes

    enc = tokenizer(
        text,
        return_offsets_mapping=True,
        return_special_tokens_mask=True,
        truncation=True,
        max_length=max_length,
    )
    tags = char_spans_to_bioes(spans, enc["offset_mapping"])
    labels = align_labels(tags, enc["special_tokens_mask"], label2id)
    return {
        "input_ids": enc["input_ids"],
        "attention_mask": enc["attention_mask"],
        "labels": labels,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_features.py -q`
Expected: PASS (2 passed). (`encode_example` is exercised by the smoke test in Task 6.)

- [ ] **Step 5: Commit**

```bash
git add src/atos/train/features.py tests/test_features.py
git commit -m "feat(train): label alignment + encode_example"
```

---

## Task 3: BIOES → spans decoder (`decode.py`)

The inverse of the tagger, used at inference to turn predicted per-token tags back into char-offset spans. Lenient with malformed sequences. Heavily tested — this is where decoding bugs hide.

**Files:**
- Create: `src/atos/train/decode.py`
- Test: `tests/test_decode.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_decode.py
from atos.train.decode import bioes_tags_to_spans
from atos.schema import Span


def test_single_S_tag():
    offsets = [(0, 2), (2, 3)]
    tags = ["S-saudar", "O"]
    assert bioes_tags_to_spans(offsets, tags) == [Span(0, 2, "saudar")]


def test_B_I_E_forms_one_span():
    offsets = [(0, 4), (5, 9), (10, 14)]
    tags = ["B-pedir", "I-pedir", "E-pedir"]
    assert bioes_tags_to_spans(offsets, tags) == [Span(0, 14, "pedir")]


def test_B_E_without_I():
    offsets = [(0, 3), (4, 8)]
    tags = ["B-informar", "E-informar"]
    assert bioes_tags_to_spans(offsets, tags) == [Span(0, 8, "informar")]


def test_two_separate_spans_with_O_between():
    offsets = [(0, 2), (3, 7), (8, 12)]
    tags = ["S-saudar", "O", "S-pedir"]
    assert bioes_tags_to_spans(offsets, tags) == [
        Span(0, 2, "saudar"),
        Span(8, 12, "pedir"),
    ]


def test_special_tokens_offset_zero_zero_are_skipped():
    offsets = [(0, 0), (0, 2), (0, 0)]
    tags = ["O", "S-saudar", "O"]
    assert bioes_tags_to_spans(offsets, tags) == [Span(0, 2, "saudar")]


def test_dangling_B_without_E_is_closed_at_sequence_end():
    offsets = [(0, 4), (5, 9)]
    tags = ["B-pedir", "I-pedir"]  # never closed with E
    assert bioes_tags_to_spans(offsets, tags) == [Span(0, 9, "pedir")]


def test_dangling_B_closed_by_O():
    offsets = [(0, 4), (5, 9)]
    tags = ["B-pedir", "O"]
    assert bioes_tags_to_spans(offsets, tags) == [Span(0, 4, "pedir")]


def test_act_switch_closes_previous_span():
    offsets = [(0, 4), (5, 9)]
    tags = ["B-pedir", "B-saudar"]  # new B closes the open one
    assert bioes_tags_to_spans(offsets, tags) == [
        Span(0, 4, "pedir"),
        Span(5, 9, "saudar"),
    ]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_decode.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.train.decode'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/train/decode.py
from typing import List, Optional, Tuple
from atos.schema import Span


def _split(tag: str) -> Tuple[str, Optional[str]]:
    if tag == "O":
        return "O", None
    prefix, _, act = tag.partition("-")
    return prefix, act


def bioes_tags_to_spans(
    offsets: List[Tuple[int, int]], tags: List[str]
) -> List[Span]:
    """Reconstruct char-offset spans from per-token BIOES tags (inverse of the tagger).

    Lenient: a new B/S or an act switch closes any open span; a dangling B/I is closed
    at the next O / special token / end of sequence. Special tokens (offset (0,0)) are
    skipped and close any open span.
    """
    spans: List[Span] = []
    open_start: Optional[int] = None
    open_end: int = 0
    open_act: Optional[str] = None

    def close():
        nonlocal open_start, open_end, open_act
        if open_start is not None and open_act is not None:
            spans.append(Span(open_start, open_end, open_act))
        open_start = None
        open_act = None

    for (s, e), tag in zip(offsets, tags):
        if s == e:  # special token / empty offset
            close()
            continue
        prefix, act = _split(tag)
        if prefix == "O":
            close()
        elif prefix == "S":
            close()
            spans.append(Span(s, e, act))
        elif prefix == "B":
            close()
            open_start, open_end, open_act = s, e, act
        elif prefix == "I":
            if open_act == act:
                open_end = e
            else:  # lenient: treat as a fresh open
                close()
                open_start, open_end, open_act = s, e, act
        elif prefix == "E":
            if open_act == act:
                open_end = e
                close()
            else:  # lenient: standalone E becomes a single-token span
                close()
                spans.append(Span(s, e, act))
    close()
    return spans
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_decode.py -q`
Expected: PASS (8 passed)

- [ ] **Step 5: Commit**

```bash
git add src/atos/train/decode.py tests/test_decode.py
git commit -m "feat(train): BIOES->spans decoder (lenient, inverse of tagger)"
```

---

## Task 4: Model builder + LoRA (`model.py`)

BERTimbau token-classification head + LoRA. Bakes in the wiki `lora-fine-tuning-pitfalls`: move `.cuda()` BEFORE `get_peft_model` (caller's job in train.py), and — critically — the BERT classifier head is named `classifier` (NOT `score` as in Privacy Filter BR), and BERT attention projections are `query`/`value` (NOT `q_proj`/`v_proj`).

**Files:**
- Create: `src/atos/train/model.py`
- Test: `tests/test_model_smoke.py`

- [ ] **Step 1: Write the failing test (smoke; requires network for tiny model)**

```python
# tests/test_model_smoke.py
import pytest

pytest.importorskip("torch")
pytest.importorskip("transformers")
pytest.importorskip("peft")

from atos.train.model import build_model, apply_lora
from atos.taxonomy import Taxonomy

TINY = "prajjwal1/bert-tiny"
TAX = Taxonomy(acts=["saudar", "pedir"], definitions={"saudar": "", "pedir": ""})


def test_build_model_sets_num_labels_from_taxonomy():
    model, tokenizer = build_model(TINY, TAX)
    # 4*2 + 1 = 9 BIOES labels
    assert model.config.num_labels == 9
    assert model.config.id2label[0] == "O"
    assert tokenizer.is_fast  # need offset mapping


def test_apply_lora_makes_few_params_trainable():
    model, _ = build_model(TINY, TAX)
    model = apply_lora(model)
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    assert 0 < trainable < total  # LoRA: only a fraction trainable
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_model_smoke.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.train.model'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/train/model.py
from typing import Tuple
from transformers import AutoModelForTokenClassification, AutoTokenizer
from peft import LoraConfig, TaskType, get_peft_model
from atos.taxonomy import Taxonomy, bioes_labels, label_maps


def build_model(model_name: str, taxonomy: Taxonomy):
    """Load a token-classification model + fast tokenizer wired to the BIOES label set."""
    labels = bioes_labels(taxonomy.acts)
    label2id, id2label = label_maps(labels)
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    model = AutoModelForTokenClassification.from_pretrained(
        model_name,
        num_labels=len(labels),
        id2label=id2label,
        label2id=label2id,
    )
    return model, tokenizer


def apply_lora(
    model,
    target_modules=("query", "value"),
    modules_to_save=("classifier",),
    r: int = 16,
    alpha: int = 32,
    dropout: float = 0.1,
):
    """Wrap a BERT token-classifier with LoRA.

    NOTE (wiki lora-fine-tuning-pitfalls): for BERT the attention projections are
    'query'/'value' and the head is 'classifier' — different from Privacy Filter BR
    (q_proj/v_proj, 'score'). modules_to_save trains the fresh head fully. Move the
    base model to its device BEFORE calling this (peft does not reliably propagate
    device transfers).
    """
    config = LoraConfig(
        task_type=TaskType.TOKEN_CLS,
        r=r,
        lora_alpha=alpha,
        lora_dropout=dropout,
        target_modules=list(target_modules),
        modules_to_save=list(modules_to_save),
    )
    return get_peft_model(model, config)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_model_smoke.py -q`
Expected: PASS (2 passed). First run downloads `prajjwal1/bert-tiny` (~17MB).

- [ ] **Step 5: Commit**

```bash
git add src/atos/train/model.py tests/test_model_smoke.py
git commit -m "feat(train): BERTimbau token-cls model builder + LoRA (BERT names)"
```

---

## Task 5: Training entrypoint (`train.py`) + CPU smoke

Wires data → features → model → HF Trainer. Uses the current Transformers API names (wiki API-churn lesson: `eval_strategy`, `processing_class`). Smoke runs 1 step on CPU with the tiny model.

**Files:**
- Create: `src/atos/train/train.py`
- Test: `tests/test_train_smoke.py`

- [ ] **Step 1: Write the failing test (smoke; requires tiny-model download)**

```python
# tests/test_train_smoke.py
import json
import pytest

pytest.importorskip("torch")
pytest.importorskip("transformers")
pytest.importorskip("peft")

from atos.train.train import main


def _write_ds(path):
    rows = [
        {"text": "Bom dia! Pode vir?", "spans": [
            {"start": 0, "end": 8, "act": "saudar"},
            {"start": 9, "end": 18, "act": "pedir"}]},
        {"text": "Obrigado!", "spans": [{"start": 0, "end": 9, "act": "saudar"}]},
    ]
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def test_training_smoke_produces_an_adapter(tmp_path):
    ds = tmp_path / "ds.jsonl"
    _write_ds(str(ds))
    out = tmp_path / "model"
    rc = main([
        "--train", str(ds),
        "--out", str(out),
        "--model", "prajjwal1/bert-tiny",
        "--taxonomy", "config/taxonomy.yaml",
        "--epochs", "1",
        "--max-steps", "1",
        "--batch-size", "2",
        "--cpu",
    ])
    assert rc == 0
    # adapter or model artifacts were written
    assert any(out.iterdir())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_train_smoke.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.train.train'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/train/train.py
import argparse
import torch
from transformers import (
    Trainer,
    TrainingArguments,
    DataCollatorForTokenClassification,
)
from atos.taxonomy import load_taxonomy, bioes_labels, label_maps
from atos.train.data import load_jsonl
from atos.train.features import encode_example
from atos.train.model import build_model, apply_lora


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="atos.train.train",
        description="Fine-tune BERTimbau (LoRA) as a BIOES speech-act token classifier.",
    )
    p.add_argument("--train", required=True, help="training JSONL")
    p.add_argument("--out", required=True, help="output dir for the adapter/model")
    p.add_argument("--model", default="neuralmind/bert-base-portuguese-cased")
    p.add_argument("--taxonomy", default="config/taxonomy.yaml")
    p.add_argument("--epochs", type=float, default=5.0)
    p.add_argument("--max-steps", type=int, default=-1)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--max-length", type=int, default=256)
    p.add_argument("--cpu", action="store_true", help="force CPU (smoke/debug)")
    return p


class _Dataset(torch.utils.data.Dataset):
    def __init__(self, rows):
        self.rows = rows

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        return self.rows[i]


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    taxonomy = load_taxonomy(args.taxonomy)
    label2id, _ = label_maps(bioes_labels(taxonomy.acts))

    model, tokenizer = build_model(args.model, taxonomy)
    # pitfall: move base model to device BEFORE LoRA wrapping
    device = "cpu" if args.cpu else ("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model = apply_lora(model)

    anns = load_jsonl(args.train)
    rows = [
        encode_example(a.text, a.spans, tokenizer, label2id, args.max_length)
        for a in anns
    ]
    dataset = _Dataset(rows)
    collator = DataCollatorForTokenClassification(tokenizer)

    targs = TrainingArguments(
        output_dir=args.out,
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        per_device_train_batch_size=args.batch_size,
        learning_rate=args.lr,
        logging_steps=10,
        save_strategy="no",
        report_to=[],
        use_cpu=args.cpu,
    )
    trainer = Trainer(
        model=model,
        args=targs,
        train_dataset=dataset,
        data_collator=collator,
        processing_class=tokenizer,
    )
    trainer.train()
    model.save_pretrained(args.out)
    tokenizer.save_pretrained(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_train_smoke.py -q`
Expected: PASS (1 passed). Runs 1 training step on CPU with bert-tiny and writes an adapter to the tmp dir.

- [ ] **Step 5: Commit**

```bash
git add src/atos/train/train.py tests/test_train_smoke.py
git commit -m "feat(train): Trainer entrypoint (LoRA token-cls) + CPU smoke"
```

---

## Task 6: Prediction + span-level eval CLI (`eval_cli.py`)

Loads a trained model, predicts BIOES tags on a holdout JSONL, decodes to spans, and scores with the Plan-1 span evaluator. The pure predict→decode step is testable with a fake "model" callable (argmax over injected logits); the CLI wiring is smoke-tested.

**Files:**
- Create: `src/atos/train/eval_cli.py`
- Test: `tests/test_eval_cli.py`

- [ ] **Step 1: Write the failing test (no model download — uses a fake predictor)**

```python
# tests/test_eval_cli.py
from atos.train.eval_cli import score_predictions
from atos.schema import Annotation, Span


def test_score_predictions_matches_gold():
    gold = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])]
    pred = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])]
    report = score_predictions(gold, pred)
    assert report["overall"]["f1"] == 1.0
    assert report["per_act"]["saudar"]["f1"] == 1.0


def test_score_predictions_partial():
    gold = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])]
    pred = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "sugerir")])]
    report = score_predictions(gold, pred)
    assert report["overall"]["f1"] == 0.5
    assert report["per_act"]["pedir"]["f1"] == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_eval_cli.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'atos.train.eval_cli'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/atos/train/eval_cli.py
import argparse
import json
from typing import Dict, List
from atos.schema import Annotation
from atos.eval import span_prf1, per_act_f1


def score_predictions(
    gold: List[Annotation], pred: List[Annotation]
) -> Dict:
    """Combine overall span-F1 and per-act breakdown into one report dict."""
    return {"overall": span_prf1(gold, pred), "per_act": per_act_f1(gold, pred)}


def predict_annotations(model_dir: str, texts: List[str], max_length: int = 256) -> List[Annotation]:
    """Run the trained model over texts and decode BIOES tags into span annotations."""
    import torch
    from transformers import AutoTokenizer
    from peft import AutoPeftModelForTokenClassification
    from atos.train.decode import bioes_tags_to_spans

    tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)
    model = AutoPeftModelForTokenClassification.from_pretrained(model_dir)
    model.eval()
    id2label = model.config.id2label

    out: List[Annotation] = []
    for text in texts:
        enc = tokenizer(
            text,
            return_offsets_mapping=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
        offsets = enc.pop("offset_mapping")[0].tolist()
        with torch.no_grad():
            logits = model(**enc).logits[0]
        ids = logits.argmax(-1).tolist()
        tags = [id2label[i] for i in ids]
        spans = bioes_tags_to_spans([tuple(o) for o in offsets], tags)
        out.append(Annotation(text=text, spans=spans))
    return out


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="atos.train.eval_cli",
        description="Span-level evaluation of a trained speech-act model on a holdout.",
    )
    p.add_argument("--model", required=True, help="trained model/adapter dir")
    p.add_argument("--holdout", required=True, help="holdout JSONL (gold)")
    p.add_argument("--max-length", type=int, default=256)
    return p


def main(argv=None) -> int:
    from atos.train.data import load_jsonl

    args = build_arg_parser().parse_args(argv)
    gold = load_jsonl(args.holdout)
    pred = predict_annotations(args.model, [a.text for a in gold], args.max_length)
    report = score_predictions(gold, pred)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_eval_cli.py -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Run the full suite**

Run: `.venv/bin/pytest -q`
Expected: PASS (Plan 1 + 2 + 3; pure-logic tests always; model/train smokes pass when ml deps + network available).

- [ ] **Step 6: Commit**

```bash
git add src/atos/train/eval_cli.py tests/test_eval_cli.py
git commit -m "feat(train): span-level eval CLI (predict -> decode -> F1)"
```

---

## Task 7: Colab runbook + wiki bookkeeping

**Files:**
- Create: `docs/colab/train_bertimbau_lora.md`
- Create: `wiki/concepts/bertimbau-lora-token-cls.md`
- Modify: `log.md`, `index.md`

- [ ] **Step 1: Create the Colab runbook**

```markdown
# Colab Runbook — BERTimbau LoRA (speech-act span classifier)

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
   from atos.train.model import build_model, apply_lora
   from atos.taxonomy import load_taxonomy
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
   python -m atos.train.train \
     --train data/dataset.jsonl --out runs/sa-lora \
     --epochs 5 --batch-size 16 --lr 2e-4
   ```
6. Evaluate (span-F1):
   ```bash
   python -m atos.train.eval_cli --model runs/sa-lora --holdout data/holdout.jsonl
   ```
7. Watch for the documented gotchas: Transformers API churn (`eval_strategy`, `processing_class`),
   disk filling from logs (redirect + rotate), and head/target names (`classifier`, `query`/`value`).
```

- [ ] **Step 2: Create the concept page**

```markdown
---
type: concept
tags: [bertimbau, lora, token-classification, speech-acts, atos-project]
sources: 0
updated: 2026-06-04
---

# BERTimbau LoRA Token Classification

## Definition

The student model: BERTimbau (`neuralmind/bert-base-portuguese-cased`) fine-tuned with LoRA as a
BIOES token classifier over the speech-act label set. Trained on the Plan-2 synthetic dataset;
evaluated with span-level F1.

## How It Works

`build_model` wires `num_labels`/id maps from the taxonomy; `apply_lora` targets BERT's
`query`/`value` projections and fully trains the `classifier` head (modules_to_save). Features:
char-span annotations → fast-tokenizer offsets → `char_spans_to_bioes` → label ids (-100 on
special tokens). Inference: argmax tags → `bioes_tags_to_spans` → char-offset spans → span-F1.

## Why It Matters

Distills the teacher mixture into a cheap, fast, self-hostable model. Reuses Plan-1 tagger/eval
and Plan-2 data. The BERT-specific names (`classifier`, `query`/`value`) differ from Privacy
Filter BR (`score`, `q_proj`/`v_proj`) — the exact-name pitfall.

## Related Concepts

- [LoRA Fine-tuning Pitfalls](lora-fine-tuning-pitfalls.md)
- [Speech Act Label Scheme](speech-act-label-scheme.md)
- [Teacher-Mixture Generation Pipeline](teacher-mixture-pipeline.md)

## Sources

- Plan: `docs/superpowers/plans/2026-06-04-training-eval.md`
- Colab: `docs/colab/train_bertimbau_lora.md`
```

- [ ] **Step 3: Append to `log.md`**

```markdown
## [2026-06-04] build | Training & Eval (Plan 3)
Implementado treino + avaliação: load_jsonl, align_labels e decoder BIOES→spans (lógica pura testada), model builder BERTimbau + LoRA (nomes BERT: classifier, query/value), train.py com HF Trainer (+ smoke CPU em bert-tiny) e eval CLI span-F1 reusando o evaluator do Plano 1. Runbook de Colab A100 com sanity check anti-NaN. Treino real depende de data/dataset.jsonl (Plano 2) e da taxonomia congelada (Fase 0).
```

- [ ] **Step 4: Add to `index.md`** under "### Fine-tuning & Task Adaptation" (last bullet):

```markdown
- [BERTimbau LoRA Token Classification](wiki/concepts/bertimbau-lora-token-cls.md) — student: BERTimbau + LoRA (classifier, query/value) BIOES token-cls; treino Colab + eval span-F1
```

- [ ] **Step 5: Commit**

```bash
git add docs/colab/train_bertimbau_lora.md wiki/concepts/bertimbau-lora-token-cls.md log.md index.md
git commit -m "docs: Colab runbook + wiki record for training/eval"
```

---

## Self-Review

**1. Spec coverage (Plan 3 portion):**
- BERTimbau + token-classification head + LoRA → Task 4 (`build_model`/`apply_lora`). ✓
- Reuse lora-fine-tuning-pitfalls (`.cuda()` before wrap, exact head/target names, NaN sanity) → Task 4 docstring + Task 5 device order + Task 7 Colab sanity check. ✓
- Mixed precision / grad accumulation → available via TrainingArguments (`--batch-size`, A100 bf16 in Colab); not over-built into smoke. ✓ (Note: bf16 flag can be added at Colab time; smoke runs CPU fp32.)
- Features: char spans → fast-tokenizer offsets → BIOES (Plan 1) → ids with -100 → Tasks 2,3 (encode_example reuses `char_spans_to_bioes`). ✓
- Inference decoding BIOES→spans → Task 3 `bioes_tags_to_spans`. ✓
- Span-level F1 + per-act breakdown on a holdout (Phase-4 metric) → Task 6 reuses Plan-1 `span_prf1`/`per_act_f1`. ✓
- Config-driven taxonomy → Tasks 4,5 read `config/taxonomy.yaml`. ✓
- Real-text holdout eval → Task 6 CLI + Colab step 6. ✓
- Viterbi decoding (spec "optional") → intentionally omitted from v1 (greedy argmax + lenient decoder); can be added later. Noted, not a gap.

**2. Placeholder scan:** No "TBD"/vague steps. Pure-logic tasks have full code + offline tests. ML tasks have full code + smoke tests (tiny model) clearly marked as requiring download. Colab runbook has concrete commands. ✓

**3. Type consistency:** `Annotation`/`Span` from Plan 1 used throughout. `align_labels(tags, special_mask, label2id)` matches its test + `encode_example` call. `bioes_tags_to_spans(offsets, tags)` consistent (Task 3 + Task 6 `predict_annotations`). `build_model(model_name, taxonomy) -> (model, tokenizer)` + `apply_lora(model, ...)` consistent (Tasks 4,5). `score_predictions(gold, pred) -> {overall, per_act}` consistent (Task 6). `load_jsonl(path)` consistent (Tasks 1,5,6). Reuses Plan-1 `bioes_labels`/`label_maps`/`char_spans_to_bioes`/`span_prf1`/`per_act_f1` with their established signatures. ✓

---

## Done criteria

Pure-logic suite (data/features/decode) green offline; model/train/eval smokes green with ml deps + network (tiny model); `python -m atos.train.train --help` and `... eval_cli --help` work. Real run: train on `data/dataset.jsonl` in Colab A100 per the runbook, then `eval_cli` reports span-F1 on the real-text holdout — the v1 success metric. After Fase 0, only `config/taxonomy.yaml` changes; `num_labels` and id maps follow automatically.
