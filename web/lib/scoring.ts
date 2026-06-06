// Mirror of src/chomsky/collect/score.py — keep values identical so client display and
// server-side stats agree with the Python aggregation. Suggestions never penalize.

export const POINTS_VOTE_BASE = 10;
export const POINTS_SUGGESTION = 20;            // provisional, on submit
export const POINTS_SUGGESTION_CONFIRMED = 50;  // retroactive, when adjudicator confirms

export type Stats = { points: number; streak: number; reliability: number; itemsDone: number };

export function streakMultiplier(streak: number): number {
  if (streak < 5) return 1.0;
  if (streak < 10) return 1.5;
  return 2.0;
}

export function pointsForVote(streak: number, base = POINTS_VOTE_BASE): number {
  return Math.round(base * streakMultiplier(streak));
}

export function updateReliability(reliability: number, honeypotCorrect: boolean): number {
  const r = honeypotCorrect ? reliability + 0.1 * (1.0 - reliability) : reliability * 0.8;
  return Math.max(0.0, Math.min(1.0, r));
}

// One item judged: award points for each evaluated span at the current streak, bump streak,
// update reliability only when the item was a honeypot (honeypotCorrect is null otherwise).
export function applyItemOutcome(stats: Stats, nSpans: number, honeypotCorrect: boolean | null): Stats {
  return {
    points: stats.points + pointsForVote(stats.streak) * nSpans,
    streak: stats.streak + 1,
    reliability: honeypotCorrect === null ? stats.reliability : updateReliability(stats.reliability, honeypotCorrect),
    itemsDone: stats.itemsDone + 1,
  };
}
