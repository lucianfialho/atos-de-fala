"""Adjudication worksheet: turn teacher/student SILVER into human GOLD, cheaply.

The eval needs *human* gold, and human gold is human labor — but authoring spans from
scratch is the slow way. Instead: pre-fill a worksheet with the model's proposed spans
(silver) and let a human CORRECT it (confirm / fix act / fix boundary / delete / add).
Correcting is far faster than authoring, and the result is genuine human gold.

Spans are stored as `{quote, act}` (readable text, not char offsets) so the human edits
words, never numbers. `harvest` resolves quotes -> offsets and validates against the
taxonomy, emitting the domain-tagged gold JSONL that atos.train.multidomain consumes.

    # 1. build worksheet from silver (annotate_corpus output, with a domain tag)
    python -m atos.collect.worksheet build --in data/review-silver.jsonl \
        --domain review --out gold/review-worksheet.jsonl
    # 2. a human edits the worksheet: fix spans, set "reviewed": true
    # 3. harvest the reviewed lines into gold
    python -m atos.collect.worksheet harvest --in gold/review-worksheet.jsonl \
        --out gold/review.jsonl
"""
import argparse
import json
from typing import Dict, List, Optional, Tuple

from atos.resolve import resolve_quoted_spans
from atos.validator import validate
from atos.taxonomy import load_taxonomy


def to_worksheet(records: List[Dict], domain: Optional[str] = None) -> List[Dict]:
    """Silver ({text, spans:[{start,end,act}], domain?}) -> worksheet lines with quote-spans
    and reviewed:false. `domain` arg overrides a per-record domain; falls back to 'geral'."""
    out: List[Dict] = []
    for r in records:
        text = r["text"]
        spans = [{"quote": text[s["start"]:s["end"]], "act": s["act"]} for s in r["spans"]]
        out.append({
            "domain": domain or r.get("domain") or "geral",
            "text": text,
            "reviewed": False,
            "spans": spans,
            "notes": "",
        })
    return out


def from_worksheet(records: List[Dict], taxonomy) -> Tuple[List[Dict], Dict[str, int]]:
    """Reviewed worksheet lines -> gold ({text, spans:[{start,end,act}], domain}).
    Skips lines not marked reviewed; rejects lines whose quotes don't resolve or fail
    validation (kept honest — a bad line never silently becomes gold)."""
    gold: List[Dict] = []
    stats = {"kept": 0, "skipped_unreviewed": 0, "rejected": 0}
    for r in records:
        if not r.get("reviewed"):
            stats["skipped_unreviewed"] += 1
            continue
        ann, errs = resolve_quoted_spans(r["text"], r.get("spans", []))
        errs = list(errs) + validate(ann, taxonomy)
        if errs:
            stats["rejected"] += 1
            continue
        gold.append({
            "text": ann.text,
            "spans": [{"start": s.start, "end": s.end, "act": s.act} for s in ann.spans],
            "domain": r.get("domain") or "geral",
        })
        stats["kept"] += 1
    return gold, stats


def _read_jsonl(path: str) -> List[Dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def _write_jsonl(path: str, rows: List[Dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="atos.collect.worksheet",
                                description="Build/harvest an adjudication worksheet (silver -> human gold).")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="silver JSONL -> worksheet JSONL (quote-spans, reviewed:false)")
    b.add_argument("--in", dest="inp", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--domain", default=None, help="override/set domain tag for every line")
    h = sub.add_parser("harvest", help="reviewed worksheet -> gold JSONL (offsets, domain)")
    h.add_argument("--in", dest="inp", required=True)
    h.add_argument("--out", required=True)
    h.add_argument("--taxonomy", default="config/taxonomy.yaml")
    args = p.parse_args(argv)

    if args.cmd == "build":
        rows = to_worksheet(_read_jsonl(args.inp), args.domain)
        _write_jsonl(args.out, rows)
        print(json.dumps({"worksheet_lines": len(rows), "out": args.out}))
    else:
        gold, stats = from_worksheet(_read_jsonl(args.inp), load_taxonomy(args.taxonomy))
        _write_jsonl(args.out, gold)
        print(json.dumps(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
