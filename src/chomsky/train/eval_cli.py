import argparse
import json
from typing import Dict, List
from chomsky.schema import Annotation
from chomsky.eval import span_prf1, per_act_f1
from chomsky.train.data import load_jsonl


def score_predictions(
    gold: List[Annotation], pred: List[Annotation]
) -> Dict:
    """Combine overall span-F1 and per-act breakdown into one report dict."""
    return {"overall": span_prf1(gold, pred), "per_act": per_act_f1(gold, pred)}


def predict_annotations(
    model_dir: str, texts: List[str], taxonomy_path: str = "config/taxonomy.yaml", max_length: int = 256
) -> List[Annotation]:
    """Run the trained model over texts and decode BIOES tags into span annotations.

    The base model must be rebuilt with the correct num_labels/id2label BEFORE attaching
    the LoRA adapter — AutoPeft* would instantiate the base with the default num_labels=2
    and the saved 53-class head would not fit (size mismatch). So we read the base name
    from adapter_config.json, build the base with the taxonomy's labels, then load the adapter.
    """
    import json as _json
    import os
    import torch
    from transformers import AutoModelForTokenClassification, AutoTokenizer
    from peft import PeftModel
    from chomsky.taxonomy import load_taxonomy, bioes_labels, label_maps
    from chomsky.train.decode import bioes_tags_to_spans

    with open(os.path.join(model_dir, "adapter_config.json"), encoding="utf-8") as f:
        base_name = _json.load(f)["base_model_name_or_path"]
    labels = bioes_labels(load_taxonomy(taxonomy_path).acts)
    label2id, id2label = label_maps(labels)
    base = AutoModelForTokenClassification.from_pretrained(
        base_name, num_labels=len(labels), id2label=id2label, label2id=label2id
    )
    model = PeftModel.from_pretrained(base, model_dir)
    if torch.cuda.is_available():
        model = model.cuda()
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)

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
        enc = {k: v.to(model.device) for k, v in enc.items()}
        with torch.no_grad():
            logits = model(**enc).logits[0]
        ids = logits.argmax(-1).tolist()
        tags = [id2label[i] for i in ids]
        spans = bioes_tags_to_spans([tuple(o) for o in offsets], tags)
        out.append(Annotation(text=text, spans=spans))
    return out


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="chomsky.train.eval_cli",
        description="Span-level evaluation of a trained speech-act model on a holdout.",
    )
    p.add_argument("--model", required=True, help="trained model/adapter dir")
    p.add_argument("--holdout", required=True, help="holdout JSONL (gold)")
    p.add_argument("--taxonomy", default="config/taxonomy.yaml")
    p.add_argument("--max-length", type=int, default=256)
    return p


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    gold = load_jsonl(args.holdout)
    pred = predict_annotations(args.model, [a.text for a in gold], args.taxonomy, args.max_length)
    report = score_predictions(gold, pred)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
