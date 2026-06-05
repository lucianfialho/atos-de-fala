from chomsky.eval import span_prf1, per_act_f1
from chomsky.schema import Annotation, Span


def test_perfect_prediction_scores_one():
    gold = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])]
    pred = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])]
    m = span_prf1(gold, pred)
    assert m == {"precision": 1.0, "recall": 1.0, "f1": 1.0}


def test_half_correct_prediction():
    # gold 2 spans, pred 2 spans, 1 exact match -> P=0.5 R=0.5 F1=0.5
    gold = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])]
    pred = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "sugerir")])]
    m = span_prf1(gold, pred)
    assert m == {"precision": 0.5, "recall": 0.5, "f1": 0.5}


def test_per_act_f1_reports_each_gold_act():
    gold = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])]
    pred = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "sugerir")])]
    by_act = per_act_f1(gold, pred)
    assert by_act["saudar"]["f1"] == 1.0
    assert by_act["pedir"]["f1"] == 0.0  # missed (predicted as sugerir)


def test_empty_dataset_scores_zero():
    assert span_prf1([], []) == {"precision": 0.0, "recall": 0.0, "f1": 0.0}
