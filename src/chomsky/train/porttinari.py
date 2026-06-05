"""Convert the Porttinari speech-act corpus (CSV) into chomsky JSONL.

The Porttinari corpus (da Silva et al., PROPOR 2024) is annotated at the
**sentence level** (one ISO 24617-2 communicative function per sentence). chomsky
is **span level**. This converter therefore emits, per sentence, a single
``Annotation`` whose only span covers the WHOLE sentence, with the Porttinari label
mapped to the chomsky v1 act set (13 acts).

GRANULARITY CAVEAT: running ``chomsky.train.eval_cli`` (exact span-F1) against this
output compares the model's fine-grained spans to whole-sentence gold spans, so an
exact (start,end,act) match is unlikely even when the act is right. Read the result
as a **sentence-level** signal, not strict span-F1. (A sentence-level eval mode —
"does the gold act appear among the predicted span acts?" — is a sensible follow-up.)

Label mapping reflects the chomsky v1 merges (answer/correction -> informar;
instruct -> pedir; compliment/congratulation/sympathy -> expressar_emocao;
confirm -> concordar; disconfirm -> discordar). Acts in our set with no Porttinari
counterpart (oferecer, saudar, despedir) simply never appear in this news corpus.
"""
import argparse
import csv
import sys
from typing import Dict, List, Optional, Tuple
from chomsky.schema import Annotation, Span

# Porttinari ISO label (normalized lowercase) -> chomsky v1 act
LABEL_MAP: Dict[str, str] = {
    "inform": "informar",
    "answer": "informar",
    "correction": "informar",
    "question": "perguntar",
    "agreement": "concordar",
    "confirm": "concordar",
    "disagreement": "discordar",
    "disconfirm": "discordar",
    "request": "pedir",
    "instruct": "pedir",
    "suggest": "sugerir",
    "promise": "prometer",
    "thanking": "agradecer",
    "apology": "desculpar",
    "compliment": "expressar_emocao",
    "congratulation": "expressar_emocao",
    "sympathyexpression": "expressar_emocao",
}


def map_label(porttinari_label: str) -> Optional[str]:
    """Map a Porttinari speech_act value to a chomsky act, or None if unmapped."""
    return LABEL_MAP.get(porttinari_label.strip().lower())


def convert_rows(rows: List[Dict[str, str]]) -> Tuple[List[Annotation], Dict[str, int]]:
    """Convert CSV rows (dicts with 'sentence' and 'speech_act') to Annotations.

    Each kept row becomes one Annotation with a single whole-sentence span. Returns
    the annotations and a stats dict {kept, skipped_unmapped, skipped_empty}.
    """
    anns: List[Annotation] = []
    stats = {"kept": 0, "skipped_unmapped": 0, "skipped_empty": 0}
    for row in rows:
        text = (row.get("sentence") or "").strip()
        if not text:
            stats["skipped_empty"] += 1
            continue
        act = map_label(row.get("speech_act") or "")
        if act is None:
            stats["skipped_unmapped"] += 1
            continue
        anns.append(Annotation(text=text, spans=[Span(0, len(text), act)]))
        stats["kept"] += 1
    return anns, stats


def convert_csv(csv_path: str) -> Tuple[List[Annotation], Dict[str, int]]:
    """Read a Porttinari CSV and convert it (see convert_rows)."""
    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return convert_rows(rows)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="chomsky.train.porttinari",
        description="Convert the Porttinari speech-act CSV into chomsky JSONL "
        "(whole-sentence spans; sentence-level gold).",
    )
    p.add_argument(
        "--csv",
        default="raw/porttinari-base-speech-acts/data/"
        "porttinari-annotated-sample-paper-v1-20231211.csv",
        help="path to the Porttinari annotated CSV",
    )
    p.add_argument("--out", required=True, help="output JSONL path")
    return p


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    anns, stats = convert_csv(args.csv)
    with open(args.out, "w", encoding="utf-8") as f:
        for ann in anns:
            f.write(ann.to_json() + "\n")
    print(
        f"wrote {stats['kept']} annotations to {args.out} "
        f"(skipped: {stats['skipped_unmapped']} unmapped, "
        f"{stats['skipped_empty']} empty)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
