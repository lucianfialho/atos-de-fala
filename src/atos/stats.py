"""Quick stats over a speech-act dataset JSONL.

Run mid-generation to check the per-act balance BEFORE spending GPU on training:

    python -m atos.stats --in data/dataset.jsonl --taxonomy config/taxonomy.yaml

Reports examples, spans, spans/example, per-act counts (with zeros for taxonomy acts
that never appeared — the thing you want to catch), and a balance ratio (min/max act
count; 1.0 = perfectly even, →0 = skewed/starved rare acts).
"""
import argparse
import json
from collections import Counter
from typing import Dict, List, Optional
from atos.schema import Annotation


def compute_stats(anns: List[Annotation], acts: Optional[List[str]] = None) -> Dict:
    n = len(anns)
    spans = [s for a in anns for s in a.spans]
    counter = Counter(s.act for s in spans)

    if acts is not None:
        # taxonomy order + zeros for missing acts, then any stray acts not in taxonomy
        keys = list(acts) + [a for a in counter if a not in acts]
        per_act = {k: counter.get(k, 0) for k in keys}
    else:
        per_act = dict(counter.most_common())

    out: Dict = {
        "examples": n,
        "total_spans": len(spans),
        "spans_per_example": round(len(spans) / n, 3) if n else 0.0,
        "examples_without_spans": sum(1 for a in anns if not a.spans),
        "per_act": per_act,
    }
    if acts is not None and per_act:
        vals = [per_act[a] for a in acts]
        out["min_act_count"] = min(vals)
        out["max_act_count"] = max(vals)
        out["balance_ratio"] = round(min(vals) / max(vals), 3) if max(vals) else 0.0
    return out


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="atos.stats",
        description="Per-act distribution + balance stats over a dataset JSONL.",
    )
    p.add_argument("--in", dest="inp", required=True, help="dataset JSONL")
    p.add_argument("--taxonomy", default="config/taxonomy.yaml",
                   help="show zeros for acts that never appeared + balance ratio")
    p.add_argument("--json", action="store_true", help="emit raw JSON instead of a table")
    return p


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    with open(args.inp, encoding="utf-8") as f:
        anns = [Annotation.from_json(ln) for ln in f if ln.strip()]

    acts = None
    try:
        from atos.taxonomy import load_taxonomy
        acts = load_taxonomy(args.taxonomy).acts
    except Exception:  # noqa: BLE001 — taxonomy optional for stats
        pass

    s = compute_stats(anns, acts=acts)
    if args.json:
        print(json.dumps(s, ensure_ascii=False, indent=2))
        return 0

    print(f"examples            : {s['examples']}")
    print(f"total spans         : {s['total_spans']}")
    print(f"spans / example     : {s['spans_per_example']}")
    print(f"examples w/o spans  : {s['examples_without_spans']}")
    if "balance_ratio" in s:
        print(f"balance (min/max)   : {s['balance_ratio']}  "
              f"(min {s['min_act_count']}, max {s['max_act_count']})")
    print("per act (count, %):")
    total = s["total_spans"] or 1
    for act, c in sorted(s["per_act"].items(), key=lambda kv: -kv[1]):
        print(f"  {act:<18} {c:>7}  {100 * c / total:5.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
