// Pure next-item picker. The route supplies candidates = items the participant has NOT yet
// voted on (dedup done in SQL). Phase 1 = depth: prefer the fewest-voted items, but pick
// RANDOMLY among the ones tied at that minimum — so the order feels varied (not the same
// sentence first for everyone) while still spreading overlap evenly. Honeypot due every 7th.

export type Candidate = { id: number; isHoneypot: boolean; voteCount: number };

// Pick a random candidate from those tied at the lowest vote count (null if empty).
const fewestVotes = (xs: Candidate[]): Candidate | null => {
  if (xs.length === 0) return null;
  const min = Math.min(...xs.map((c) => c.voteCount));
  const tied = xs.filter((c) => c.voteCount === min);
  return tied[Math.floor(Math.random() * tied.length)];
};

export function pickNextItem(candidates: Candidate[], itemsDone: number): Candidate | null {
  if (candidates.length === 0) return null;
  const honeypotDue = (itemsDone + 1) % 7 === 0;
  const honeypots = candidates.filter((c) => c.isHoneypot);
  const normals = candidates.filter((c) => !c.isHoneypot);
  const primary = honeypotDue ? honeypots : normals;
  const fallback = honeypotDue ? normals : honeypots;
  return fewestVotes(primary) ?? fewestVotes(fallback);
}
