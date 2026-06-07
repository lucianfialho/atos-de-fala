"""Multi-domain evaluation: slice a gold set by `domain` and score each slice
independently so a regression in one domain (notícia) can't be masked by a gain in
another (review/SAC/entrevista) — the eval-blindness we hit with Porttinari-only.

Gold JSONL is the usual {text, spans:[{start,end,act}]} plus an optional top-level
`"domain"` key (defaults to "geral"). The harness groups by domain, runs the model
per group, and reports per-domain + a pooled "todos" overall — in span or sentence
mode (sentence for sentence-level gold like Porttinari, where exact span-F1 is ~0).

    .venv/bin/python -m atos.train.multidomain --model models/v3 \
        --gold data/gold-multidomain.jsonl --mode span
"""
import argparse
import json
from collections import OrderedDict
from typing import Dict, List, Optional

from atos.schema import Annotation, Span
from atos.eval import span_prf1, per_act_f1, coarsen, sentence_label_f1
from atos.taxonomy import load_taxonomy


def group_by_domain(records: List[Dict]) -> "OrderedDict[str, List[Annotation]]":
    """Group raw JSONL records (text/spans/optional domain) into Annotations per domain,
    preserving first-seen domain order. Pure — no torch, no I/O — so it stays unit-testable."""
    groups: "OrderedDict[str, List[Annotation]]" = OrderedDict()
    for r in records:
        domain = r.get("domain") or "geral"
        ann = Annotation(r["text"], [Span(s["start"], s["end"], s["act"]) for s in r["spans"]])
        groups.setdefault(domain, []).append(ann)
    return groups


def load_gold(path: str) -> "OrderedDict[str, List[Annotation]]":
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return group_by_domain(records)


def _score(gold: List[Annotation], pred: List[Annotation], mode: str,
           macro: Optional[Dict[str, str]]) -> Dict:
    """One slice's report: macro-F1 + the chosen mode's detail. macro-F1 is the
    unweighted mean of per-act span-F1 (the metric we optimize), computed on the
    (optionally coarsened) spans regardless of mode so domains stay comparable."""
    g, p = (coarsen(gold, macro), coarsen(pred, macro)) if macro else (gold, pred)
    per_act = per_act_f1(g, p)
    macro_f1 = sum(v["f1"] for v in per_act.values()) / len(per_act) if per_act else 0.0
    detail = sentence_label_f1(gold, pred, macro) if mode == "sentence" else span_prf1(g, p)
    return {"n": len(gold), "macro_f1": macro_f1, "per_act": per_act, mode: detail}


def evaluate(model_dir: str, groups: "OrderedDict[str, List[Annotation]]",
             taxonomy_path: str, max_length: int, mode: str, coarse: bool) -> Dict:
    """Run the model per domain + pooled. Imports predict_annotations lazily (torch)."""
    from atos.train.eval_cli import predict_annotations
    macro = load_taxonomy(taxonomy_path).macro if coarse else None
    report: Dict[str, Dict] = {}
    all_gold: List[Annotation] = []
    all_pred: List[Annotation] = []
    for domain, gold in groups.items():
        pred = predict_annotations(model_dir, [a.text for a in gold], taxonomy_path, max_length)
        report[domain] = _score(gold, pred, mode, macro)
        all_gold.extend(gold)
        all_pred.extend(pred)
    report["todos"] = _score(all_gold, all_pred, mode, macro)
    return report


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="atos.train.multidomain",
        description="Per-domain span/sentence eval — exposes domain-specific regressions.",
    )
    p.add_argument("--model", required=True, help="trained model/adapter dir")
    p.add_argument("--gold", required=True, help="multi-domain gold JSONL (optional `domain` key/line)")
    p.add_argument("--taxonomy", default="config/taxonomy.yaml")
    p.add_argument("--max-length", type=int, default=256)
    p.add_argument("--mode", choices=["span", "sentence"], default="span",
                   help="span: exact (start,end,act) F1. sentence: dominant-act match (sentence-level gold).")
    p.add_argument("--coarse", action="store_true", help="collapse to Searle macro-classes before scoring.")
    return p


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    groups = load_gold(args.gold)
    report = evaluate(args.model, groups, args.taxonomy, args.max_length, args.mode, args.coarse)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
