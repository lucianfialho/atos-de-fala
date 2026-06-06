"""Active-learning triage (fatia C): score items so the game serves high-information
spans first. Pure (no DB) so it stays unit-testable; the CLI feeds it rows from db.py.

priority(item) = max over its spans of:
    w_dis * (1 - weighted_agreement)   # human disagreement — contested spans (0 if unvoted)
  + w_rar * (1 - count(act)/max_count) # act rarity — floats up under-represented acts,
                                        #   so unvoted-but-rare items still surface

Disagreement is the reliable day-one signal (no model needed, no cold-start); rarity covers
items nobody has voted on yet. Model-uncertainty is a later overlay (needs a human-gold retrain).
"""
from collections import Counter
from typing import Dict, List
from atos.collect.models import Vote
from atos.collect.aggregate import resolve_span


def compute_priorities(
    spans: List[Dict],
    votes_by_span: Dict[int, List[Vote]],
    w_dis: float = 1.0,
    w_rar: float = 0.5,
    threshold: float = 0.66,
) -> Dict[int, float]:
    """spans: [{span_id, item_id, ai_act}]; votes_by_span: {span_id: [Vote]}."""
    counts = Counter(sp["ai_act"] for sp in spans)
    max_count = max(counts.values()) if counts else 1
    out: Dict[int, float] = {}
    for sp in spans:
        votes = votes_by_span.get(sp["span_id"], [])
        # unvoted span: 0 disagreement (we don't know), not max
        dis = 1.0 - resolve_span(sp["ai_act"], votes, threshold).agreement if votes else 0.0
        rar = 1.0 - counts[sp["ai_act"]] / max_count
        score = w_dis * dis + w_rar * rar
        out[sp["item_id"]] = max(out.get(sp["item_id"], 0.0), score)
    return out
