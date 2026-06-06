export const STEPS = [
  {
    num: "01",
    title: "Avalie",
    body: 'A IA mostra o ato que ela achou pra cada trecho de uma frase. Você confirma com ✓, corrige com ✗, ou marca "não sei".',
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
];

export default function HowItWorks() {
  return (
    <section id="como-funciona" className="lp-section">
      <div className="lp-wide">
        <p className="label lp-eyebrow" style={{ textAlign: "center", marginBottom: 8 }}>COMO FUNCIONA</p>
        <h2
          className="display"
          style={{ fontSize: "clamp(24px, 3.5vw, 32px)", textAlign: "center", marginBottom: 56 }}
        >
          Três passos, sem cadastro
        </h2>

        <div className="lp-steps-editorial">
          {STEPS.map((step, i) => (
            <div key={step.num} className="lp-step-row">
              <span className="lp-step-numeral display">{step.num}</span>
              <div className="lp-step-content">
                <h3 className="display lp-step-title">{step.title}</h3>
                <p className="lp-step-body">{step.body}</p>
              </div>
              {i < STEPS.length - 1 && <hr className="lp-step-rule" />}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
