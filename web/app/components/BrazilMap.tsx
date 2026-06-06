"use client";

import { useEffect, useState } from "react";

/* @svg-maps/brazil types are declared against an optional peer (svg-maps__common)
   that isn't installed — use a local shape to keep TS happy. */
interface MapLocation {
  id: string;
  name: string;
  path: string;
}

interface SvgMap {
  label: string;
  viewBox: string;
  locations: MapLocation[];
}

// eslint-disable-next-line @typescript-eslint/no-require-imports
const Brazil = (require("@svg-maps/brazil") as { default: SvgMap }).default;

interface StatsData {
  participants: number;
  votes: number;
  states: number;
  byRegion: Record<string, number>;
}

function MapSkeleton() {
  return (
    <div className="brazil-map-skeleton" aria-label="Carregando mapa…">
      <div className="brazil-map-skeleton-fill" />
    </div>
  );
}

export default function BrazilMap() {
  const [stats, setStats] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/stats")
      .then((r) => r.json())
      .then((d) => {
        setStats(d);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="brazil-map-wrap">
        <MapSkeleton />
        <div className="brazil-map-counter-skeleton" />
      </div>
    );
  }

  const byRegion = stats?.byRegion ?? {};
  const counts = Object.values(byRegion);
  const maxCount = counts.length > 0 ? Math.max(...counts, 1) : 1;

  function alphaForUF(uf: string): number {
    const count = byRegion[uf] ?? 0;
    if (count === 0) return 0.05;
    return 0.18 + 0.62 * (count / maxCount);
  }

  return (
    <div className="brazil-map-wrap">
      <svg
        viewBox={Brazil.viewBox}
        className="brazil-map-svg"
        aria-label="Mapa do Brasil com contribuições por estado"
        role="img"
      >
        {Brazil.locations.map((loc) => {
          const uf = loc.id.toUpperCase();
          const alpha = alphaForUF(uf);
          return (
            <path
              key={loc.id}
              d={loc.path}
              fill={`rgba(35,37,29,${alpha})`}
              stroke="#bfc1b7"
              strokeWidth={0.5}
              strokeLinejoin="round"
            >
              <title>{loc.name}</title>
            </path>
          );
        })}
      </svg>

      <div className="brazil-map-meta">
        <div className="brazil-map-legend">
          <span className="brazil-map-legend-swatch brazil-map-legend-low" />
          <span className="brazil-map-legend-label">menos contribuições</span>
          <span className="brazil-map-legend-arrow">⟶</span>
          <span className="brazil-map-legend-swatch brazil-map-legend-high" />
          <span className="brazil-map-legend-label">mais</span>
        </div>
        <p className="brazil-map-counter">
          {(stats?.votes ?? 0).toLocaleString("pt-BR")}{" "}
          <span className="brazil-map-counter-unit">avaliações</span>
          {" · "}
          {(stats?.participants ?? 0).toLocaleString("pt-BR")}{" "}
          <span className="brazil-map-counter-unit">pessoas</span>
          {" · "}
          {(stats?.states ?? 0)}{" "}
          <span className="brazil-map-counter-unit">estados</span>
        </p>
      </div>
    </div>
  );
}
