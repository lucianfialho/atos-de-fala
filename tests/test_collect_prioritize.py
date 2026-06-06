from atos.collect.prioritize import compute_priorities
from atos.collect.models import Vote


def _v(verdict, corrected=None, rel=1.0):
    return Vote(span_id=0, verdict=verdict, corrected_act=corrected, reliability=rel)


def test_contested_span_scores_higher_than_agreed_span():
    spans = [
        {"span_id": 1, "item_id": 10, "ai_act": "pedir"},
        {"span_id": 2, "item_id": 20, "ai_act": "pedir"},
    ]
    votes = {
        1: [_v("agree"), _v("agree"), _v("agree")],                 # full agreement
        2: [_v("agree"), _v("disagree", "perguntar")],             # split
    }
    pr = compute_priorities(spans, votes, w_rar=0.0)  # isolate disagreement
    assert pr[20] > pr[10]


def test_item_priority_is_max_over_its_spans():
    spans = [
        {"span_id": 1, "item_id": 10, "ai_act": "pedir"},
        {"span_id": 2, "item_id": 10, "ai_act": "pedir"},
    ]
    votes = {1: [_v("agree"), _v("agree")], 2: [_v("agree"), _v("disagree", "sugerir")]}
    pr = compute_priorities(spans, votes, w_rar=0.0)
    # item 10's priority = the contested span's score, not the agreed one
    assert pr[10] > 0


def test_unvoted_item_gets_rarity_only_priority():
    spans = [
        {"span_id": 1, "item_id": 10, "ai_act": "informar"},  # common (x3)
        {"span_id": 2, "item_id": 10, "ai_act": "informar"},
        {"span_id": 3, "item_id": 11, "ai_act": "informar"},
        {"span_id": 4, "item_id": 20, "ai_act": "oferecer"},  # rare (x1)
    ]
    pr = compute_priorities(spans, {}, w_dis=0.0)  # no votes; rarity only
    assert pr[20] > pr[10]  # rare act floats up over common act


def test_no_spans_returns_empty():
    assert compute_priorities([], {}) == {}
