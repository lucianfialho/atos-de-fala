"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { getOrCreateParticipantId } from "@/lib/participant";
import OnboardingForm from "@/app/components/OnboardingForm";

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
    <main style={{ minHeight: "100vh", overflowX: "hidden" }}>

      {/* ── 1. Hero ──────────────────────────────────────────────────── */}
      <section className="lp-hero" style={{ position: "relative", overflow: "hidden" }}>
        {/* Atmospheric orbs */}
        <div className="orb orb-mint"    style={{ width: 560, height: 560, top: -160, left: "calc(50% - 460px)" }} />
        <div className="orb orb-peach"   style={{ width: 440, height: 440, top: -100, right: "calc(50% - 440px)" }} />
        <div className="orb orb-lavender" style={{ width: 320, height: 320, top: 240, left: "calc(50% + 180px)" }} />

        <div className="lp-center" style={{ position: "relative", zIndex: 1 }}>
          <p className="label" style={{ marginBottom: 20 }}>DATASET ABERTO · PORTUGUÊS BRASILEIRO</p>

          <h1
            className="display"
            style={{
              fontSize: "clamp(40px, 7vw, 68px)",
              lineHeight: 1.1,
              letterSpacing: "-1px",
              maxWidth: 820,
              margin: "0 auto 24px",
            }}
          >
            Ensine a IA a entender a intenção por trás do que a gente diz.
          </h1>

          <p
            style={{
              fontSize: 18,
              color: "var(--muted)",
              maxWidth: 560,
              margin: "0 auto 40px",
              lineHeight: 1.7,
            }}
          >
            Quando você diz "você pode me passar o sal?", não é uma pergunta — é um pedido.
            As máquinas erram isso o tempo todo em português. Ajude a corrigir, jogando.
          </p>

          <div style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap" }}>
            <a className="btn-ink" href="#participar" style={{ height: 48, padding: "0 28px", fontSize: 16 }}>
              Participar
            </a>
            <a className="btn-outline" href="#como-funciona" style={{ height: 48, padding: "0 28px", fontSize: 16 }}>
              Como funciona
            </a>
          </div>
        </div>
      </section>

      {/* ── 2. O que é ───────────────────────────────────────────────── */}
      <section id="sobre" className="lp-section">
        <div className="lp-center lp-prose">
          <p className="label lp-eyebrow">O QUE É</p>
          <h2 className="display" style={{ fontSize: "clamp(26px, 4vw, 36px)", marginBottom: 20 }}>
            Atos de fala
          </h2>
          <p style={{ fontSize: 17, lineHeight: 1.75, color: "var(--body)" }}>
            Todo trecho que falamos realiza uma ação: pedir, agradecer, discordar, prometer,
            se despedir… São os atos de fala. Um modelo de IA tentou adivinhar o ato de cada
            trecho de milhares de frases — e precisa de gente real pra dizer se ele acertou.
          </p>
        </div>
      </section>

      {/* ── 3. A tese — highlighted card ─────────────────────────────── */}
      <section className="lp-section lp-section-tinted">
        <div className="lp-center lp-prose">
          <div className="card" style={{ padding: "36px 40px", textAlign: "left" }}>
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

      {/* ── 4. Como funciona ─────────────────────────────────────────── */}
      <section id="como-funciona" className="lp-section">
        <div className="lp-center">
          <p className="label lp-eyebrow" style={{ textAlign: "center" }}>COMO FUNCIONA</p>
          <h2
            className="display"
            style={{ fontSize: "clamp(24px, 3.5vw, 32px)", textAlign: "center", marginBottom: 48 }}
          >
            Três passos, sem cadastro
          </h2>

          <div className="lp-steps">
            {[
              {
                num: "01",
                title: "Avalie",
                body: 'A IA mostra o ato que ela achou pra cada trecho de uma frase. Você confirma com ✓, corrige com ✗, ou marca “não sei”.',
              },
              {
                num: "02",
                title: "Enriqueça",
                body: "Pode sugerir outras formas de dizer a mesma coisa, com a mesma intenção. Vale pontos de bônus.",
              },
              {
                num: "03",
                title: "Contribua",
                body: "Tudo vira um dataset aberto (CC BY) pra treinar modelos de português melhores — e a sua percepção entra na pesquisa.",
              },
            ].map((step) => (
              <div key={step.num} className="card lp-step-card">
                <span
                  className="display"
                  style={{ fontSize: 13, letterSpacing: "0.06em", color: "var(--muted)", display: "block", marginBottom: 14 }}
                >
                  {step.num}
                </span>
                <h3 className="display" style={{ fontSize: 22, marginBottom: 12 }}>
                  {step.title}
                </h3>
                <p style={{ fontSize: 15, lineHeight: 1.7, color: "var(--body)" }}>
                  {step.body}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── 5. Participar ────────────────────────────────────────────── */}
      <section id="participar" className="lp-section lp-section-tinted">
        <div className="lp-center" style={{ maxWidth: 560 }}>
          <p className="label lp-eyebrow" style={{ textAlign: "center" }}>PARTICIPAR</p>
          <p
            style={{
              fontSize: 16,
              color: "var(--muted)",
              textAlign: "center",
              marginBottom: 32,
              lineHeight: 1.6,
            }}
          >
            Anônimo, sem cadastro. Conte um pouco sobre você e comece a jogar.
          </p>

          <OnboardingForm
            f={f}
            setF={setF}
            consent={consent}
            setConsent={setConsent}
            ready={!!ready}
            onStart={start}
          />
        </div>
      </section>

      {/* ── 6. Footer ────────────────────────────────────────────────── */}
      <footer className="lp-footer">
        <div className="lp-center">
          <p style={{ fontSize: 13, color: "var(--muted)", lineHeight: 1.6 }}>
            <a href="#">Dataset aberto CC BY</a>
            {" · "}
            <a href="https://huggingface.co/spaces/lucianfialho/atos-de-fala-ptbr" target="_blank" rel="noopener noreferrer">
              Modelo no Hugging Face
            </a>
            {" · "}
            <a href="https://github.com/lucianfialho/atos-de-fala" target="_blank" rel="noopener noreferrer">
              Código no GitHub
            </a>
          </p>
        </div>
      </footer>

    </main>
  );
}
