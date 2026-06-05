import argparse
import sys
from typing import List, Dict
from chomsky.taxonomy import load_taxonomy
from chomsky.gen.prompts import (
    parse_llm_json,
    build_generation_prompt,
    build_annotation_prompt,
    build_adjudication_prompt,
)
from chomsky.gen.minimax import MiniMaxClient
from chomsky.gen.claude import ClaudeClient
from chomsky.gen.pipeline import process_example
from chomsky.gen.dataset import append_annotation, load_done_texts


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="chomsky.gen.cli",
        description="Generate a synthetic speech-act span dataset (MiniMax bulk + Claude adjudicator).",
    )
    p.add_argument("--n", type=int, required=True, help="number of accepted examples to reach")
    p.add_argument("--out", required=True, help="output JSONL path (append + resume)")
    p.add_argument("--taxonomy", default="config/taxonomy.yaml")
    p.add_argument("--rubric", default="config/rubric.md")
    p.add_argument("--cross-check-rate", type=float, default=0.15,
                   help="fraction of examples also annotated by Claude for agreement")
    p.add_argument("--threshold", type=float, default=0.8)
    p.add_argument("--debug", action="store_true")
    return p


def run(args) -> int:
    taxonomy = load_taxonomy(args.taxonomy)
    rubric = _read(args.rubric)
    mm = MiniMaxClient()
    cl = ClaudeClient()

    def mm_generate_one() -> Dict:
        raw = mm.complete(build_generation_prompt(rubric, 1))
        return parse_llm_json(raw)

    def cl_annotate(text: str) -> List[Dict]:
        raw = cl.complete(build_annotation_prompt(rubric, text))
        return parse_llm_json(raw)["spans"]

    def adjudicate(text: str, problems: List[str]) -> List[Dict]:
        raw = cl.complete(build_adjudication_prompt(rubric, text, problems))
        return parse_llm_json(raw)["spans"]

    done = load_done_texts(args.out)
    accepted = len(done)
    every = max(1, round(1 / args.cross_check_rate)) if args.cross_check_rate > 0 else 0
    seen = 0
    consecutive_failures = 0
    max_consecutive = max(50, args.n)  # stall guard: stop if we can't make progress
    while accepted < args.n:
        if consecutive_failures >= max_consecutive:
            print(f"stopping: {consecutive_failures} consecutive non-accepts "
                  f"(generation likely degraded)", file=sys.stderr)
            return 1
        seen += 1
        try:
            obj = mm_generate_one()
            text = obj["text"]
            if text in done:
                consecutive_failures += 1
                continue
            cross = cl_annotate if (every and seen % every == 0) else None
            res = process_example(
                text, obj["spans"], taxonomy=taxonomy,
                cross_annotate=cross, adjudicate=adjudicate, threshold=args.threshold,
            )
        except Exception as e:  # noqa: BLE001 — never let one bad example kill the run
            if args.debug:
                print(f"[error] {e}", file=sys.stderr)
            consecutive_failures += 1
            continue
        if args.debug:
            print(f"[{res.status}] agree={res.agreement} {res.reason} :: {text[:60]!r}",
                  file=sys.stderr)
        if res.annotation is not None:
            append_annotation(args.out, res.annotation)
            done.add(text)
            accepted += 1
            consecutive_failures = 0
            print(f"accepted {accepted}/{args.n}")
        else:
            consecutive_failures += 1
    return 0


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
