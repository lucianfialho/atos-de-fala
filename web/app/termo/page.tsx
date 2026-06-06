import { TermoSections } from "./TermoSections";

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

const DATE_LINE: React.CSSProperties = {
  fontSize: 13,
  color: "var(--muted)",
  marginBottom: 40,
};

export default function TermoPage() {
  return (
    <div style={WRAP}>
      <div style={INNER}>
        <a href="/" style={BACK_LINK}>← voltar</a>
        <div className="card" style={CARD}>
          <p className="label" style={{ marginBottom: 12 }}>PESQUISA ABERTA</p>
          <h1 className="display" style={H1}>
            Termo de Consentimento e Uso de Dados
          </h1>
          <p style={DATE_LINE}>Última atualização: junho de 2026</p>
          <TermoSections />
        </div>
      </div>
    </div>
  );
}
