"use client";

interface FloatItem { id: number; delta: number }

interface Props {
  sessionCount: number;
  points: number;
  streak: number;
  pointsAnimate: boolean;
  streakAnimate: boolean;
  floats: FloatItem[];
}

export default function GameHeader({ sessionCount, points, streak, pointsAnimate, streakAnimate, floats }: Props) {
  return (
    <header
      style={{
        width: "100%",
        maxWidth: 680,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        gap: 10,
        padding: "20px 0 20px",
        borderBottom: "1px solid var(--hairline)",
        marginBottom: 32,
      }}
    >
      <span style={{ fontSize: 13, color: "var(--muted)", fontWeight: 500 }}>
        {sessionCount > 0 ? `✓ ${sessionCount} nesta sessão` : ""}
      </span>

      <div style={{ display: "flex", alignItems: "center", gap: 8, position: "relative" }}>
        <div style={{ position: "relative" }}>
          {floats.map((f) => (
            <span
              key={f.id}
              className="points-float"
              style={{ position: "absolute", right: 0, bottom: "100%", whiteSpace: "nowrap" }}
            >
              +{f.delta}
            </span>
          ))}
          <span
            className={`badge${pointsAnimate ? " badge-points-pop" : ""}`}
            style={{ display: "inline-flex", alignItems: "center" }}
          >
            Pontos {points}
          </span>
        </div>
        <span className={`badge${streakAnimate ? " badge-streak-pop" : ""}`}>
          Streak {streak} 🔥
        </span>
      </div>
    </header>
  );
}
