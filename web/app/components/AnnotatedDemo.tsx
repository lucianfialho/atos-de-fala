"use client";

import { getActTint } from "@/lib/actColors";
import { Arrow } from "@/app/components/marks";

// A real PT-BR sentence broken into trechos, each labelled with its act.
// This SHOWS the product: annotating the intention of each trecho.
const TRECHOS: { text: string; act: string; label: string }[] = [
  { text: "Bom dia!", act: "saudar", label: "saudar" },
  { text: "Você pode me revisar o relatório?", act: "pedir", label: "pedir" },
  { text: "Obrigado!", act: "agradecer", label: "agradecer" },
];

export default function AnnotatedDemo() {
  return (
    <figure className="demo-card" aria-label="Exemplo de frase anotada por ato de fala">
      <figcaption className="demo-card-head">
        <span className="demo-card-dot" aria-hidden="true" />
        <span className="demo-card-filename">frase&nbsp;#0427 · anotada</span>
      </figcaption>

      <div className="demo-sentence">
        {TRECHOS.map((t) => {
          const tint = getActTint(t.act);
          return (
            <span key={t.text} className="demo-trecho">
              <span className="demo-tag" style={{ background: tint.bg, color: tint.text, borderColor: tint.border }}>
                {t.label}
              </span>
              <span className="demo-text" style={{ ["--act-line" as string]: tint.text }}>
                {t.text}
              </span>
            </span>
          );
        })}
      </div>

      {/* Hand-drawn arrow + note pointing at the "pedir" trecho */}
      <div className="demo-arrow" aria-hidden="true">
        <Arrow width={64} height={50} />
        <span className="demo-arrow-note">pedido, não pergunta!</span>
      </div>
    </figure>
  );
}
