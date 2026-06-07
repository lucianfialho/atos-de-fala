"""Benchmark ONNX quantization variants on the multi-domain gold — int8 vs fp16.

Decides the PR #2 question with a number instead of faith: runs each .onnx variant over the
same domain-tagged gold the harness uses, scores per-domain + pooled, and times it. If fp16
doesn't beat int8 on macro-F1 (especially on the rare social/commissive acts), the extra
~100 MB download isn't worth it.

    python scripts/compare_onnx.py MODEL_DIR GOLD.jsonl [--mode sentence] [--coarse] \
        [--variant int8=onnx/model_quantized.onnx] [--variant fp16=onnx/model_fp16.onnx]

MODEL_DIR holds config.json + tokenizer (the HF repo layout). Default variants are
int8 (onnx/model_quantized.onnx) and fp16 (onnx/model_fp16.onnx) relative to MODEL_DIR.
"""
import argparse
import json
import os
import time

from atos.train.multidomain import load_gold, _score
from atos.train.onnx_predict import predict_annotations_onnx
from atos.taxonomy import load_taxonomy


def run_variant(onnx_path, model_dir, groups, taxonomy, max_length, mode, macro):
    """Score one ONNX variant per domain + pooled; return (report, seconds, n_items)."""
    report, all_gold, all_pred, n = {}, [], [], 0
    t0 = time.perf_counter()
    for domain, gold in groups.items():
        texts = [a.text for a in gold]
        pred = predict_annotations_onnx(onnx_path, model_dir, texts, taxonomy, max_length)
        report[domain] = _score(gold, pred, mode, macro)
        all_gold.extend(gold); all_pred.extend(pred); n += len(gold)
    report["todos"] = _score(all_gold, all_pred, mode, macro)
    return report, time.perf_counter() - t0, n


def detail_f1(slice_report, mode):
    d = slice_report[mode]
    return d.get("f1", d.get("macro_f1", 0.0)) if isinstance(d, dict) else 0.0


def print_table(results, mode):
    """results: {variant_name: (report, secs, n)}. One row per domain, macro-F1 per variant."""
    names = list(results)
    domains = list(next(iter(results.values()))[0])
    w = max(12, max((len(d) for d in domains), default=12) + 1)
    head = "domínio".ljust(w) + "".join(f"{n:>16}" for n in names)
    print(head); print("-" * len(head))
    for dom in domains:
        cells = "".join(f"{results[n][0][dom]['macro_f1']:>16.3f}" for n in names)
        print(dom.ljust(w) + cells)
    print("-" * len(head))
    print(f"{mode}-F1 (todos)".ljust(w) + "".join(
        f"{detail_f1(results[n][0]['todos'], mode):>16.3f}" for n in names))
    print("latência (s)".ljust(w) + "".join(f"{results[n][1]:>16.1f}" for n in names))


def parse_variants(items, model_dir):
    if not items:
        return {"int8": os.path.join(model_dir, "onnx/model_quantized.onnx"),
                "fp16": os.path.join(model_dir, "onnx/model_fp16.onnx")}
    out = {}
    for it in items:
        name, _, path = it.partition("=")
        out[name] = path if os.path.isabs(path) else os.path.join(model_dir, path)
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="compare_onnx", description="int8 vs fp16 on multi-domain gold")
    p.add_argument("model_dir"); p.add_argument("gold")
    p.add_argument("--taxonomy", default="config/taxonomy.yaml")
    p.add_argument("--max-length", type=int, default=256)
    p.add_argument("--mode", choices=["span", "sentence"], default="span")
    p.add_argument("--coarse", action="store_true")
    p.add_argument("--variant", action="append", default=[],
                   help="name=relpath (repeatable); default int8 + fp16")
    p.add_argument("--json", action="store_true", help="also dump the full report dict as JSON")
    args = p.parse_args(argv)

    groups = load_gold(args.gold)
    macro = load_taxonomy(args.taxonomy).macro if args.coarse else None
    variants = parse_variants(args.variant, args.model_dir)
    results = {}
    for name, path in variants.items():
        if not os.path.exists(path):
            print(f"[skip] {name}: {path} não existe"); continue
        results[name] = run_variant(path, args.model_dir, groups, args.taxonomy,
                                    args.max_length, args.mode, macro)
    if not results:
        raise SystemExit("nenhuma variante encontrada")
    print_table(results, args.mode)
    if args.json:
        print(json.dumps({n: r for n, (r, _, _) in results.items()}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
