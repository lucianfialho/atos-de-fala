from typing import Tuple
from transformers import AutoModelForTokenClassification, AutoTokenizer
from peft import LoraConfig, TaskType, get_peft_model
from chomsky.taxonomy import Taxonomy, bioes_labels, label_maps


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
