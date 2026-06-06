"use client";
import { useEffect, useRef, useState } from "react";
import { getOrCreateParticipantId } from "@/lib/participant";
import SpanCard from "./components/SpanCard";
import InlineSentence from "./components/InlineSentence";
import Tutorial, { hasSeen } from "./components/Tutorial";
import GameHeader from "./components/GameHeader";
import EmptyState from "./components/EmptyState";

type Span = { id: number; char_start: number; char_end: number; ai_act: string };
type Item = { id: number; text: string; spans: Span[] };
type VerdictState = { verdict: "agree" | "disagree" | "skip"; correctedAct?: string };
type VerdictMap = Record<number, VerdictState>;

export default function Jogar() {
  const [pid, setPid] = useState<string>("");
  const [item, setItem] = useState<Item | null>(null);
  const [verdicts, setVerdicts] = useState<VerdictMap>({});
  const [points, setPoints] = useState(0);
  const [streak, setStreak] = useState(0);
  const [sessionCount, setSessionCount] = useState(0);
  const [showTutorial, setShowTutorial] = useState(false);
  const [floats, setFloats] = useState<{ id: number; delta: number }[]>([]);
  const [pointsAnimate, setPointsAnimate] = useState(false);
  const [streakAnimate, setStreakAnimate] = useState(false);
  const floatId = useRef(0);
  const prevPoints = useRef(0);
  const prevStreak = useRef(0);

  useEffect(() => {
    setPid(getOrCreateParticipantId());
    setShowTutorial(!hasSeen());
  }, []);

  useEffect(() => { if (pid) loadNext(pid); }, [pid]);

  async function loadNext(p: string) {
    const r = await fetch(`/api/next-item?participant=${p}`).then((x) => x.json());
    setItem(r.item ?? null);
    setVerdicts({});
  }

  const allAnswered =
    item !== null &&
    item.spans.length > 0 &&
    item.spans.every((s) => verdicts[s.id] !== undefined);

  async function submit() {
    if (!item || !allAnswered) return;
    const votes = item.spans
      .filter((s) => verdicts[s.id]?.verdict === "agree" || verdicts[s.id]?.verdict === "disagree")
      .map((s) => ({
        spanId: s.id,
        verdict: verdicts[s.id].verdict as "agree" | "disagree",
        correctedAct: verdicts[s.id].verdict === "disagree" ? verdicts[s.id].correctedAct : undefined,
      }));

    if (votes.length === 0) {
      setSessionCount((c) => c + 1);
      loadNext(pid);
      return;
    }

    const r = await fetch("/api/vote", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ participant: pid, itemId: item.id, votes }),
    }).then((x) => x.json());

    const newPoints: number = r.stats.points;
    const newStreak: number = r.stats.streak;
    const delta = newPoints - prevPoints.current;

    if (delta > 0) {
      const id = ++floatId.current;
      setFloats((prev) => [...prev, { id, delta }]);
      setTimeout(() => setFloats((prev) => prev.filter((f) => f.id !== id)), 1400);
      setPointsAnimate(true);
      setTimeout(() => setPointsAnimate(false), 500);
    }
    if (newStreak > prevStreak.current) {
      setStreakAnimate(true);
      setTimeout(() => setStreakAnimate(false), 600);
    }

    prevPoints.current = newPoints;
    prevStreak.current = newStreak;
    setPoints(newPoints);
    setStreak(newStreak);
    setSessionCount((c) => c + 1);
    loadNext(pid);
  }

  async function suggest(spanId: number, text: string) {
    if (!text.trim()) return;
    await fetch("/api/suggestion", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ participant: pid, spanId, text }),
    });
  }

  if (!item) return <EmptyState points={points} sessionCount={sessionCount} />;

  return (
    <>
      {showTutorial && <Tutorial onDismiss={() => setShowTutorial(false)} />}
      <main style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", padding: "0 24px 80px" }}>
        <GameHeader sessionCount={sessionCount} points={points} streak={streak} pointsAnimate={pointsAnimate} streakAnimate={streakAnimate} floats={floats} />
        <div style={{ width: "100%", maxWidth: 680 }}>
          <InlineSentence text={item.text} spans={item.spans} />
          <div style={{ display: "flex", flexDirection: "column", gap: 16, marginBottom: 28 }}>
            {item.spans.map((s, i) => (
              <SpanCard key={s.id} s={s} spanIndex={i} text={item.text} verdicts={verdicts} setVerdicts={setVerdicts} onSuggest={suggest} />
            ))}
          </div>
          {!allAnswered && (
            <p style={{ fontSize: 13, color: "var(--muted)", textAlign: "center", marginBottom: 12 }}>
              Escolha uma opção em cada cartão para avançar
            </p>
          )}
          <button className="btn-ink" onClick={submit} disabled={!allAnswered} aria-disabled={!allAnswered} style={{ width: "100%", height: 48, fontSize: 16 }}>
            Próxima →
          </button>
        </div>
      </main>
    </>
  );
}
