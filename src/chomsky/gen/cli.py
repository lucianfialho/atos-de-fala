import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from chomsky.taxonomy import load_taxonomy
from chomsky.gen.prompts import (
    parse_llm_json,
    build_generation_prompt,
    build_annotation_prompt,
    build_adjudication_prompt,
)
from chomsky.gen.minimax import MiniMaxClient
from chomsky.gen.deepseek import DeepSeekClient
from chomsky.gen.claude import ClaudeClient
from chomsky.gen.pipeline import process_example
from chomsky.gen.dataset import append_annotation, load_done_annotations
from chomsky.gen.balance import act_counts, under_target_acts


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="chomsky.gen.cli",
        description="Generate a synthetic speech-act span dataset "
        "(bulk teacher: MiniMax or DeepSeek; adjudicator: DeepSeek/Claude/none; per-act balancing).",
    )
    p.add_argument("--n", type=int, required=True, help="number of accepted examples to reach")
    p.add_argument("--out", required=True, help="output JSONL path (append + resume)")
    p.add_argument("--provider", choices=["minimax", "deepseek"], default="minimax",
                   help="bulk-teacher provider (default: minimax)")
    p.add_argument("--adjudicator", choices=["deepseek", "claude", "none"], default="deepseek",
                   help="cross-checks + fixes disagreements/invalids (default deepseek; "
                        "'none' = validator-only, no second model)")
    p.add_argument("--adjudicator-model", default="deepseek-reasoner",
                   help="model for the deepseek adjudicator (use a stronger model than the bulk)")
    p.add_argument("--taxonomy", default="config/taxonomy.yaml")
    p.add_argument("--rubric", default="config/rubric.md")
    p.add_argument("--cross-check-rate", type=float, default=0.15,
                   help="fraction of examples also annotated by the adjudicator for agreement")
    p.add_argument("--threshold", type=float, default=0.8)
    p.add_argument("--no-balance", dest="balance", action="store_false",
                   help="disable per-act balancing (default: balanced toward n/num_acts each)")
    p.add_argument("--focus-k", type=int, default=3,
                   help="how many under-represented acts to steer each generation toward")
    p.add_argument("--concurrency", type=int, default=1,
                   help="parallel in-flight requests per wave (I/O-bound; try 8). "
                        "Default 1 = sequential.")
    p.add_argument("--debug", action="store_true")
    return p


def run(args) -> int:
    taxonomy = load_taxonomy(args.taxonomy)
    rubric = _read(args.rubric)
    bulk = DeepSeekClient() if args.provider == "deepseek" else MiniMaxClient()

    def bulk_generate_one(focus=None) -> Dict:
        raw = bulk.complete(build_generation_prompt(rubric, 1, focus))
        return parse_llm_json(raw)

    # Adjudicator / cross-checker. Only the chosen client is instantiated, so e.g.
    # --adjudicator deepseek needs no ANTHROPIC_API_KEY. "none" => validator-only.
    if args.adjudicator == "claude":
        adj = ClaudeClient()
    elif args.adjudicator == "deepseek":
        adj = DeepSeekClient(model=args.adjudicator_model)
    else:
        adj = None

    adj_annotate = None
    adjudicate = None
    if adj is not None:
        def adj_annotate(text: str) -> List[Dict]:  # noqa: F811 — defined when adj exists
            return parse_llm_json(adj.complete(build_annotation_prompt(rubric, text)))["spans"]

        def adjudicate(text: str, problems: List[str]) -> List[Dict]:  # noqa: F811
            return parse_llm_json(
                adj.complete(build_adjudication_prompt(rubric, text, problems))
            )["spans"]

    done_anns = load_done_annotations(args.out)
    done = {a.text for a in done_anns}
    accepted = len(done)
    counts = act_counts(done_anns) if args.balance else {}
    # even split: aim for roughly n/num_acts spans of each act
    per_act_target = max(1, args.n // max(1, len(taxonomy.acts)))
    every = max(1, round(1 / args.cross_check_rate)) if args.cross_check_rate > 0 else 0
    seen = 0
    consecutive_failures = 0
    max_consecutive = max(50, args.n)  # stall guard: stop if we can't make progress

    def attempt(do_cross: bool, focus):
        """One full example, runs in a worker thread: generate -> process. Pure I/O."""
        try:
            obj = bulk_generate_one(focus)
            text = obj["text"]
            cross = adj_annotate if (adj_annotate is not None and do_cross) else None
            res = process_example(
                text, obj["spans"], taxonomy=taxonomy,
                cross_annotate=cross, adjudicate=adjudicate, threshold=args.threshold,
            )
            return text, res, None
        except Exception as e:  # noqa: BLE001 — never let one bad example kill the run
            return None, None, e

    def accept(text, res) -> None:
        nonlocal accepted, consecutive_failures
        append_annotation(args.out, res.annotation)
        done.add(text)
        if args.balance:
            for span in res.annotation.spans:
                counts[span.act] = counts.get(span.act, 0) + 1
        accepted += 1
        consecutive_failures = 0
        print(f"accepted {accepted}/{args.n}")

    # Concurrent waves: submit `workers` attempts in flight, collect, update counts,
    # recompute focus, repeat. All file writes + counter updates happen on this thread
    # (the workers only do HTTP + the pure pipeline), so no locking is needed.
    workers = max(1, args.concurrency)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        while accepted < args.n:
            if consecutive_failures >= max_consecutive:
                print(f"stopping: {consecutive_failures} consecutive non-accepts "
                      f"(generation likely degraded)", file=sys.stderr)
                return 1
            focus = (under_target_acts(counts, taxonomy.acts, per_act_target, args.focus_k)
                     if args.balance else None)
            futures = []
            for _ in range(workers):
                do_cross = bool(every) and (seen % every == 0)
                seen += 1
                futures.append(pool.submit(attempt, do_cross, focus))
            for fut in as_completed(futures):
                text, res, err = fut.result()
                if err is not None:
                    if args.debug:
                        print(f"[error] {err}", file=sys.stderr)
                    consecutive_failures += 1
                    continue
                if text in done:  # dupe (already saved, or another worker just added it)
                    consecutive_failures += 1
                    continue
                if args.debug:
                    print(f"[{res.status}] agree={res.agreement} {res.reason} :: {text[:60]!r}",
                          file=sys.stderr)
                if res.annotation is not None:
                    accept(text, res)
                    if accepted >= args.n:
                        break
                else:
                    consecutive_failures += 1
    return 0


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
