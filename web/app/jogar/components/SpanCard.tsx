"use client";
import { ACTS } from "@/lib/taxonomy";
import SuggestBox from "./SuggestBox";

type Span = { id: number; char_start: number; char_end: number; ai_act: string };
type VerdictMap = Record<number, { verdict: string; correctedAct?: string }>;

interface Props {
  s: Span;
  text: string;
  verdicts: VerdictMap;
  setVerdicts: (v: VerdictMap) => void;
  onSuggest: (spanId: number, text: string) => void;
}

export default function SpanCard({ s, text, verdicts, setVerdicts, onSuggest }: Props) {
  const v = verdicts[s.id]?.verdict ?? "agree";
  return (
    <div className="card">
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 10, marginBottom: 16 }}>
        <span style={{ fontStyle: "italic", fontWeight: 500, color: "var(--ink)", fontSize: 15 }}>
          &ldquo;{text.slice(s.char_start, s.char_end)}&rdquo;
        </span>
        <span className="label" style={{ marginRight: 4 }}>IA classifica como</span>
        <span className="badge">{s.ai_act}</span>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: v === "disagree" ? 14 : 0 }}>
        <button
          className={v === "agree" ? "btn-ink" : "btn-outline"}
          aria-pressed={v === "agree"}
          onClick={() => setVerdicts({ ...verdicts, [s.id]: { verdict: "agree" } })}
          style={{ height: 36, padding: "0 16px", fontSize: 14 }}
        >
          ✓ certo
        </button>
        <button
          className={v === "disagree" ? "btn-ink" : "btn-outline"}
          aria-pressed={v === "disagree"}
          onClick={() => setVerdicts({ ...verdicts, [s.id]: { verdict: "disagree", correctedAct: ACTS[0] } })}
          style={{ height: 36, padding: "0 16px", fontSize: 14 }}
        >
          ✗ corrigir
        </button>
      </div>

      {v === "disagree" && (
        <div className="field" style={{ marginBottom: 8 }}>
          <span className="field-label">Ato correto</span>
          <div className="select-wrapper">
            <select
              value={verdicts[s.id]?.correctedAct ?? ACTS[0]}
              onChange={(e) => setVerdicts({ ...verdicts, [s.id]: { verdict: "disagree", correctedAct: e.target.value } })}
            >
              {ACTS.map((a) => <option key={a} value={a}>{a}</option>)}
            </select>
          </div>
        </div>
      )}

      <details style={{ marginTop: 12 }}>
        <summary style={{ cursor: "pointer", fontSize: 13, fontWeight: 500, color: "var(--muted)", listStyle: "none", userSelect: "none" }}>
          ＋ sugerir outra forma (bônus)
        </summary>
        <SuggestBox onSubmit={(t) => onSuggest(s.id, t)} />
      </details>
    </div>
  );
}
