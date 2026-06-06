"use client";

import { getActTint } from "@/lib/actColors";

interface BarListProps {
  title: string;
  entries: [string, number][];
  colorFn?: (key: string) => string;
}

export function BarList({ title, entries, colorFn }: BarListProps) {
  const max = Math.max(...entries.map(([, n]) => n), 1);
  return (
    <div className="painel-barlist">
      <p className="label painel-barlist-title">{title}</p>
      {entries.map(([key, n]) => {
        const pct = Math.round((n / max) * 100);
        const bg = colorFn ? colorFn(key) : "var(--primary)";
        return (
          <div key={key} className="painel-bar-row">
            <span className="painel-bar-label">{key}</span>
            <div className="painel-bar-track">
              <div
                className="painel-bar-fill"
                style={{ width: `${pct}%`, background: bg }}
              />
            </div>
            <span className="painel-bar-count">{n.toLocaleString("pt-BR")}</span>
          </div>
        );
      })}
    </div>
  );
}

interface ActBarsProps {
  byAct: Record<string, number>;
}

export function ActBars({ byAct }: ActBarsProps) {
  const sorted = Object.entries(byAct).sort(([, a], [, b]) => b - a);
  return (
    <BarList
      title="O que a IA mais erra/acerta? (avaliações por ato)"
      entries={sorted}
      colorFn={(act) => getActTint(act).bg}
    />
  );
}

export function SuggestionBars({ suggByAct }: { suggByAct: Record<string, number> }) {
  const sorted = Object.entries(suggByAct).sort(([, a], [, b]) => b - a);
  if (sorted.length === 0) return null;
  return (
    <BarList
      title="Variações sugeridas por ato"
      entries={sorted}
      colorFn={(act) => getActTint(act).bg}
    />
  );
}

interface ProfileBarsProps {
  byRegion: Record<string, number>;
  byAge: Record<string, number>;
}

export function ProfileBars({ byRegion, byAge }: ProfileBarsProps) {
  const regionEntries = Object.entries(byRegion).sort(([, a], [, b]) => b - a);
  const ageEntries = Object.entries(byAge).sort(([, a], [, b]) => b - a);
  return (
    <div className="painel-profile-grid">
      <BarList title="Por região" entries={regionEntries} />
      <BarList title="Por faixa etária" entries={ageEntries} />
    </div>
  );
}
