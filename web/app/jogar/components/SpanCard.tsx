"use client";
import { getActTint, getIndexGlyph } from "@/lib/actColors";
import SuggestBox from "./SuggestBox";
import VerdictButtons from "./VerdictButtons";

type Span = { id: number; char_start: number; char_end: number; ai_act: string };
type Verdict = "agree" | "disagree" | "skip";
type VerdictMap = Record<number, { verdict: Verdict; correctedAct?: string }>;

interface Props {
  s: Span;
  spanIndex: number;
  text: string;
  verdicts: VerdictMap;
  setVerdicts: (v: VerdictMap) => void;
  onSuggest: (spanId: number, text: string) => void;
}

export default function SpanCard({ s, spanIndex, text, verdicts, setVerdicts, onSuggest }: Props) {
  const v = verdicts[s.id]?.verdict;
  const tint = getActTint(s.ai_act);
  const glyph = getIndexGlyph(spanIndex);

  return (
    <div className="card" style={{ borderLeft: `3px solid ${tint.border}`, transition: "box-shadow 0.15s ease" }}>
      {/* Header: index glyph + fragment + act badge */}
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 8, marginBottom: 14 }}>
        <span style={{
          fontFamily: "var(--font-inter, Inter, system-ui, sans-serif)",
          fontWeight: 700, fontSize: 13,
          color: tint.text, background: tint.bg,
          border: `1px solid ${tint.border}`,
          borderRadius: 4, padding: "1px 6px", flexShrink: 0,
        }}>
          {glyph}
        </span>
        <span style={{
          fontFamily: "var(--font-serif, Georgia, serif)",
          fontWeight: 300, fontStyle: "italic",
          color: "var(--ink)", fontSize: 15,
        }}>
          &ldquo;{text.slice(s.char_start, s.char_end)}&rdquo;
        </span>
        <span className="label" style={{ marginLeft: "auto", marginRight: 4, flexShrink: 0 }}>IA:</span>
        <span className="badge" style={{ background: tint.bg, color: tint.text, border: `1px solid ${tint.border}` }}>
          {s.ai_act}
        </span>
      </div>

      {/* Verdict buttons, correction dropdown, chosen state chip */}
      <VerdictButtons spanId={s.id} v={v} verdicts={verdicts} setVerdicts={setVerdicts} />

      {/* Suggestion box */}
      <details style={{ marginTop: 12 }}>
        <summary style={{ cursor: "pointer", fontSize: 13, fontWeight: 500, color: "var(--muted)", listStyle: "none", userSelect: "none" }}>
          ＋ sugerir outra forma (bônus)
        </summary>
        <SuggestBox onSubmit={(t) => onSuggest(s.id, t)} />
      </details>
    </div>
  );
}
