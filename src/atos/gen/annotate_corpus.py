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
import os
import sys

from atos.taxonomy import load_taxonomy
from atos.resolve import resolve_quoted_spans
from atos.validator import validate
from atos.gen.fapesp import fetch_interview
from atos.gen.prompts import build_annotation_prompt, parse_llm_json
from atos.gen.dataset import append_annotation, load_done_annotations


def _make_client(provider: str, model):
    """Instantiate the chosen teacher; only pass model if the user overrode it."""
    kw = {"model": model} if model else {}
    if provider == "claude":
        from atos.gen.claude import ClaudeClient
        return ClaudeClient(**kw)
    if provider == "kimi-code":
        # Kimi Code subscription — Anthropic-compatible endpoint (ClaudeClient speaks it).
        from atos.gen.claude import ClaudeClient
        key = os.environ.get("KIMI_API_KEY") or os.environ.get("MOONSHOT_API_KEY")
        base = os.environ.get("KIMI_BASE_URL", "https://api.kimi.com/coding/v1/messages")
        return ClaudeClient(api_key=key, base_url=base, model=model or "kimi-k2-0905-preview")
    if provider == "kimi":
        from atos.gen.kimi import KimiClient
        return KimiClient(**kw)
    if provider == "deepseek":
        from atos.gen.deepseek import DeepSeekClient
        return DeepSeekClient(**kw)
    if provider == "minimax":
        from atos.gen.minimax import MiniMaxClient
        return MiniMaxClient(**kw)
    raise ValueError(f"unknown provider: {provider}")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="atos.gen.annotate_corpus",
        description="Teacher-annotate real dialogic transcripts (FAPESP) -> training JSONL.",
    )
    p.add_argument("--urls", nargs="+", required=True, help="rodaviva.fapesp.br interview URLs")
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
    p.add_argument("--debug", action="store_true")
    return p


def run(args) -> int:
    taxonomy = load_taxonomy(args.taxonomy)
    with open(args.rubric, encoding="utf-8") as f:
        rubric = f.read()
    client = _make_client(args.provider, args.model)
    done = {a.text for a in load_done_annotations(args.out)}

    turns = []
    for url in args.urls:
        turns.extend(fetch_interview(url))

    kept = rejected = 0
    for t in turns:
        text = t["text"]
        if not (args.min_chars <= len(text) <= args.max_chars) or text in done:
            continue
        try:
            items = parse_llm_json(client.complete(build_annotation_prompt(rubric, text)))["spans"]
            ann, errs = resolve_quoted_spans(text, items)
            errs = list(errs) + validate(ann, taxonomy)
            if errs:
                rejected += 1
                if args.debug:
                    print(f"[reject] {errs} :: {text[:60]!r}", file=sys.stderr)
                continue
            append_annotation(args.out, ann)
            done.add(text)
            kept += 1
            print(f"kept {kept} (rejected {rejected})")
        except Exception as e:  # noqa: BLE001 — one bad turn shouldn't kill the run
            rejected += 1
            if args.debug:
                print(f"[error] {e}", file=sys.stderr)
        if args.limit and kept >= args.limit:
            break
    print(json.dumps({"kept": kept, "rejected": rejected}))
    return 0


def main(argv=None) -> int:
    return run(build_arg_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
