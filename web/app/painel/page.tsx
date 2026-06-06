"use client";

import { useEffect, useState } from "react";
import BrazilMap from "@/app/components/BrazilMap";
import { ActBars, ProfileBars, SuggestionBars } from "./StatBars";

const GOAL = 4000;

interface StatsData {
  participants: number;
  votes: number;
  states: number;
  suggestions: number;
  itemsTouched: number;
  itemsTotal: number;
  agree: number;
  disagree: number;
  byAct: Record<string, number>;
  byAge: Record<string, number>;
  byRegion: Record<string, number>;
  suggByAct: Record<string, number>;
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="card painel-stat-card">
      <p className="painel-stat-value display">{typeof value === "number" ? value.toLocaleString("pt-BR") : value}</p>
      <p className="label painel-stat-label">{label}</p>
    </div>
  );
}

export default function PainelPage() {
  const [data, setData] = useState<StatsData | null>(null);

  useEffect(() => {
    const load = () =>
      fetch("/api/stats")
        .then((r) => r.json())
        .then(setData)
        .catch(() => {});

    load();
    const id = setInterval(load, 15_000);
    return () => clearInterval(id);
  }, []);

  const votes = data?.votes ?? 0;
  const pct = Math.min(100, Math.round((votes / GOAL) * 100));

  return (
    <main className="painel-page">
      <div className="painel-inner">
        {/* Header */}
        <div className="painel-header">
          <a href="/" className="painel-back">← voltar</a>
          <span className="label lp-eyebrow">PAINEL · AO VIVO</span>
          <h1 className="display painel-title">Quanto a galera já ensinou</h1>
          <p className="painel-live-badge">
            <span className="painel-live-dot" aria-hidden="true">●</span>
            ao vivo · atualiza sozinho
          </p>
        </div>

        {/* Stat cards */}
        <div className="painel-stats-grid">
          <StatCard label="Participantes" value={data?.participants ?? "—"} />
          <StatCard label="Avaliações" value={data?.votes ?? "—"} />
          <StatCard label="Sugestões" value={data?.suggestions ?? "—"} />
          <StatCard label="Estados" value={data?.states ?? "—"} />
          <div className="card painel-stat-card painel-stat-card--wide">
            <p className="painel-stat-value display">
              {data ? `${data.itemsTouched}/${data.itemsTotal}` : "—"}
            </p>
            <p className="label painel-stat-label">Frases cobertas</p>
          </div>
        </div>

        {/* Meta da Fase 1 */}
        <div className="card painel-section">
          <p className="label painel-section-eyebrow">META DA FASE 1</p>
          <div className="painel-goalbar-track">
            <div className="painel-goalbar-fill" style={{ width: `${pct}%` }} />
          </div>
          <p className="painel-goalbar-numbers">
            {votes.toLocaleString("pt-BR")} de {GOAL.toLocaleString("pt-BR")} avaliações · {pct}%
          </p>
        </div>

        {/* Map */}
        <div className="card painel-section">
          <p className="label painel-section-eyebrow">De onde vêm as anotações</p>
          <div className="painel-map-wrap">
            <BrazilMap />
          </div>
        </div>

        {/* Por ato */}
        {data && Object.keys(data.byAct).length > 0 && (
          <div className="card painel-section">
            <ActBars byAct={data.byAct} />
          </div>
        )}

        {/* Sugestões por ato */}
        {data && data.suggByAct && Object.keys(data.suggByAct).length > 0 && (
          <div className="card painel-section">
            <SuggestionBars suggByAct={data.suggByAct} />
          </div>
        )}

        {/* Por perfil */}
        {data && (
          <div className="card painel-section">
            <p className="label painel-section-eyebrow">Quem está anotando</p>
            <ProfileBars byRegion={data.byRegion} byAge={data.byAge} />
          </div>
        )}

        {/* Concordância */}
        <div className="card painel-section painel-concordancia">
          <p className="label painel-section-eyebrow">Concordância vs Discordância</p>
          <div className="painel-agree-row">
            <div className="painel-agree-item">
              <span className="painel-agree-num display">{(data?.agree ?? 0).toLocaleString("pt-BR")}</span>
              <span className="painel-agree-lbl">concordam com a IA</span>
            </div>
            <div className="painel-agree-sep" aria-hidden="true">vs</div>
            <div className="painel-agree-item">
              <span className="painel-agree-num display">{(data?.disagree ?? 0).toLocaleString("pt-BR")}</span>
              <span className="painel-agree-lbl">discordam da IA</span>
            </div>
          </div>
          <p className="painel-concordancia-note">
            a discordância é o sinal de pesquisa — quanto mais gente diversa, mais ela aparece.
          </p>
        </div>

        {/* CTA */}
        <div className="painel-cta-wrap">
          <a href="/#participar" className="btn-ink painel-cta-btn">Participar</a>
        </div>
      </div>
    </main>
  );
}
