"""Merge the trained LoRA adapter into BERTimbau -> a standalone token-classification model.

The merged model loads with a plain `AutoModelForTokenClassification.from_pretrained` (no PEFT)
and works with `pipeline("token-classification")` / the HF Inference API. The config carries
id2label/label2id (the 53 BIOES labels) so predictions come back as act names, not LABEL_0.

    .venv/bin/python scripts/merge_model.py            # -> runs/sa-merged/
"""
import json
from transformers import AutoModelForTokenClassification, AutoTokenizer
from peft import PeftModel
from chomsky.taxonomy import load_taxonomy, bioes_labels, label_maps

ADAPTER = "runs/sa-lora"
OUT = "runs/sa-merged"


def main() -> int:
    tax = load_taxonomy("config/taxonomy.yaml")
    labels = bioes_labels(tax.acts)
    label2id, id2label = label_maps(labels)
    base_name = json.load(open(f"{ADAPTER}/adapter_config.json"))["base_model_name_or_path"]
    base = AutoModelForTokenClassification.from_pretrained(
        base_name, num_labels=len(labels), id2label=id2label, label2id=label2id
    )
    merged = PeftModel.from_pretrained(base, ADAPTER).merge_and_unload()
    merged.save_pretrained(OUT)
    AutoTokenizer.from_pretrained(ADAPTER, use_fast=True).save_pretrained(OUT)
    print(f"merged -> {OUT} ({len(labels)} labels)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
