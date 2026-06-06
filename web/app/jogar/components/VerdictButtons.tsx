"use client";
import { ACTS } from "@/lib/taxonomy";

type Verdict = "agree" | "disagree" | "skip";
type VerdictMap = Record<number, { verdict: Verdict; correctedAct?: string }>;

interface Props {
  spanId: number;
  v: Verdict | undefined;
  verdicts: VerdictMap;
  setVerdicts: (v: VerdictMap) => void;
}

export default function VerdictButtons({ spanId, v, verdicts, setVerdicts }: Props) {
  function setVerdict(verdict: Verdict) {
    if (verdict === "disagree") {
      setVerdicts({ ...verdicts, [spanId]: { verdict: "disagree", correctedAct: ACTS[0] } });
    } else {
      setVerdicts({ ...verdicts, [spanId]: { verdict } });
    }
  }

  return (
    <>
      <div
        role="group"
        aria-label="Escolha seu veredito"
        style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: v === "disagree" ? 14 : 0 }}
      >
        <button className={v === "agree" ? "btn-ink" : "btn-outline"} aria-pressed={v === "agree"} onClick={() => setVerdict("agree")} style={{ height: 36, padding: "0 16px", fontSize: 14 }}>
          ✓ certo
        </button>
        <button className={v === "disagree" ? "btn-ink" : "btn-outline"} aria-pressed={v === "disagree"} onClick={() => setVerdict("disagree")} style={{ height: 36, padding: "0 16px", fontSize: 14 }}>
          ✗ corrigir
        </button>
        <button
          className={v === "skip" ? "btn-ink" : "btn-outline"}
          aria-pressed={v === "skip"}
          onClick={() => setVerdict("skip")}
          style={{ height: 36, padding: "0 16px", fontSize: 14, ...(v === "skip" ? { background: "var(--surface-strong)", color: "var(--muted)", border: "1px solid var(--hairline-strong)" } : {}) }}
        >
          ? não sei
        </button>
      </div>

      {v === "disagree" && (
        <div className="field" style={{ marginBottom: 8, marginTop: 4 }}>
          <span className="field-label">Ato correto</span>
          <div className="select-wrapper">
            <select
              value={verdicts[spanId]?.correctedAct ?? ACTS[0]}
              onChange={(e) => setVerdicts({ ...verdicts, [spanId]: { verdict: "disagree", correctedAct: e.target.value } })}
            >
              {ACTS.map((a) => <option key={a} value={a}>{a}</option>)}
            </select>
          </div>
        </div>
      )}

      {v !== undefined && (
        <div style={{ marginTop: 10, display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ display: "inline-block", width: 8, height: 8, borderRadius: "50%", background: v === "agree" ? "var(--success)" : v === "disagree" ? "var(--error)" : "var(--hairline-strong)", flexShrink: 0 }} />
          <span style={{ fontSize: 12, color: "var(--muted)", fontWeight: 500 }}>
            {v === "agree" ? "marcado como certo" : v === "disagree" ? "marcado para correção" : "pulado"}
          </span>
        </div>
      )}
    </>
  );
}
