import { Underline, CircleScribble } from "@/app/components/marks";

const HF_SPACE = "https://huggingface.co/spaces/lucianfialho/atos-de-fala-ptbr";

export function OpenStrip() {
  return (
    <div className="lp-open-strip">
      <div className="lp-wide lp-open-strip-inner">
        <span className="lp-open-item">código aberto</span>
        <span className="lp-open-sep" aria-hidden="true">·</span>
        <span className="lp-open-item">dataset aberto</span>
        <span className="lp-open-sep" aria-hidden="true">·</span>
        <span className="lp-open-item">
          <a href={HF_SPACE} target="_blank" rel="noopener noreferrer" className="lp-open-link">
            modelo aberto
          </a>
        </span>
      </div>
    </div>
  );
}

export function OQueE() {
  return (
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
        <p style={{ fontSize: 17, lineHeight: 1.75, color: "var(--body)", marginTop: 20 }}>
          Construímos um modelo que lê a intenção de cada trecho — o primeiro aberto pra
          português, até onde sabemos. Cada correção sua treina a próxima versão.{" "}
          <a href={HF_SPACE} target="_blank" rel="noopener noreferrer" className="lp-model-link">
            Testar o modelo →
          </a>
        </p>
      </div>
    </section>
  );
}

export function ATeseCard() {
  return (
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
  );
}
