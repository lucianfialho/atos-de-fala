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
