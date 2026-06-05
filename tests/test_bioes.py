from chomsky.bioes import char_spans_to_bioes
from chomsky.schema import Span


def test_single_token_span_gets_S():
    # text "Oi!" -> tokens "Oi" (0,2), "!" (2,3); span covers "Oi" only
    offsets = [(0, 2), (2, 3)]
    spans = [Span(0, 2, "saudar")]
    assert char_spans_to_bioes(spans, offsets) == ["S-saudar", "O"]


def test_multi_token_span_gets_B_I_E():
    # 3 tokens all inside one span
    offsets = [(0, 4), (5, 9), (10, 14)]
    spans = [Span(0, 14, "pedir")]
    assert char_spans_to_bioes(spans, offsets) == ["B-pedir", "I-pedir", "E-pedir"]


def test_two_token_span_gets_B_E_without_I():
    offsets = [(0, 3), (4, 8)]
    spans = [Span(0, 8, "informar")]
    assert char_spans_to_bioes(spans, offsets) == ["B-informar", "E-informar"]


def test_special_tokens_and_gaps_are_O():
    # offset (0,0) = special token; a token outside any span = O
    offsets = [(0, 0), (0, 2), (3, 7), (0, 0)]
    spans = [Span(0, 2, "saudar")]
    assert char_spans_to_bioes(spans, offsets) == ["O", "S-saudar", "O", "O"]
