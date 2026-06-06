"use client";
import { useState } from "react";

export default function SuggestBox({ onSubmit }: { onSubmit: (t: string) => void }) {
  const [t, setT] = useState("");
  return (
    <div style={{ display: "flex", gap: 8, marginTop: 10, alignItems: "center" }}>
      <input
        className="field-input"
        value={t}
        onChange={(e) => setT(e.target.value)}
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
        className="btn-outline"
        onClick={() => { onSubmit(t); setT(""); }}
        style={{ height: 40, padding: "0 14px", fontSize: 13, flexShrink: 0 }}
      >
        ＋ Adicionar
      </button>
    </div>
  );
}
