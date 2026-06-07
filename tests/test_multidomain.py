from atos.train.multidomain import group_by_domain, _score
from atos.schema import Annotation, Span


def test_group_by_domain_preserves_order_and_defaults():
    records = [
        {"text": "Oi.", "spans": [{"start": 0, "end": 3, "act": "saudar"}], "domain": "sac"},
        {"text": "Que horas?", "spans": [{"start": 0, "end": 10, "act": "perguntar"}]},  # no domain
        {"text": "Tchau.", "spans": [{"start": 0, "end": 6, "act": "despedir"}], "domain": "sac"},
    ]
    groups = group_by_domain(records)
    assert list(groups.keys()) == ["sac", "geral"]  # first-seen order
    assert len(groups["sac"]) == 2
    assert groups["geral"][0] == Annotation("Que horas?", [Span(0, 10, "perguntar")])


def test_score_perfect_prediction_is_f1_one():
    gold = [Annotation("Obrigado!", [Span(0, 9, "agradecer")])]
    rep = _score(gold, gold, mode="span", macro=None)
    assert rep["n"] == 1
    assert rep["macro_f1"] == 1.0
    assert rep["span"]["f1"] == 1.0
    assert rep["per_act"]["agradecer"]["f1"] == 1.0


def test_score_wrong_act_is_f1_zero():
    gold = [Annotation("Oi.", [Span(0, 3, "saudar")])]
    pred = [Annotation("Oi.", [Span(0, 3, "informar")])]
    rep = _score(gold, pred, mode="span", macro=None)
    assert rep["macro_f1"] == 0.0
    assert rep["span"]["f1"] == 0.0


def test_score_coarse_collapses_to_macro():
    # saudar vs agradecer differ as fine acts but both are "expressivo" macro
    gold = [Annotation("Oi.", [Span(0, 3, "saudar")])]
    pred = [Annotation("Oi.", [Span(0, 3, "agradecer")])]
    macro = {"saudar": "expressivo", "agradecer": "expressivo"}
    rep = _score(gold, pred, mode="span", macro=macro)
    assert rep["span"]["f1"] == 1.0  # match after coarsening
