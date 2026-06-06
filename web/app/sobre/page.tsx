import { SobreSections } from "./SobreSections";

const WRAP: React.CSSProperties = {
  minHeight: "100vh",
  background: "var(--canvas)",
  padding: "48px 24px 80px",
};

const INNER: React.CSSProperties = {
  maxWidth: 720,
  margin: "0 auto",
};

const BACK_LINK: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
  fontSize: 14,
  color: "var(--muted)",
  textDecoration: "none",
  marginBottom: 32,
};

const CARD: React.CSSProperties = {
  padding: "40px 48px",
};

const H1: React.CSSProperties = {
  fontSize: "clamp(26px, 4vw, 36px)",
  marginBottom: 8,
};

const SUBTITLE: React.CSSProperties = {
  fontSize: 14,
  color: "var(--muted)",
  marginBottom: 40,
  lineHeight: 1.5,
};

const CTA_WRAP: React.CSSProperties = {
  marginTop: 8,
  display: "flex",
};

export default function SobrePage() {
  return (
    <div style={WRAP}>
      <div style={INNER}>
        <a href="/" style={BACK_LINK}>← voltar</a>
        <div className="card" style={CARD}>
          <p className="label" style={{ marginBottom: 12 }}>PROJETO ABERTO</p>
          <h1 className="display" style={H1}>
            Sobre o Atos de Fala
          </h1>
          <p style={SUBTITLE}>
            um projeto aberto pra ensinar a IA a entender a intenção em português
          </p>
          <SobreSections />
          <div style={CTA_WRAP}>
            <a
              href="/#participar"
              className="btn-ink"
              style={{ borderRadius: 9999 }}
            >
              Participar
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
