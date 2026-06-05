from chomsky.resolve import resolve_quoted_spans
from chomsky.schema import Span


def test_malformed_item_reports_error_without_crashing():
    text = "Bom dia!"
    items = [{"act": "saudar"}, {"quote": "Bom dia!", "act": "saudar"}]
    ann, errors = resolve_quoted_spans(text, items)
    assert len(errors) == 1
    assert "missing" in errors[0]
    assert ann.spans == [Span(0, 8, "saudar")]


def test_resolves_quotes_to_offsets_in_order():
    text = "Bom dia! Pode enviar o relatorio?"
    items = [
        {"quote": "Bom dia!", "act": "saudar"},
        {"quote": "Pode enviar o relatorio?", "act": "pedir"},
    ]
    ann, errors = resolve_quoted_spans(text, items)
    assert errors == []
    assert ann.text == text
    assert ann.spans == [Span(0, 8, "saudar"), Span(9, 33, "pedir")]


def test_repeated_quote_is_located_left_to_right():
    text = "Sim. Sim."
    items = [
        {"quote": "Sim.", "act": "concordar"},
        {"quote": "Sim.", "act": "concordar"},
    ]
    ann, errors = resolve_quoted_spans(text, items)
    assert errors == []
    assert ann.spans == [Span(0, 4, "concordar"), Span(5, 9, "concordar")]


def test_missing_quote_reports_error():
    text = "Bom dia!"
    items = [{"quote": "Boa noite!", "act": "saudar"}]
    ann, errors = resolve_quoted_spans(text, items)
    assert len(errors) == 1
    assert "Boa noite!" in errors[0]
    assert ann.spans == []
