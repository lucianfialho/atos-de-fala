"""Build and compile a small HUMAN gold set for speech-act spans.

Why: the synthetic dataset's quality is capped by the teacher LLM. A small,
human-verified gold set lets you (a) measure how good a teacher actually is
(re-annotate generated texts blind, then score the teacher against you) and
(b) have a trustworthy eval holdout beyond Porttinari.

Authoring format = the same quote-based JSON the teacher emits, one per line:

    {"text": "Oi! Pode me enviar?", "spans": [
        {"quote": "Oi!", "act": "saudar"},
        {"quote": "Pode me enviar?", "act": "pedir"}]}

You write `quote` (an exact substring of `text`) + `act` (one of the 13). `compile`
resolves quotes to char offsets, validates against the taxonomy (legal act, in
bounds, non-overlapping), reports per-line errors, and emits the offset JSONL that
`chomsky.train.eval_cli` consumes. Follow `config/rubric.md` while annotating —
same rules the teacher follows (most-specific act; describing != performing; etc.).
"""
import argparse
import json
import sys
from typing import Dict, List, Tuple
from chomsky.schema import Annotation
from chomsky.taxonomy import load_taxonomy
from chomsky.resolve import resolve_quoted_spans
from chomsky.validator import validate


def make_template(texts: List[str]) -> List[Dict]:
    """Blank annotation skeleton: each text with empty spans for you to fill."""
    return [{"text": t, "spans": []} for t in texts]


def sample_texts(jsonl_path: str, n: int) -> List[str]:
    """Read texts from a dataset JSONL and pick up to n, evenly spread across the file."""
    texts: List[str] = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                texts.append(json.loads(line)["text"])
    if n >= len(texts):
        return texts
    stride = len(texts) / n
    return [texts[int(i * stride)] for i in range(n)]


def compile_gold(
    rows: List[Dict], taxonomy
) -> Tuple[List[Annotation], List[str]]:
    """Resolve+validate quote-based rows into offset Annotations.

    Returns (annotations, errors). Each error is "line N: <reasons>". Rows with any
    resolve/validate error are dropped (not silently miscompiled). Empty spans are
    allowed (a legitimate "this text performs no act" example).
    """
    anns: List[Annotation] = []
    errors: List[str] = []
    for i, row in enumerate(rows):
        text = (row.get("text") or "").strip()
        if not text:
            errors.append(f"line {i + 1}: empty text")
            continue
        ann, rerr = resolve_quoted_spans(text, row.get("spans", []))
        problems = list(rerr) + validate(ann, taxonomy)
        if problems:
            errors.append(f"line {i + 1}: " + "; ".join(problems))
            continue
        anns.append(ann)
    return anns, errors


def score_against(gold: List[Annotation], teacher: List[Annotation]) -> Dict:
    """Score a teacher's labels against the human gold, matched by identical text.

    Since both annotate the SAME string, exact span-F1 (start,end,act) is fair here —
    this measures how good the teacher (DeepSeek/Kimi/MiniMax) actually is. Returns
    overall + per-act F1 plus how many gold texts were matched/missing in the teacher set.
    """
    from chomsky.eval import span_prf1, per_act_f1

    by_text = {a.text: a for a in teacher}
    g: List[Annotation] = []
    p: List[Annotation] = []
    missing = 0
    for ga in gold:
        ta = by_text.get(ga.text)
        if ta is None:
            missing += 1
            continue
        g.append(ga)
        p.append(ta)
    return {
        "overall": span_prf1(g, p),
        "per_act": per_act_f1(g, p),
        "matched": len(g),
        "missing": missing,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="chomsky.gold",
        description="Build a blank gold template, or compile a hand-annotated "
        "quote-JSONL into validated offset gold.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("template", help="emit a blank quote-based annotation skeleton")
    src = t.add_mutually_exclusive_group(required=True)
    src.add_argument("--from", dest="src", help="dataset JSONL to sample texts from (blind: labels stripped)")
    src.add_argument("--texts", help="plain text file, one text per line")
    t.add_argument("--n", type=int, default=150, help="how many texts (default 150)")
    t.add_argument("--out", required=True)

    c = sub.add_parser("compile", help="resolve+validate hand annotations into gold offset JSONL")
    c.add_argument("--in", dest="inp", required=True, help="hand-annotated quote-JSONL")
    c.add_argument("--out", required=True, help="validated gold JSONL (offsets)")
    c.add_argument("--taxonomy", default="config/taxonomy.yaml")

    s = sub.add_parser("score", help="score a teacher's labels vs the human gold (same texts)")
    s.add_argument("--gold", required=True, help="compiled gold JSONL")
    s.add_argument("--teacher", required=True, help="teacher dataset JSONL (e.g. data/dataset.jsonl)")
    return p


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    if args.cmd == "template":
        if args.texts:
            with open(args.texts, encoding="utf-8") as f:
                texts = [ln.strip() for ln in f if ln.strip()][: args.n]
        else:
            texts = sample_texts(args.src, args.n)
        rows = make_template(texts)
        with open(args.out, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"wrote {len(rows)} skeleton rows to {args.out} — fill the spans by hand "
              f"(quote + act), following config/rubric.md", file=sys.stderr)
        return 0

    if args.cmd == "score":
        def _load(path):
            with open(path, encoding="utf-8") as f:
                return [Annotation.from_json(ln) for ln in f if ln.strip()]
        report = score_against(_load(args.gold), _load(args.teacher))
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    taxonomy = load_taxonomy(args.taxonomy)
    with open(args.inp, encoding="utf-8") as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    anns, errors = compile_gold(rows, taxonomy)
    with open(args.out, "w", encoding="utf-8") as f:
        for a in anns:
            f.write(a.to_json() + "\n")
    for e in errors:
        print("ERROR " + e, file=sys.stderr)
    print(f"compiled {len(anns)} gold annotations to {args.out}; {len(errors)} error(s)",
          file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
