"""Generate an example honeypots.jsonl: small, UNAMBIGUOUS gold whose acts are known.

Honeypots are the "iscas" — items with a known-correct answer used to score annotator
reliability. They must be unambiguous, so they are hand-authored here (NOT sampled from the
unverified synthetic dataset). Quotes are resolved to char offsets and validated against the
frozen taxonomy via the project's own gold machinery, guaranteeing correct, non-overlapping,
in-taxonomy spans. Output is the offset-Annotation JSONL that `atos.collect export
--honeypots` (and `atos.train.data.load_jsonl`) consume.

    .venv/bin/python scripts/gen_honeypots.py            # -> gold/honeypots.jsonl
"""
import json
import os
import sys
from atos.gold import compile_gold
from atos.taxonomy import load_taxonomy

# (text, [(quote, act)]) — every quote is an exact substring of its text.
ROWS = [
    {"text": "Bom dia!", "spans": [{"quote": "Bom dia!", "act": "saudar"}]},
    {"text": "Muito obrigado pela ajuda!", "spans": [{"quote": "Muito obrigado pela ajuda!", "act": "agradecer"}]},
    {"text": "Que horas são?", "spans": [{"quote": "Que horas são?", "act": "perguntar"}]},
    {"text": "O relatório foi enviado ontem.", "spans": [{"quote": "O relatório foi enviado ontem.", "act": "informar"}]},
    {"text": "Me envia o arquivo, por favor.", "spans": [{"quote": "Me envia o arquivo, por favor.", "act": "pedir"}]},
    {"text": "Desculpa pelo atraso.", "spans": [{"quote": "Desculpa pelo atraso.", "act": "desculpar"}]},
    {"text": "Até amanhã!", "spans": [{"quote": "Até amanhã!", "act": "despedir"}]},
    {"text": "Prometo que termino hoje.", "spans": [{"quote": "Prometo que termino hoje.", "act": "prometer"}]},
    {"text": "Posso te ajudar com isso.", "spans": [{"quote": "Posso te ajudar com isso.", "act": "oferecer"}]},
    {"text": "Concordo plenamente.", "spans": [{"quote": "Concordo plenamente.", "act": "concordar"}]},
    {"text": "Discordo dessa ideia.", "spans": [{"quote": "Discordo dessa ideia.", "act": "discordar"}]},
    {"text": "Que tal almoçarmos mais tarde?", "spans": [{"quote": "Que tal almoçarmos mais tarde?", "act": "sugerir"}]},
    {"text": "Que alívio!", "spans": [{"quote": "Que alívio!", "act": "expressar_emocao"}]},
    # clean multi-span honeypots
    {"text": "Bom dia! Obrigado pela ajuda.",
     "spans": [{"quote": "Bom dia!", "act": "saudar"}, {"quote": "Obrigado pela ajuda.", "act": "agradecer"}]},
    {"text": "Oi! Pode me enviar o relatório?",
     "spans": [{"quote": "Oi!", "act": "saudar"}, {"quote": "Pode me enviar o relatório?", "act": "pedir"}]},
    {"text": "Desculpa o atraso. Prometo entregar hoje.",
     "spans": [{"quote": "Desculpa o atraso.", "act": "desculpar"}, {"quote": "Prometo entregar hoje.", "act": "prometer"}]},
    {"text": "Até logo! Foi ótimo te ver.",
     "spans": [{"quote": "Até logo!", "act": "despedir"}, {"quote": "Foi ótimo te ver.", "act": "expressar_emocao"}]},
    {"text": "Concordo. Que tal começarmos amanhã?",
     "spans": [{"quote": "Concordo.", "act": "concordar"}, {"quote": "Que tal começarmos amanhã?", "act": "sugerir"}]},
]


def main() -> int:
    tax = load_taxonomy("config/taxonomy.yaml")
    anns, errors = compile_gold(ROWS, tax)
    if errors:
        print("ERRORS (fix the rows):", *errors, sep="\n  ", file=sys.stderr)
        return 1
    os.makedirs("gold", exist_ok=True)
    with open("gold/honeypots.jsonl", "w", encoding="utf-8") as f:
        for a in anns:
            f.write(a.to_json() + "\n")
    covered = {s.act for a in anns for s in a.spans}
    print(f"wrote {len(anns)} honeypots -> gold/honeypots.jsonl; acts covered: {len(covered)}/13")
    missing = set(tax.acts) - covered
    if missing:
        print("WARNING: acts not covered:", sorted(missing))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
