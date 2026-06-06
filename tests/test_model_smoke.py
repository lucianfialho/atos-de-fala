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
