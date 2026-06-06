"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { getOrCreateParticipantId } from "@/lib/participant";
import OnboardingForm from "@/app/components/OnboardingForm";
import Nav from "@/app/components/Nav";
import GoalBar from "@/app/components/GoalBar";
import HowItWorks from "@/app/components/HowItWorks";
import AnnotatedDemo from "@/app/components/AnnotatedDemo";
import MapBand from "@/app/components/MapBand";
import Footer from "@/app/components/Footer";
import { Underline, CircleScribble } from "@/app/components/marks";

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
                <AnnotatedDemo />
              </div>
            </div>
          </div>
        </section>

        {/* ── 2. O que é ─────────────────────────────────────────────── */}
        <section id="sobre" className="lp-section">
          <div className="lp-center lp-prose">
            <p className="label lp-eyebrow">O QUE É</p>
            <h2 className="display" style={{ fontSize: "clamp(26px, 4vw, 36px)", marginBottom: 20 }}>
              <span className="mark-word">
                Atos de fala
                <Underline className="mark-underline" width={170} height={12} />
              </span>
            </h2>
            <p style={{ fontSize: 17, lineHeight: 1.75, color: "var(--body)" }}>
              Todo trecho que falamos realiza uma ação: pedir, agradecer, discordar, prometer,
              se despedir… São os atos de fala. Um modelo de IA tentou adivinhar o ato de cada
              trecho de milhares de frases — e precisa de gente real pra dizer se ele acertou.
            </p>
          </div>
        </section>

        {/* ── 3. A tese — highlighted card ───────────────────────────── */}
        <section className="lp-section lp-section-tinted">
          <div className="lp-center lp-prose">
            <div className="card tese-card" style={{ padding: "36px 40px", textAlign: "left" }}>
              <span className="tese-scribble" aria-hidden="true">
                <CircleScribble width={104} height={64} />
              </span>
              <p className="label lp-eyebrow">A PERGUNTA DE PESQUISA</p>
              <h2 className="display" style={{ fontSize: "clamp(22px, 3.5vw, 30px)", marginBottom: 20 }}>
                Será que todo mundo lê a mesma intenção?
              </h2>
              <p style={{ fontSize: 17, lineHeight: 1.75, color: "var(--body)" }}>
                Ninguém respondeu isso pro português: pessoas de perfis diferentes percebem
                intenções diferentes na mesma frase? Um nordestino e um paulista, alguém de
                20 e alguém de 50 — leem o mesmo "que tal?" como sugestão ou como cobrança?
                Por isso a gente pergunta seu perfil (anônimo) — é o que torna esse dataset único.
              </p>
            </div>
          </div>
        </section>

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
