"use client";
import { useState } from "react";

// Collects alternative phrasings for a span. Each added suggestion is submitted (onSubmit,
// which POSTs it) AND shown as a removable tag — a visible receipt of what you contributed.
export default function SuggestBox({ onSubmit }: { onSubmit: (t: string) => void }) {
  const [t, setT] = useState("");
  const [added, setAdded] = useState<string[]>([]);

  function add() {
    const v = t.trim();
    if (!v) return;
    onSubmit(v);
    setAdded((a) => [...a, v]);
    setT("");
  }

  return (
    <div style={{ marginTop: 10 }}>
      {added.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 8 }}>
          {added.map((s, i) => (
            <span key={i} className="suggestion-tag">
              {s}
              <button
                type="button"
                aria-label={`remover "${s}"`}
                className="suggestion-tag-x"
                onClick={() => setAdded((a) => a.filter((_, j) => j !== i))}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <input
          className="field-input"
          value={t}
          onChange={(e) => setT(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); add(); } }}
          placeholder="mesma intenção, outras palavras…"
          style={{
            flex: 1,
            background: "var(--surface-card)",
            border: "1px solid var(--hairline-strong)",
            borderRadius: 8,
            height: 40,
            padding: "0 14px",
            fontSize: 14,
            fontFamily: "inherit",
            color: "var(--ink)",
            outline: "none",
          }}
          onFocus={(e) => { e.currentTarget.style.borderColor = "var(--ink)"; }}
          onBlur={(e) => { e.currentTarget.style.borderColor = "var(--hairline-strong)"; }}
        />
        <button
          type="button"
          className="btn-outline"
          onClick={add}
          style={{ height: 40, padding: "0 14px", fontSize: 13, flexShrink: 0 }}
        >
          ＋ Adicionar
        </button>
      </div>
    </div>
  );
}
