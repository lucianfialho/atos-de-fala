"use client";

const REGIONS = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"];

type Fields = { ageBand: string; gender: string; region: string; education: string };

interface Props {
  f: Fields;
  setF: (v: Fields) => void;
  consent: boolean;
  setConsent: (v: boolean) => void;
  ready: boolean;
  onStart: () => void;
}

export default function OnboardingForm({ f, setF, consent, setConsent, ready, onStart }: Props) {
  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <p className="label" style={{ marginBottom: 4 }}>Sobre você</p>

      <div className="field">
        <span className="field-label">Faixa de idade</span>
        <div className="select-wrapper">
          <select value={f.ageBand} onChange={(e) => setF({ ...f, ageBand: e.target.value })}>
            <option value="">— selecione —</option>
            {["18-24","25-34","35-44","45-54","55+"].map((v) => <option key={v} value={v}>{v}</option>)}
          </select>
        </div>
      </div>

      <div className="field">
        <span className="field-label">Gênero</span>
        <div className="select-wrapper">
          <select value={f.gender} onChange={(e) => setF({ ...f, gender: e.target.value })}>
            <option value="">— selecione —</option>
            {["feminino","masculino","outro","prefiro não dizer"].map((v) => <option key={v} value={v}>{v}</option>)}
          </select>
        </div>
      </div>

      <div className="field">
        <span className="field-label">Estado (UF)</span>
        <div className="select-wrapper">
          <select value={f.region} onChange={(e) => setF({ ...f, region: e.target.value })}>
            <option value="">— selecione —</option>
            {REGIONS.map((v) => <option key={v} value={v}>{v}</option>)}
          </select>
        </div>
      </div>

      <div className="field">
        <span className="field-label">Escolaridade</span>
        <div className="select-wrapper">
          <select value={f.education} onChange={(e) => setF({ ...f, education: e.target.value })}>
            <option value="">— selecione —</option>
            {["fundamental","médio","superior","pós"].map((v) => <option key={v} value={v}>{v}</option>)}
          </select>
        </div>
      </div>

      <label style={{ display: "flex", alignItems: "flex-start", gap: 10, cursor: "pointer", fontSize: 14, color: "var(--body)", lineHeight: 1.55, paddingTop: 4 }}>
        <input
          type="checkbox"
          checked={consent}
          onChange={(e) => setConsent(e.target.checked)}
          style={{ marginTop: 3, accentColor: "var(--primary)", flexShrink: 0 }}
        />
        Concordo que minhas respostas entrem em um{" "}
        <a href="/termo" style={{ color: "var(--ink)", textDecoration: "underline", textUnderlineOffset: 2 }}>
          dataset aberto (CC BY)
        </a>
        .
      </label>

      <button
        className="btn-ink"
        disabled={!ready}
        onClick={onStart}
        style={{ marginTop: 8, width: "100%", height: 48, fontSize: 16 }}
      >
        Começar
      </button>
    </div>
  );
}
