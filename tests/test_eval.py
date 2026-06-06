from atos.eval import (
    span_prf1,
    per_act_f1,
    coarsen,
    dominant_act,
    sentence_label_f1,
)
from atos.schema import Annotation, Span

MACRO = {
    "informar": "assertivo", "concordar": "assertivo", "discordar": "assertivo",
    "perguntar": "pergunta", "pedir": "diretivo", "sugerir": "diretivo",
    "oferecer": "comissivo", "prometer": "comissivo", "saudar": "expressivo",
    "agradecer": "expressivo", "desculpar": "expressivo", "despedir": "expressivo",
    "expressar_emocao": "expressivo",
}


def test_coarsen_relabels_spans_to_macro_class():
    anns = [Annotation("Oi! Vai?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])]
    out = coarsen(anns, MACRO)
    assert [s.act for s in out[0].spans] == ["expressivo", "diretivo"]
    assert out[0].spans[0].start == 0 and out[0].spans[0].end == 3  # offsets preserved


def test_coarsen_keeps_unmapped_act_name():
    anns = [Annotation("x", [Span(0, 1, "desconhecido")])]
    assert coarsen(anns, MACRO)[0].spans[0].act == "desconhecido"


def test_dominant_act_picks_widest_char_coverage():
    # pedir covers 4 chars, saudar covers 3 -> pedir dominates
    ann = Annotation("Oi! Vai?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])
    assert dominant_act(ann) == "pedir"


def test_dominant_act_none_when_no_spans():
    assert dominant_act(Annotation("x", [])) is None


def test_sentence_label_f1_lenient_hit_when_gold_act_among_pred_spans():
    # gold = whole-sentence "pedir"; pred splits into saudar + pedir. Dominant pred is
    # saudar (wider), so accuracy misses, but lenient hit succeeds: "pedir" is predicted.
    gold = [Annotation("Ola amigo, manda?", [Span(0, 17, "pedir")])]
    pred = [Annotation("Ola amigo, manda?", [Span(0, 10, "saudar"), Span(11, 17, "pedir")])]
    rep = sentence_label_f1(gold, pred)
    assert rep["lenient_hit_rate"] == 1.0
    assert rep["accuracy"] == 0.0  # dominant pred = saudar != pedir


def test_sentence_label_f1_coarse_mapping_collapses_to_macro():
    # pedir vs sugerir disagree at fine level but both are 'diretivo' at macro level.
    gold = [Annotation("Faz isso.", [Span(0, 9, "pedir")])]
    pred = [Annotation("Faz isso.", [Span(0, 9, "sugerir")])]
    assert sentence_label_f1(gold, pred)["accuracy"] == 0.0
    assert sentence_label_f1(gold, pred, MACRO)["accuracy"] == 1.0


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
