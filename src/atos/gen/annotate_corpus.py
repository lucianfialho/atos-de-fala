"""Teacher-annotate REAL dialogic text (instead of inventing it) — the top lever from the
synthetic-data research: imports the real PT-BR distribution for free and starves model collapse.

Pulls Roda Viva / FAPESP transcripts (real interview/debate dialogue), has the teacher (Claude)
label speech-act spans per turn with our rubric, resolves quotes → char offsets, validates, and
appends valid annotations to a training JSONL. Silver, not gold (carries teacher bias) — meant to
be MIXED with synthetic + human gold, never used as eval.

    KIMI_API_KEY=... .venv/bin/python -m atos.gen.annotate_corpus \
        --provider kimi \
        --urls https://rodaviva.fapesp.br/materia/470/entrevistados/mano_brown_2007.htm \
        --out data/corpus-silver.jsonl
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor

from atos.taxonomy import load_taxonomy
from atos.resolve import resolve_quoted_spans
from atos.validator import validate
from atos.gen.fapesp import fetch_interview
from atos.gen.prompts import build_annotation_prompt, build_correction_prompt, parse_llm_json
from atos.gen.teachers import make_client
from atos.gen.dataset import append_annotation, load_done_annotations


# Teachers quote with straight quotes; FAPESP text uses curly — normalize so quotes resolve.
_SMART = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})


def _normalize(s: str) -> str:
    return s.translate(_SMART)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="atos.gen.annotate_corpus",
        description="Teacher-annotate real dialogic transcripts (FAPESP) -> training JSONL.",
    )
    p.add_argument("--urls", nargs="*", default=[], help="rodaviva.fapesp.br interview URLs")
    p.add_argument("--text-file", default=None,
                   help="generic source: a plain-text file, one utterance per line (B2W, SAC, etc.)")
    p.add_argument("--out", required=True, help="output JSONL (append + resume)")
    p.add_argument("--rubric", default="config/rubric.md")
    p.add_argument("--taxonomy", default="config/taxonomy.yaml")
    p.add_argument("--provider",
                   choices=["claude", "kimi-code", "kimi", "deepseek", "minimax"], default="kimi-code",
                   help="teacher LLM (default kimi-code — Kimi Code subscription, Anthropic-compatible)")
    p.add_argument("--model", default=None, help="override the provider's default model")
    p.add_argument("--min-chars", type=int, default=20, help="skip turns shorter than this")
    p.add_argument("--max-chars", type=int, default=400, help="skip long monologues (keep trainable)")
    p.add_argument("--limit", type=int, default=0, help="cap turns annotated (0 = no cap)")
    p.add_argument("--concurrency", type=int, default=8, help="parallel teacher calls (I/O-bound)")
    p.add_argument("--correct", action="store_true",
                   help="correction mode: the student model annotates first, the teacher only fixes "
                        "its errors (cheaper, error-focused). Requires --student-model.")
    p.add_argument("--student-model", default=None, help="student adapter dir (for --correct)")
    p.add_argument("--max-length", type=int, default=256, help="student token max_length (--correct)")
    p.add_argument("--debug", action="store_true")
    return p


def run(args) -> int:
    taxonomy = load_taxonomy(args.taxonomy)
    with open(args.rubric, encoding="utf-8") as f:
        rubric = f.read()
    client = make_client(args.provider, args.model)
    done = {a.text for a in load_done_annotations(args.out)}

    if not args.urls and not args.text_file:
        raise SystemExit("provide --urls and/or --text-file")
    turns = []
    for url in args.urls:
        turns.extend(fetch_interview(url))
    if args.text_file:
        with open(args.text_file, encoding="utf-8") as f:
            turns.extend({"speaker": None, "text": ln.strip()} for ln in f if ln.strip())

    # candidates: normalize, length-filter, dedup, skip already-done (resume)
    seen = set()
    cands = []
    for t in turns:
        text = _normalize(t["text"])
        if not (args.min_chars <= len(text) <= args.max_chars) or text in done or text in seen:
            continue
        seen.add(text)
        cands.append(text)
        if args.limit and len(cands) >= args.limit:
            break

    # correction mode: the student annotates first; the teacher only fixes its errors
    proposed = {}
    if args.correct:
        if not args.student_model:
            raise SystemExit("--correct requires --student-model")
        from atos.train.eval_cli import predict_annotations
        preds = predict_annotations(args.student_model, cands, args.taxonomy, args.max_length)
        proposed = {
            txt: [{"quote": txt[s.start:s.end], "act": s.act} for s in ann.spans]
            for txt, ann in zip(cands, preds)
        }

    def work(text):
        """Annotate one utterance (runs in a worker thread; pure I/O)."""
        try:
            msgs = (build_correction_prompt(rubric, text, proposed.get(text, []))
                    if args.correct else build_annotation_prompt(rubric, text))
            items = parse_llm_json(client.complete(msgs))["spans"]
            ann, errs = resolve_quoted_spans(text, items)
            errs = list(errs) + validate(ann, taxonomy)
            return (ann, None) if not errs else (None, errs)
        except Exception as e:  # noqa: BLE001 — one bad turn shouldn't kill the run
            return (None, e)

    kept = rejected = 0
    # workers do HTTP; all file writes happen here on the main thread (no locking needed)
    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
        for ann, err in pool.map(work, cands):
            if ann is not None:
                append_annotation(args.out, ann)
                kept += 1
                print(f"kept {kept}/{len(cands)} (rejected {rejected})")
            else:
                rejected += 1
                if args.debug:
                    print(f"[reject] {err}", file=sys.stderr)
    print(json.dumps({"kept": kept, "rejected": rejected, "candidates": len(cands)}))
    return 0


def main(argv=None) -> int:
    return run(build_arg_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
