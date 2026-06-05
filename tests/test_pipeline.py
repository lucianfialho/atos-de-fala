from chomsky.resolve import resolve_quoted_spans
from chomsky.validator import validate
from chomsky.bioes import char_spans_to_bioes
from chomsky.taxonomy import load_taxonomy


def test_resolve_validate_bioes_pipeline():
    text = "Bom dia! Pode enviar o relatorio?"
    items = [
        {"quote": "Bom dia!", "act": "saudar"},
        {"quote": "Pode enviar o relatorio?", "act": "pedir"},
    ]
    ann, errors = resolve_quoted_spans(text, items)
    assert errors == []

    tax = load_taxonomy("config/taxonomy.yaml")
    assert validate(ann, tax) == []

    # whitespace token offsets
    offsets = []
    i = 0
    for tok in text.split(" "):
        start = text.index(tok, i)
        offsets.append((start, start + len(tok)))
        i = start + len(tok)

    tags = char_spans_to_bioes(ann.spans, offsets)
    assert len(tags) == len(offsets)
    assert tags[0] == "B-saudar"
    assert any(t.endswith("pedir") for t in tags)
