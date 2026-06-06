"use client";

import BrazilMap from "@/app/components/BrazilMap";
import { Underline } from "@/app/components/marks";

// Dedicated band that frames the Brazil map as the research thesis,
// not hero decoration: "do the regions read intention differently?"
export default function MapBand() {
  return (
    <section className="lp-section map-band">
      <div className="lp-wide">
        <div className="map-band-grid">
          <div className="map-band-copy">
            <p className="label lp-eyebrow">DE ONDE VÊM AS ANOTAÇÕES</p>
            <h2 className="display map-band-title">
              A tese: será que cada região lê a{" "}
              <span className="mark-word">
                intenção
                <Underline className="mark-underline" width={130} height={12} />
              </span>{" "}
              de um jeito diferente?
            </h2>
            <p className="map-band-lead">
              Cada anotação carrega um perfil (anônimo). Conforme o mapa esquenta,
              dá pra ver se um "que tal?" soa como sugestão no Sul e como cobrança no Nordeste.
            </p>
          </div>

          <div className="map-band-map">
            <BrazilMap />
          </div>
        </div>
      </div>
    </section>
  );
}
