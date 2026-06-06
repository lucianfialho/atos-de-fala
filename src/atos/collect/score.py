"""Scoring + reliability. Suggestions are an OPTIONAL bonus and never penalize. The only
downward pressure is the honeypot: getting a known-answer item wrong lowers reliability,
which is the WEIGHT a voter's votes get in aggregation (see aggregate.resolve_span)."""

POINTS_VOTE_BASE = 10
POINTS_SUGGESTION = 20            # provisional, on submit
POINTS_SUGGESTION_CONFIRMED = 50  # retroactive, when the adjudicator confirms it


def streak_multiplier(streak: int) -> float:
    if streak < 5:
        return 1.0
    if streak < 10:
        return 1.5
    return 2.0


def points_for_vote(streak: int, base: int = POINTS_VOTE_BASE) -> int:
    return round(base * streak_multiplier(streak))


def update_reliability(reliability: float, honeypot_correct: bool) -> float:
    """EMA toward 1.0 on a correct honeypot; multiplicative decay on a wrong one. Clamped."""
    r = reliability + 0.1 * (1.0 - reliability) if honeypot_correct else reliability * 0.8
    return max(0.0, min(1.0, r))
