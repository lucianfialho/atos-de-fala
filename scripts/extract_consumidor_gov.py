"""Extract SAC (customer-service) turns from the Consumidor.gov.br relatos dataset.

Source: Kaggle 'relatos-de-consumidores-do-site-consumidor-gov-br' (CC0 / public domain),
~204k records scraped from the federal consumidor.gov.br public-consultation platform.
Each record has free text from three turn types — the only natural PT-BR source for the
commissive/service acts (oferecer/prometer/desculpar/saudar) that news + review corpora lack:

  relato     -> customer complaint  (informar/discordar/pedir/expressar_emocao/sugerir)
  resposta   -> company response    (saudar/desculpar/oferecer/prometer/informar/despedir)
  comentario -> customer's reply     (concordar/discordar/agradecer/expressar_emocao)

CC0 covers reuse, but the text still carries real names (e.g. "Bom dia, Gabriel") — fine for
internal eval/training; scrub PII before publishing any gold subset. Output is plain turns,
one per line -> annotate_corpus -> worksheet -> human gold (domain=sac).

    python scripts/extract_consumidor_gov.py --in raw/consumidor-gov/dados2025.json \
        --out data/sac.txt --limit 80 --fields resposta relato comentario
"""
import argparse
import json
import random
import re

_SENT = re.compile(r"(?<=[.!?])\s+|\n+")
_WORD = re.compile(r"[A-Za-zÀ-ÿ]{2,}")
_LETTER = re.compile(r"[A-Za-zÀ-ÿ]")
_CODEY = re.compile(r"protocolo|\bn[ºo°]\b|\bID\b|\bSAC\b|\bCPF\b|\bCNPJ\b", re.I)
# sign-offs/headers are the main PII vector (agent signatures, "Nome / Cargo") AND boilerplate.
_SIGNOFF = re.compile(r"^\s*(atenciosamente|cordialmente|att\.?|abraç|equipe\b|ouvidoria|"
                      r"central de atendimento|canal de comunica)", re.I)


def _is_junk(s: str) -> bool:
    """Drop boilerplate that's technically 'informar' but worthless to annotate — and, crucially,
    the lines that carry names: agent signatures ('Nome / Cargo'), sign-offs, ALL-CAPS headers,
    protocol/ID/number lines, and anything too sparse on real words."""
    words = _WORD.findall(s)
    if len(words) < 4:
        return True
    letters = _LETTER.findall(s)
    if len(letters) / max(1, len(s)) < 0.55:  # digit/punct heavy
        return True
    if sum(c.isupper() for c in letters) / max(1, len(letters)) > 0.7:  # ALL-CAPS header
        return True
    if " / " in s or _SIGNOFF.search(s):  # "Grazielle Duarte / Assistente", sign-offs
        return True
    if _CODEY.search(s) and any(c.isdigit() for c in s):  # "Protocolo nº ABC123"
        return True
    return False


def turns(text: str, lo: int, hi: int) -> list:
    out = []
    for sent in _SENT.split(text or ""):
        sent = re.sub(r"\s{2,}", " ", sent).strip(" \t,.;")
        if lo <= len(sent) <= hi and "http" not in sent and not _is_junk(sent):
            out.append(sent)
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="extract_consumidor_gov",
                                description="Consumidor.gov.br relatos JSON -> SAC turns")
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--limit", type=int, default=80, help="number of records to sample")
    p.add_argument("--seed", type=int, default=13)
    p.add_argument("--fields", nargs="+", default=["resposta", "relato", "comentario"],
                   help="which turn fields to extract (resposta first = more service acts)")
    p.add_argument("--min-chars", type=int, default=20)
    p.add_argument("--max-chars", type=int, default=400)
    args = p.parse_args(argv)

    data = json.load(open(args.inp, encoding="utf-8"))
    # only records that actually have a company response (those carry the service acts)
    answered = [r for r in data if (r.get("resposta") or "").strip()]
    random.Random(args.seed).shuffle(answered)
    sample = answered[:args.limit]

    seen, rows = set(), []
    for rec in sample:
        for field in args.fields:
            for t in turns(rec.get(field), args.min_chars, args.max_chars):
                if t not in seen:
                    seen.add(t)
                    rows.append(t)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(rows) + "\n")
    print(json.dumps({"records_sampled": len(sample), "unique_turns": len(rows),
                      "fields": args.fields, "out": args.out}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
