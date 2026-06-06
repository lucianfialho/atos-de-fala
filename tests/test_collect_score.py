from chomsky.collect.score import (
    streak_multiplier, points_for_vote, update_reliability,
    POINTS_SUGGESTION, POINTS_SUGGESTION_CONFIRMED,
)


def test_streak_multiplier_tiers():
    assert streak_multiplier(0) == 1.0
    assert streak_multiplier(4) == 1.0
    assert streak_multiplier(5) == 1.5
    assert streak_multiplier(9) == 1.5
    assert streak_multiplier(10) == 2.0


def test_points_for_vote_applies_multiplier():
    assert points_for_vote(0) == 10
    assert points_for_vote(5) == 15
    assert points_for_vote(10) == 20


def test_suggestion_point_constants():
    assert POINTS_SUGGESTION == 20 and POINTS_SUGGESTION_CONFIRMED == 50


def test_update_reliability_rises_on_correct_and_falls_on_wrong():
    assert update_reliability(0.5, True) == 0.55       # 0.5 + 0.1*0.5
    assert update_reliability(0.5, False) == 0.4       # 0.5 * 0.8


def test_update_reliability_is_clamped():
    assert update_reliability(1.0, True) == 1.0
    assert update_reliability(0.0, False) == 0.0
