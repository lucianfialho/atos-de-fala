"use client";

import { useState } from "react";
import { getActTint } from "@/lib/actColors";
import { Arrow } from "@/app/components/marks";

type Segment = { text: string; act: string | null };

const DEFAULT_INPUT = "Bom dia! Você pode me revisar o relatório? Obrigado.";

const STATIC_SEGMENTS: Segment[] = [
  { text: "Bom dia!", act: "saudar" },
  { text: " ", act: null },
  { text: "Você pode me revisar o relatório?", act: "pedir" },
  { text: " ", act: null },
  { text: "Obrigado.", act: "agradecer" },
];

export default function LiveDemo() {
  const [inputText, setInputText] = useState(DEFAULT_INPUT);
  const [segments, setSegments] = useState<Segment[]>(STATIC_SEGMENTS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hasPedir = segments.some((s) => s.act === "pedir");

  async function annotate() {
    if (!inputText.trim() || loading) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/demo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: inputText }),
      });
      if (res.status === 503) {
        setError("coldstart");
        // keep last good annotation — do not update segments
        return;
      }
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setError(data.error ?? "não consegui anotar agora");
        return;
      }
      const data = await res.json();
      if (data.segments && Array.isArray(data.segments)) {
        setSegments(data.segments as Segment[]);
        setError(null);
      }
    } catch {
      setError("não consegui anotar agora");
    } finally {
      setLoading(false);
    }
  }

  function handleKey(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") annotate();
  }

  return (
    <figure className="demo-card" aria-label="Demo interativo: anote sua frase com o modelo">
      <figcaption className="demo-card-head">
        <span className="demo-card-dot" aria-hidden="true" />
        <span className="demo-card-filename">o nosso modelo anotou:</span>
      </figcaption>

      {/* Input row */}
      <div className="live-demo-input-row">
        <input
          className="live-demo-input"
          type="text"
          maxLength={200}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Digite uma frase…"
          aria-label="Frase para anotar"
          disabled={loading}
        />
        <button
          className="btn-ink live-demo-btn"
          onClick={annotate}
          disabled={loading || !inputText.trim()}
          aria-busy={loading}
        >
          {loading ? "anotando…" : "anotar"}
        </button>
      </div>

      {/* Error / cold-start notice */}
      {error === "coldstart" && (
        <p className="live-demo-notice" role="status">
          o modelo está acordando, tenta de novo em alguns segundos
        </p>
      )}
      {error && error !== "coldstart" && (
        <p className="live-demo-notice live-demo-notice-error" role="alert">
          {error}
        </p>
      )}

      {/* Annotated sentence — renders inline as a reading-flow sentence */}
      <div className="live-demo-sentence">
        {segments.map((seg, i) => {
          if (!seg.act) {
            return <span key={i} className="live-demo-plain">{seg.text}</span>;
          }
          const tint = getActTint(seg.act);
          return (
            <span key={i} className="live-demo-seg">
              <span
                className="live-demo-seg-text"
                style={{ ["--act-line" as string]: tint.text }}
              >
                {seg.text}
              </span>
              <span
                className="live-demo-pill"
                style={{ background: tint.bg, color: tint.text, borderColor: tint.border }}
              >
                {seg.act}
              </span>
            </span>
          );
        })}
      </div>

      {/* Hand-drawn arrow + note — shown when a "pedir" segment is present */}
      {hasPedir && (
        <div className="demo-arrow" aria-hidden="true">
          <Arrow width={64} height={50} />
          <span className="demo-arrow-note">pedido, não pergunta!</span>
        </div>
      )}
    </figure>
  );
}
