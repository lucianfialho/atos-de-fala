from chomsky.collect.models import Vote, SpanResolution


def test_vote_is_frozen_and_holds_fields():
    v = Vote(span_id=1, verdict="disagree", corrected_act="sugerir", reliability=0.8)
    assert v.span_id == 1 and v.corrected_act == "sugerir" and v.reliability == 0.8


def test_span_resolution_holds_fields():
    r = SpanResolution(span_id=1, act="pedir", agreement=0.75, is_gold=True)
    assert r.act == "pedir" and r.is_gold is True and r.agreement == 0.75
