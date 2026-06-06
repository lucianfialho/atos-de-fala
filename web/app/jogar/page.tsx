"use client";
import { useEffect, useState } from "react";
import { getOrCreateParticipantId } from "@/lib/participant";
import { ACTS } from "@/lib/taxonomy";

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

  if (!item) return <main style={{ maxWidth: 640, margin: "40px auto", fontFamily: "system-ui" }}><p>Sem mais frases por agora. Valeu! 🙌 ({points} pts)</p></main>;

  return (
    <main style={{ maxWidth: 640, margin: "40px auto", fontFamily: "system-ui", padding: "0 16px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", color: "#666" }}>
        <span>Pontos: {points}</span><span>Streak: {streak}🔥</span>
      </div>
      <p style={{ fontSize: 18 }}>{item.text}</p>
      {item.spans.map((s) => {
        const v = verdicts[s.id]?.verdict ?? "agree";
        return (
          <div key={s.id} style={{ border: "1px solid #e5e5e5", borderRadius: 10, padding: 12, marginBottom: 10 }}>
            <b>"{item.text.slice(s.char_start, s.char_end)}"</b> — IA diz: <code>{s.ai_act}</code>
            <div style={{ marginTop: 8 }}>
              <button onClick={() => setVerdicts({ ...verdicts, [s.id]: { verdict: "agree" } })} aria-pressed={v === "agree"}>✓ certo</button>
              <button onClick={() => setVerdicts({ ...verdicts, [s.id]: { verdict: "disagree", correctedAct: ACTS[0] } })} aria-pressed={v === "disagree"}>✗ corrigir</button>
              {v === "disagree" && (
                <select value={verdicts[s.id]?.correctedAct ?? ACTS[0]}
                        onChange={(e) => setVerdicts({ ...verdicts, [s.id]: { verdict: "disagree", correctedAct: e.target.value } })}>
                  {ACTS.map((a) => <option key={a} value={a}>{a}</option>)}
                </select>
              )}
            </div>
            <details style={{ marginTop: 6 }}>
              <summary style={{ cursor: "pointer", color: "#5b21b6" }}>＋ sugerir outra forma (bônus)</summary>
              <SuggestBox onSubmit={(t) => suggest(s.id, t)} />
            </details>
          </div>
        );
      })}
      <button onClick={submit} style={{ fontWeight: 700, padding: "10px 22px" }}>Próxima →</button>
    </main>
  );
}

function SuggestBox({ onSubmit }: { onSubmit: (t: string) => void }) {
  const [t, setT] = useState("");
  return (
    <div style={{ marginTop: 6 }}>
      <input value={t} onChange={(e) => setT(e.target.value)} placeholder="mesma intenção, outras palavras…" />
      <button onClick={() => { onSubmit(t); setT(""); }}>＋ Adicionar</button>
    </div>
  );
}
