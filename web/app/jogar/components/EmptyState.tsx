"use client";

interface Props {
  points: number;
  sessionCount: number;
}

export default function EmptyState({ points, sessionCount }: Props) {
  const label = sessionCount === 1 ? "frase avaliada" : "frases avaliadas";
  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px 24px",
        textAlign: "center",
      }}
    >
      <h2 className="display" style={{ fontSize: 36, marginBottom: 16 }}>
        Valeu! 🙌
      </h2>
      <p style={{ color: "var(--muted)", fontSize: 17 }}>
        Sem mais frases por agora.&nbsp;
        <span className="badge" style={{ fontSize: 14, verticalAlign: "middle" }}>
          {points} pts
        </span>
      </p>
      {sessionCount > 0 && (
        <p style={{ marginTop: 12, fontSize: 14, color: "var(--muted)" }}>
          ✓ {sessionCount} {label} nesta sessão
        </p>
      )}
    </main>
  );
}
