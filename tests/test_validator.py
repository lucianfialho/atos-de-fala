from chomsky.validator import validate
from chomsky.schema import Annotation, Span
from chomsky.taxonomy import Taxonomy

TAX = Taxonomy(acts=["saudar", "pedir"], definitions={"saudar": "", "pedir": ""})


def test_valid_annotation_has_no_errors():
    ann = Annotation("Oi! Pode vir?", [Span(0, 3, "saudar"), Span(4, 13, "pedir")])
    assert validate(ann, TAX) == []


def test_out_of_bounds_span_is_flagged():
    ann = Annotation("Oi", [Span(0, 5, "saudar")])
    errors = validate(ann, TAX)
    assert any("bounds" in e for e in errors)


def test_inverted_span_is_flagged():
    ann = Annotation("Oi tudo bem", [Span(5, 2, "saudar")])
    errors = validate(ann, TAX)
    assert any("bounds" in e for e in errors)


def test_illegal_act_is_flagged():
    ann = Annotation("Oi", [Span(0, 2, "xingar")])
    errors = validate(ann, TAX)
    assert any("illegal act" in e for e in errors)


def test_overlapping_spans_are_flagged():
    ann = Annotation("Oi tudo bem", [Span(0, 7, "saudar"), Span(3, 11, "pedir")])
    errors = validate(ann, TAX)
    assert any("overlap" in e for e in errors)
