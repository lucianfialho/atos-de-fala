"""Scrub person names (LGPD) from a one-turn-per-line text file using PT NER, BEFORE the text
reaches the public collection site. Replaces PESSOA entities with a placeholder; keeps
ORGANIZACAO/LOCAL (company names / cities aren't personal data and are already public on
consumidor.gov.br). Catches names anywhere — salutations, signatures, mid-prose — which the
regex pre-pass alone misses (e.g. "Agradeço a Grazielle Duarte pelo atendimento").

    python scripts/scrub_pii.py --in data/sac-eval.txt --out data/sac-eval-clean.txt
"""
import argparse


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="scrub_pii", description="NER person-name scrub for PT text")
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--model", default="marquesafonso/bertimbau-large-ner-selective")
    p.add_argument("--groups", nargs="+", default=["PESSOA", "PER", "PERSON"],
                   help="entity groups treated as personal names")
    p.add_argument("--repl", default="[nome]")
    p.add_argument("--batch-size", type=int, default=32)
    args = p.parse_args(argv)

    from transformers import pipeline
    ner = pipeline("ner", model=args.model, aggregation_strategy="simple")
    groups = set(args.groups)

    lines = [ln.rstrip("\n") for ln in open(args.inp, encoding="utf-8")]
    nonempty = [(i, t) for i, t in enumerate(lines) if t.strip()]
    results = ner([t for _, t in nonempty], batch_size=args.batch_size)

    scrubbed = 0
    for (i, text), ents in zip(nonempty, results):
        # replace right-to-left so earlier offsets stay valid
        spans = sorted(((e["start"], e["end"]) for e in ents if e["entity_group"] in groups),
                       reverse=True)
        for s, e in spans:
            text = text[:s] + args.repl + text[e:]
        if spans:
            scrubbed += 1
        lines[i] = text

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"scrubbed names in {scrubbed}/{len(lines)} lines -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
