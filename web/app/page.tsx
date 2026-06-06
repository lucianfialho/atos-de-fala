"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { getOrCreateParticipantId } from "@/lib/participant";
import OnboardingForm from "@/app/components/OnboardingForm";
import Nav from "@/app/components/Nav";
import GoalBar from "@/app/components/GoalBar";
import HowItWorks from "@/app/components/HowItWorks";
import LiveDemo from "@/app/components/LiveDemo";
import MapBand from "@/app/components/MapBand";
import Footer from "@/app/components/Footer";
import { OpenStrip, OQueE, ATeseCard } from "@/app/components/LandingSections";

export default function LandingPage() {
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
    <>
      <Nav />
      <GoalBar />
      <main style={{ minHeight: "100vh", overflowX: "hidden" }}>

        {/* ── 1. Hero — product demo, asymmetric grid ────────────────── */}
        <section className="lp-hero lp-hero-asymmetric">
          <div className="lp-wide">
            <div className="lp-hero-grid">
              <div className="lp-hero-copy">
                <p className="label" style={{ marginBottom: 18 }}>DATASET ABERTO · PORTUGUÊS BRASILEIRO</p>
                <h1 className="display lp-hero-h1">
                  Ensine a IA a entender a{" "}
                  <mark className="hero-mark">intenção</mark>
                  {" "}por trás do que a gente diz.
                </h1>
                <p className="lp-hero-sub">
                  Quando você diz "você pode me passar o sal?", não é uma pergunta — é um pedido.
                  As máquinas erram isso o tempo todo em português. Ajude a corrigir, jogando.
                </p>
                <div className="lp-hero-actions">
                  <a className="btn-ink" href="#participar" style={{ height: 48, padding: "0 28px", fontSize: 16 }}>
                    Participar
                  </a>
                  <a className="btn-outline" href="#como-funciona" style={{ height: 48, padding: "0 28px", fontSize: 16 }}>
                    Como funciona
                  </a>
                </div>
              </div>
              <div className="lp-hero-demo">
                <LiveDemo />
              </div>
            </div>
          </div>
        </section>

        {/* ── 1b. Open-model strip ───────────────────────────────────── */}
        <OpenStrip />

        {/* ── 2. O que é ─────────────────────────────────────────────── */}
        <OQueE />

        {/* ── 3. A tese — highlighted card ───────────────────────────── */}
        <ATeseCard />

        {/* ── 4. Como funciona — editorial numbered list ─────────────── */}
        <HowItWorks />

        {/* ── 4b. Mapa — a tese de pesquisa ──────────────────────────── */}
        <MapBand />

        {/* ── 5. Participar ──────────────────────────────────────────── */}
        <section id="participar" className="lp-section lp-section-tinted">
          <div className="lp-center" style={{ maxWidth: 560 }}>
            <p className="label lp-eyebrow" style={{ textAlign: "center" }}>PARTICIPAR</p>
            <p style={{ fontSize: 16, color: "var(--muted)", textAlign: "center", marginBottom: 32, lineHeight: 1.6 }}>
              Anônimo, sem cadastro. Conte um pouco sobre você e comece a jogar.
            </p>
            <OnboardingForm f={f} setF={setF} consent={consent} setConsent={setConsent} ready={!!ready} onStart={start} />
          </div>
        </section>

        {/* ── 6. Footer ──────────────────────────────────────────────── */}
        <Footer />

      </main>
    </>
  );
}
