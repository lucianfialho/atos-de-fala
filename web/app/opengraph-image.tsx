import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "Atos de Fala — ensine a IA a entender a intenção em português";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OG() {
  return new ImageResponse(
    (
      <div
        style={{
          height: "100%",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "#eeefe9",
          padding: "64px 72px",
          fontFamily: "sans-serif",
          color: "#23251d",
        }}
      >
        {/* Top: brand label */}
        <div
          style={{
            display: "flex",
            fontSize: 26,
            fontWeight: 700,
            letterSpacing: 1,
            textTransform: "uppercase",
            color: "#6c6e63",
          }}
        >
          atos de fala · dataset aberto
        </div>

        {/* Middle: headline + annotated snippet */}
        <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>
          {/* Headline — split into three rows to avoid overflow on 1200px */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 0,
              fontSize: 64,
              fontWeight: 800,
              lineHeight: 1.08,
              letterSpacing: -1.5,
              color: "#23251d",
            }}
          >
            <span style={{ display: "flex" }}>Ensine a IA a entender a</span>
            <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 12 }}>
              <span
                style={{
                  display: "flex",
                  background: "#f7a501",
                  padding: "0 12px",
                }}
              >
                intenção
              </span>
              <span style={{ display: "flex" }}>do que a</span>
            </div>
            <span style={{ display: "flex" }}>gente diz.</span>
          </div>

          {/* Annotated snippet */}
          <div
            style={{
              display: "flex",
              flexDirection: "row",
              alignItems: "center",
              gap: 16,
              fontSize: 28,
            }}
          >
            <span
              style={{
                display: "flex",
                borderBottom: "4px solid #f7a501",
                paddingBottom: 2,
                color: "#23251d",
              }}
            >
              "Você pode me passar o sal?"
            </span>
            <span
              style={{
                display: "flex",
                background: "#ffffff",
                border: "1px solid #bfc1b7",
                borderRadius: 9999,
                padding: "6px 18px",
                fontSize: 22,
                color: "#23251d",
              }}
            >
              pedido, não pergunta
            </span>
          </div>
        </div>

        {/* Bottom: URL + locale */}
        <div style={{ display: "flex", fontSize: 26, color: "#4d4f46" }}>
          português brasileiro · anônimo · atos-de-fala.vercel.app
        </div>
      </div>
    ),
    { ...size }
  );
}
