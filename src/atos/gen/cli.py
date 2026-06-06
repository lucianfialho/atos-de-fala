import argparse
from atos.gen.runner import run  # re-exported for tests / callers (cli.run)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="atos.gen.cli",
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
    p.add_argument("--avoid-k", type=int, default=3,
                   help="how many over-represented acts to steer generation AWAY from "
                        "(negative steering; 0 disables)")
    p.add_argument("--concurrency", type=int, default=1,
                   help="parallel in-flight requests per wave (I/O-bound; try 8). "
                        "Default 1 = sequential.")
    p.add_argument("--debug", action="store_true")
    return p


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
