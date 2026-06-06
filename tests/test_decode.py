from atos.train.decode import bioes_tags_to_spans
from atos.schema import Span


def test_single_S_tag():
    offsets = [(0, 2), (2, 3)]
    tags = ["S-saudar", "O"]
    assert bioes_tags_to_spans(offsets, tags) == [Span(0, 2, "saudar")]


def test_B_I_E_forms_one_span():
    offsets = [(0, 4), (5, 9), (10, 14)]
    tags = ["B-pedir", "I-pedir", "E-pedir"]
    assert bioes_tags_to_spans(offsets, tags) == [Span(0, 14, "pedir")]


def test_B_E_without_I():
    offsets = [(0, 3), (4, 8)]
    tags = ["B-informar", "E-informar"]
    assert bioes_tags_to_spans(offsets, tags) == [Span(0, 8, "informar")]


def test_two_separate_spans_with_O_between():
    offsets = [(0, 2), (3, 7), (8, 12)]
    tags = ["S-saudar", "O", "S-pedir"]
    assert bioes_tags_to_spans(offsets, tags) == [
        Span(0, 2, "saudar"),
        Span(8, 12, "pedir"),
    ]


def test_special_tokens_offset_zero_zero_are_skipped():
    offsets = [(0, 0), (0, 2), (0, 0)]
    tags = ["O", "S-saudar", "O"]
    assert bioes_tags_to_spans(offsets, tags) == [Span(0, 2, "saudar")]


def test_dangling_B_without_E_is_closed_at_sequence_end():
    offsets = [(0, 4), (5, 9)]
    tags = ["B-pedir", "I-pedir"]  # never closed with E
    assert bioes_tags_to_spans(offsets, tags) == [Span(0, 9, "pedir")]


def test_dangling_B_closed_by_O():
    offsets = [(0, 4), (5, 9)]
    tags = ["B-pedir", "O"]
    assert bioes_tags_to_spans(offsets, tags) == [Span(0, 4, "pedir")]


def test_act_switch_closes_previous_span():
    offsets = [(0, 4), (5, 9)]
    tags = ["B-pedir", "B-saudar"]  # new B closes the open one
    assert bioes_tags_to_spans(offsets, tags) == [
        Span(0, 4, "pedir"),
        Span(5, 9, "saudar"),
    ]
