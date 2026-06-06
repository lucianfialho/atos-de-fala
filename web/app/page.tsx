"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { getOrCreateParticipantId } from "@/lib/participant";

const REGIONS = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"];

export default function Onboarding() {
  const router = useRouter();
  const [f, setF] = useState({ ageBand: "", gender: "", region: "", education: "" });
  const [consent, setConsent] = useState(false);
  const ready = consent && f.ageBand && f.gender && f.region && f.education;

  async function start() {
    const id = getOrCreateParticipantId();
    await fetch("/api/participant", { method: "POST", body: JSON.stringify({ id, ...f }) });
    router.push("/jogar");
  }

  return (
    <main style={{ maxWidth: 480, margin: "40px auto", fontFamily: "system-ui", padding: "0 16px" }}>
      <h1>Atos de Fala — ajude a IA a entender o português</h1>
      <p>Anônimo. Conte um pouco sobre você (pra pesquisa de como cada perfil interpreta intenções):</p>
      <label>Faixa de idade
        <select value={f.ageBand} onChange={(e) => setF({ ...f, ageBand: e.target.value })}>
          <option value="">—</option>{["18-24","25-34","35-44","45-54","55+"].map((v) => <option key={v}>{v}</option>)}
        </select>
      </label>
      <label>Gênero
        <select value={f.gender} onChange={(e) => setF({ ...f, gender: e.target.value })}>
          <option value="">—</option>{["feminino","masculino","outro","prefiro não dizer"].map((v) => <option key={v}>{v}</option>)}
        </select>
      </label>
      <label>Estado (UF)
        <select value={f.region} onChange={(e) => setF({ ...f, region: e.target.value })}>
          <option value="">—</option>{REGIONS.map((v) => <option key={v}>{v}</option>)}
        </select>
      </label>
      <label>Escolaridade
        <select value={f.education} onChange={(e) => setF({ ...f, education: e.target.value })}>
          <option value="">—</option>{["fundamental","médio","superior","pós"].map((v) => <option key={v}>{v}</option>)}
        </select>
      </label>
      <label style={{ display: "block", margin: "12px 0" }}>
        <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />
        {" "}Concordo que minhas respostas entrem em um dataset aberto (CC BY).
      </label>
      <button disabled={!ready} onClick={start}>Começar</button>
    </main>
  );
}
