from chomsky.train.eval_cli import score_predictions
from chomsky.schema import Annotation, Span


def test_score_predictions_matches_gold():
    gold = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])]
    pred = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])]
    report = score_predictions(gold, pred)
    assert report["overall"]["f1"] == 1.0
    assert report["per_act"]["saudar"]["f1"] == 1.0


def test_score_predictions_partial():
    gold = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])]
    pred = [Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "sugerir")])]
    report = score_predictions(gold, pred)
    assert report["overall"]["f1"] == 0.5
    assert report["per_act"]["pedir"]["f1"] == 0.0
