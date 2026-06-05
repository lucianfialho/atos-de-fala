import pytest
from chomsky.agreement import span_agreement, gate
from chomsky.schema import Annotation, Span


def _ann(spans):
    return Annotation("Bom dia! Pode vir?", spans)


def test_identical_annotations_agree_fully():
    a = _ann([Span(0, 8, "saudar"), Span(9, 18, "pedir")])
    b = _ann([Span(0, 8, "saudar"), Span(9, 18, "pedir")])
    assert span_agreement(a, b) == 1.0


def test_disjoint_annotations_agree_zero():
    a = _ann([Span(0, 8, "saudar")])
    b = _ann([Span(9, 18, "pedir")])
    assert span_agreement(a, b) == 0.0


def test_partial_overlap_is_f1():
    # a has 2 spans, b has 2 spans, 1 shared -> P=0.5, R=0.5, F1=0.5
    a = _ann([Span(0, 8, "saudar"), Span(9, 18, "pedir")])
    b = _ann([Span(0, 8, "saudar"), Span(9, 18, "sugerir")])
    assert span_agreement(a, b) == 0.5


def test_gate_keeps_above_threshold_and_adjudicates_below():
    a = _ann([Span(0, 8, "saudar"), Span(9, 18, "pedir")])
    b = _ann([Span(0, 8, "saudar"), Span(9, 18, "pedir")])
    assert gate(a, b, threshold=0.8) == "keep"
    c = _ann([Span(0, 8, "saudar")])
    d = _ann([Span(9, 18, "pedir")])
    assert gate(c, d, threshold=0.8) == "adjudicate"


def test_different_texts_raise():
    a = Annotation("texto um", [Span(0, 5, "saudar")])
    b = Annotation("texto dois", [Span(0, 5, "saudar")])
    with pytest.raises(ValueError):
        span_agreement(a, b)
