"use client";

export default function Nav() {
  return (
    <header className="lp-nav">
      <div className="lp-nav-inner">
        <a href="/" className="lp-nav-wordmark display">
          atos de fala
        </a>
        <div className="lp-nav-actions">
          <a href="/painel" className="lp-nav-painel">
            Painel
          </a>
          <a href="#participar" className="btn-ink lp-nav-cta" style={{ borderRadius: 9999 }}>
            Participar
          </a>
        </div>
      </div>
    </header>
  );
}
