from atos.stats import compute_stats
from atos.schema import Annotation, Span


def test_compute_stats_basic_counts():
    anns = [
        Annotation("a", [Span(0, 1, "informar"), Span(1, 2, "pedir")]),
        Annotation("b", [Span(0, 1, "informar")]),
        Annotation("c", []),
    ]
    s = compute_stats(anns)
    assert s["examples"] == 3
    assert s["total_spans"] == 3
    assert s["spans_per_example"] == 1.0
    assert s["examples_without_spans"] == 1
    assert s["per_act"] == {"informar": 2, "pedir": 1}  # desc order, only present acts


def test_compute_stats_with_taxonomy_includes_zeros_and_balance():
    anns = [Annotation("a", [Span(0, 1, "informar"), Span(1, 2, "informar")]),
            Annotation("b", [Span(0, 1, "pedir")])]
    s = compute_stats(anns, acts=["informar", "pedir", "saudar"])
    assert s["per_act"] == {"informar": 2, "pedir": 1, "saudar": 0}
    assert s["min_act_count"] == 0  # saudar
    assert s["max_act_count"] == 2  # informar
    assert s["balance_ratio"] == 0.0  # min/max = 0/2


def test_compute_stats_empty_dataset():
    s = compute_stats([])
    assert s["examples"] == 0
    assert s["total_spans"] == 0
    assert s["spans_per_example"] == 0.0
