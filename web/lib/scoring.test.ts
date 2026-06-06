import { describe, it, expect } from "vitest";
import {
  streakMultiplier, pointsForVote, updateReliability, applyItemOutcome,
  POINTS_SUGGESTION, POINTS_SUGGESTION_CONFIRMED,
} from "./scoring";

describe("scoring mirrors score.py", () => {
  it("streak tiers", () => {
    expect(streakMultiplier(0)).toBe(1.0);
    expect(streakMultiplier(4)).toBe(1.0);
    expect(streakMultiplier(5)).toBe(1.5);
    expect(streakMultiplier(9)).toBe(1.5);
    expect(streakMultiplier(10)).toBe(2.0);
  });
  it("points per vote", () => {
    expect(pointsForVote(0)).toBe(10);
    expect(pointsForVote(5)).toBe(15);
    expect(pointsForVote(10)).toBe(20);
  });
  it("suggestion constants", () => {
    expect(POINTS_SUGGESTION).toBe(20);
    expect(POINTS_SUGGESTION_CONFIRMED).toBe(50);
  });
  it("reliability rises/falls and clamps", () => {
    expect(updateReliability(0.5, true)).toBeCloseTo(0.55, 10);
    expect(updateReliability(0.5, false)).toBeCloseTo(0.4, 10);
    expect(updateReliability(1.0, true)).toBe(1.0);
    expect(updateReliability(0.0, false)).toBe(0.0);
  });
});

describe("applyItemOutcome", () => {
  const base = { points: 0, streak: 0, reliability: 0.5, itemsDone: 0 };
  it("normal item: +points*nSpans, streak+1, reliability unchanged", () => {
    const r = applyItemOutcome(base, 2, null);
    expect(r).toEqual({ points: 20, streak: 1, reliability: 0.5, itemsDone: 1 });
  });
  it("honeypot correct raises reliability", () => {
    const r = applyItemOutcome(base, 1, true);
    expect(r.reliability).toBeCloseTo(0.55, 10);
    expect(r.streak).toBe(1);
  });
  it("honeypot wrong lowers reliability", () => {
    const r = applyItemOutcome(base, 1, false);
    expect(r.reliability).toBeCloseTo(0.4, 10);
  });
});
