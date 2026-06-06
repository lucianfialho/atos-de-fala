// Pure next-item picker. The route supplies candidates = items the participant has NOT yet
// voted on (dedup done in SQL). Phase 1 = depth: spread overlap by serving the fewest-voted
// item. A honeypot is due on every 7th item; if the due category is empty, fall back.

export type Candidate = { id: number; isHoneypot: boolean; voteCount: number };

const fewestVotes = (xs: Candidate[]): Candidate | null =>
  xs.length === 0 ? null : xs.reduce((a, b) => (b.voteCount < a.voteCount ? b : a));

export function pickNextItem(candidates: Candidate[], itemsDone: number): Candidate | null {
  if (candidates.length === 0) return null;
  const honeypotDue = (itemsDone + 1) % 7 === 0;
  const honeypots = candidates.filter((c) => c.isHoneypot);
  const normals = candidates.filter((c) => !c.isHoneypot);
  const primary = honeypotDue ? honeypots : normals;
  const fallback = honeypotDue ? normals : honeypots;
  return fewestVotes(primary) ?? fewestVotes(fallback);
}
