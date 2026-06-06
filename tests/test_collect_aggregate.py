from chomsky.collect.aggregate import resolve_span
from chomsky.collect.models import Vote


def test_unanimous_agree_resolves_to_ai_act_as_gold():
    votes = [Vote(1, "agree", None, 1.0), Vote(1, "agree", None, 1.0)]
    r = resolve_span("pedir", votes, threshold=0.66)
    assert r.act == "pedir" and r.agreement == 1.0 and r.is_gold is True


def test_weighted_correction_can_overturn_ai_act():
    # one low-trust agree vs two high-trust corrections -> corrected act wins
    votes = [Vote(1, "agree", None, 0.2),
             Vote(1, "disagree", "sugerir", 0.9),
             Vote(1, "disagree", "sugerir", 0.9)]
    r = resolve_span("pedir", votes)
    assert r.act == "sugerir"
    assert round(r.agreement, 3) == round(1.8 / 2.0, 3)  # 0.9
    assert r.is_gold is True


def test_disagree_without_correction_lowers_agreement_below_gold():
    votes = [Vote(1, "agree", None, 1.0), Vote(1, "disagree", None, 1.0)]
    r = resolve_span("pedir", votes, threshold=0.66)
    assert r.act == "pedir" and r.agreement == 0.5 and r.is_gold is False


def test_no_votes_returns_empty_resolution():
    r = resolve_span("pedir", [])
    assert r.act is None and r.is_gold is False and r.agreement == 0.0
