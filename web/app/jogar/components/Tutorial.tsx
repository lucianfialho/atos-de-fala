"use client";

const STORAGE_KEY = "chomsky_seen_tutorial";

interface Props {
  onDismiss: () => void;
}

export default function Tutorial({ onDismiss }: Props) {
  function handleDismiss() {
    try { localStorage.setItem(STORAGE_KEY, "1"); } catch { /* SSR/privacy */ }
    onDismiss();
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Como funciona"
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 100,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "24px",
        background: "rgba(12, 10, 9, 0.35)",
        backdropFilter: "blur(4px)",
      }}
    >
      <div
        className="card"
        style={{
          maxWidth: 440,
          width: "100%",
          padding: "36px 32px",
          display: "flex",
          flexDirection: "column",
          gap: 18,
          position: "relative",
        }}
      >
        <h2 className="display" style={{ fontSize: 26, lineHeight: 1.2 }}>
          Como funciona
        </h2>

        <p style={{ fontSize: 15, color: "var(--body)", lineHeight: 1.65 }}>
          Um <strong>ato de fala</strong> é a intenção comunicativa por trás de uma frase —
          por exemplo, <em>informar</em>, <em>pedir</em> ou <em>agradecer</em>.
          A IA já fez uma classificação; você confirma ou corrige.
        </p>

        <ul style={{ fontSize: 15, color: "var(--body)", lineHeight: 1.7, paddingLeft: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: 8 }}>
          <li>
            <span style={{ display: "inline-block", minWidth: 24, fontWeight: 600, color: "var(--ink)" }}>✓</span>
            <strong>Certo</strong> — a classificação da IA está correta
          </li>
          <li>
            <span style={{ display: "inline-block", minWidth: 24, fontWeight: 600, color: "var(--ink)" }}>✗</span>
            <strong>Corrigir</strong> — escolha o ato correto no menu
          </li>
          <li>
            <span style={{ display: "inline-block", minWidth: 24, fontWeight: 600, color: "var(--muted)" }}>?</span>
            <strong>Não sei</strong> — sem problema, pule sem votar
          </li>
        </ul>

        <p style={{ fontSize: 13, color: "var(--muted)", lineHeight: 1.5 }}>
          Cada trecho destacado na frase corresponde a um cartão abaixo.
          Você precisa escolher uma opção em <em>cada</em> cartão para avançar.
        </p>

        <button
          className="btn-ink"
          onClick={handleDismiss}
          style={{ marginTop: 4, height: 48, fontSize: 16 }}
          autoFocus
        >
          Entendi, bora →
        </button>
      </div>
    </div>
  );
}

export function hasSeen(): boolean {
  try { return localStorage.getItem(STORAGE_KEY) === "1"; } catch { return false; }
}
