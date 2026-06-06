import ForgetLink from "./ForgetLink";

export default function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="lp-footer">
      <div className="lp-wide">
        <div className="lp-footer-grid">
          <div className="lp-footer-brand">
            <span className="lp-footer-wordmark display">atos de fala</span>
            <p className="lp-footer-blurb">
              Dataset aberto de intenção em português — anotado à mão, por gente real.
            </p>
          </div>

          <nav className="lp-footer-col" aria-label="Projeto">
            <p className="label lp-footer-col-head">PROJETO</p>
            <a href="/termo">Termo de uso</a>
            <a href="#como-funciona">Como funciona</a>
            <a href="#participar">Participar</a>
            <a href="/painel">Painel ao vivo</a>
            <ForgetLink />
          </nav>

          <nav className="lp-footer-col" aria-label="Recursos">
            <p className="label lp-footer-col-head">RECURSOS</p>
            <a href="https://huggingface.co/lucianfialho/atos-de-fala-ptbr" target="_blank" rel="noopener noreferrer">
              Modelo (Hugging Face)
            </a>
            <a href="https://huggingface.co/spaces/lucianfialho/atos-de-fala-ptbr" target="_blank" rel="noopener noreferrer">
              Demo (Space)
            </a>
            <a href="https://github.com/lucianfialho/atos-de-fala" target="_blank" rel="noopener noreferrer">
              Código (GitHub)
            </a>
          </nav>
        </div>

        <div className="lp-footer-base">
          <span>© {year} Atos de Fala</span>
          <span className="lp-footer-base-sep">·</span>
          <span>Dataset aberto CC BY</span>
        </div>
      </div>
    </footer>
  );
}
