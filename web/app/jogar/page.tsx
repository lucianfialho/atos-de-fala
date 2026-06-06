"use client";
import { useEffect, useState } from "react";
import { getOrCreateParticipantId } from "@/lib/participant";
import SpanCard from "./components/SpanCard";

type Span = { id: number; char_start: number; char_end: number; ai_act: string };
type Item = { id: number; text: string; spans: Span[] };

export default function Jogar() {
  const [pid, setPid] = useState<string>("");
  const [item, setItem] = useState<Item | null>(null);
  const [verdicts, setVerdicts] = useState<Record<number, { verdict: string; correctedAct?: string }>>({});
  const [points, setPoints] = useState(0);
  const [streak, setStreak] = useState(0);

  useEffect(() => { setPid(getOrCreateParticipantId()); }, []);
  useEffect(() => { if (pid) loadNext(pid); }, [pid]);

  async function loadNext(p: string) {
    const r = await fetch(`/api/next-item?participant=${p}`).then((x) => x.json());
    setItem(r.item); setVerdicts({});
  }

  async function submit() {
    if (!item) return;
    const votes = item.spans.map((s) => ({
      spanId: s.id,
      verdict: verdicts[s.id]?.verdict ?? "agree",
      correctedAct: verdicts[s.id]?.correctedAct,
    }));
    const r = await fetch("/api/vote", { method: "POST", body: JSON.stringify({ participant: pid, itemId: item.id, votes }) }).then((x) => x.json());
    setPoints(r.stats.points); setStreak(r.stats.streak);
    loadNext(pid);
  }

  async function suggest(spanId: number, text: string) {
    if (!text.trim()) return;
    await fetch("/api/suggestion", { method: "POST", body: JSON.stringify({ participant: pid, spanId, text }) });
  }

  if (!item) {
    return (
      <main style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "40px 24px", textAlign: "center" }}>
        <h2 className="display" style={{ fontSize: 36, marginBottom: 16 }}>Valeu! 🙌</h2>
        <p style={{ color: "var(--muted)", fontSize: 17 }}>
          Sem mais frases por agora.&nbsp;
          <span className="badge" style={{ fontSize: 14, verticalAlign: "middle" }}>{points} pts</span>
        </p>
      </main>
    );
  }

  return (
    <main style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", padding: "0 24px 80px" }}>
      <header style={{ width: "100%", maxWidth: 680, display: "flex", justifyContent: "flex-end", alignItems: "center", gap: 10, padding: "20px 0 24px", borderBottom: "1px solid var(--hairline)", marginBottom: 36 }}>
        <span className="badge">Pontos {points}</span>
        <span className="badge">Streak {streak} 🔥</span>
      </header>

      <div style={{ width: "100%", maxWidth: 680 }}>
        <p className="display" style={{ fontSize: "clamp(22px, 3vw, 28px)", lineHeight: 1.45, marginBottom: 32, color: "var(--ink)" }}>
          {item.text}
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: 16, marginBottom: 32 }}>
          {item.spans.map((s) => (
            <SpanCard
              key={s.id}
              s={s}
              text={item.text}
              verdicts={verdicts}
              setVerdicts={setVerdicts}
              onSuggest={suggest}
            />
          ))}
        </div>

        <button className="btn-ink" onClick={submit} style={{ width: "100%", height: 48, fontSize: 16 }}>
          Próxima →
        </button>
      </div>
    </main>
  );
}
