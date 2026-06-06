"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { getOrCreateParticipantId } from "@/lib/participant";
import OnboardingForm from "./components/OnboardingForm";

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
    <main style={{ minHeight: "100vh", position: "relative", overflow: "hidden", display: "flex", flexDirection: "column", alignItems: "center" }}>
      {/* Atmospheric orbs */}
      <div className="orb orb-mint" style={{ width: 520, height: 520, top: -120, left: "calc(50% - 380px)" }} />
      <div className="orb orb-peach" style={{ width: 420, height: 420, top: -80, right: "calc(50% - 400px)" }} />
      <div className="orb orb-lavender" style={{ width: 340, height: 340, top: 200, left: "calc(50% + 160px)" }} />

      {/* Hero */}
      <section style={{ position: "relative", zIndex: 1, textAlign: "center", padding: "80px 24px 48px" }}>
        <h1 className="display" style={{ fontSize: "clamp(36px, 6vw, 52px)", lineHeight: 1.15, marginBottom: 16 }}>
          Atos de Fala
        </h1>
        <p style={{ fontSize: 17, color: "var(--muted)", maxWidth: 480, margin: "0 auto", lineHeight: 1.65 }}>
          Pesquisa anônima sobre como diferentes perfis interpretam intenções comunicativas em português.
          Suas respostas ajudam a tornar a IA mais precisa — e entram num dataset aberto.
        </p>
      </section>

      {/* Form card */}
      <section style={{ position: "relative", zIndex: 1, width: "100%", maxWidth: 520, padding: "0 24px 80px" }}>
        <OnboardingForm
          f={f}
          setF={setF}
          consent={consent}
          setConsent={setConsent}
          ready={!!ready}
          onStart={start}
        />
      </section>
    </main>
  );
}
