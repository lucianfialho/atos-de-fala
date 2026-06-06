"use client";

import { useEffect, useState } from "react";

const GOAL = 4000; // Fase 1: ~200 frases × ~20 avaliações

interface StatsData {
  votes: number;
}

export default function GoalBar() {
  const [votes, setVotes] = useState<number | null>(null);

  useEffect(() => {
    fetch("/api/stats")
      .then((r) => r.json())
      .then((d: StatsData) => setVotes(d.votes ?? 0))
      .catch(() => setVotes(0));
  }, []);

  const loading = votes === null;
  const pct = loading ? 0 : Math.min(100, Math.round((votes / GOAL) * 100));

  return (
    <div className="goalbar" role="status" aria-label="Progresso da meta da Fase 1">
      <div className="goalbar-inner">
        <span className="label goalbar-label">META DA FASE 1</span>

        <div className="goalbar-track-wrap" aria-hidden="true">
          {loading ? (
            <div className="goalbar-track">
              <div className="goalbar-fill-skeleton" />
            </div>
          ) : (
            <div className="goalbar-track">
              <div
                className="goalbar-fill"
                style={{ width: `${pct}%` }}
              />
            </div>
          )}
        </div>

        <span className="goalbar-numbers">
          {loading ? (
            <span className="goalbar-numbers-skeleton" aria-hidden="true" />
          ) : (
            <>
              {votes!.toLocaleString("pt-BR")}
              {" de "}
              {GOAL.toLocaleString("pt-BR")}
              {" avaliações · "}
              {pct}%
            </>
          )}
        </span>
      </div>
    </div>
  );
}
