"""Weighted majority over the act each vote endorses, weighting by voter reliability.

agree -> endorses the AI's act. disagree+corrected -> endorses the corrected act.
disagree without a correction -> endorses NO act (adds to the total weight, so it lowers
the winning act's share). A span becomes gold when the winning act's weighted share
reaches `threshold`."""
from typing import Dict, List
from chomsky.collect.models import Vote, SpanResolution


def resolve_span(ai_act: str, votes: List[Vote], threshold: float = 0.66) -> SpanResolution:
    if not votes:
        return SpanResolution(span_id=-1, act=None, agreement=0.0, is_gold=False)
    span_id = votes[0].span_id
    tally: Dict[str, float] = {}
    total = 0.0
    for v in votes:
        total += v.reliability
        act = ai_act if v.verdict == "agree" else v.corrected_act
        if act is not None:
            tally[act] = tally.get(act, 0.0) + v.reliability
    if not tally:
        return SpanResolution(span_id=span_id, act=None, agreement=0.0, is_gold=False)
    act, weight = max(tally.items(), key=lambda kv: kv[1])
    agreement = weight / total if total else 0.0
    return SpanResolution(span_id=span_id, act=act, agreement=agreement, is_gold=agreement >= threshold)
