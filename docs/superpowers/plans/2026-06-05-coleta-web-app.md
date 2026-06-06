# Coleta Colaborativa — Plano 2: Web App (Next.js / Vercel / Neon)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir o jogo público anônimo onde a galera avalia (✓/✗) os atos que a IA atribuiu a frases PT-BR e sugere paráfrases (bônus), gravando votos + perfil demográfico no Postgres que o Plano 1 consome.

**Architecture:** Next.js (App Router) na Vercel + Postgres (Neon, driver `@neondatabase/serverless`). O coração — pontuação (espelho exato do `score.py`) e seleção do próximo item (honeypot a cada ~7, dedup por participante) — fica em funções **puras** em `web/lib/`, testadas com Vitest sem banco. As rotas de API e páginas são finas e usam essas libs. Aplica o MESMO `db/schema.sql` do Plano 1 como migration.

**Tech Stack:** Next.js 14 (App Router, TypeScript), React, Vitest, `@neondatabase/serverless`, Vercel, Neon Postgres.

**Pré-requisito:** Plano 1 Task 1 (o `db/schema.sql`) precisa existir — este plano aplica esse arquivo como migration e depende das tabelas.

---

## File Structure

App separado em `web/` (monorepo-lite; o pacote Python continua em `src/atos`):

- `web/package.json`, `web/tsconfig.json`, `web/next.config.mjs`, `web/vitest.config.ts` — scaffold.
- `web/lib/scoring.ts` — **espelho do `score.py`**: `streakMultiplier`, `pointsForVote`, `updateReliability`, `applyItemOutcome`, constantes.
- `web/lib/serving.ts` — puro: `pickNextItem()` (honeypot a cada ~7, menos votos, dedup).
- `web/lib/taxonomy.ts` — os 13 atos (espelho do `config/taxonomy.yaml`) pro dropdown de correção.
- `web/lib/db.ts` — cliente Neon (`sql` tagged template) + `applySchema()`.
- `web/lib/participant.ts` — uuid anônimo no `localStorage` (client).
- `web/app/layout.tsx`, `web/app/page.tsx` (onboarding), `web/app/jogar/page.tsx` (jogo).
- `web/app/api/next-item/route.ts`, `vote/route.ts`, `suggestion/route.ts`, `me/route.ts`.
- `web/lib/*.test.ts` — Vitest (puro, sem banco).

Rode os testes com `cd web && npm test`. As rotas/páginas (I/O + UI) são verificadas por integração (curl) e um smoke manual — não por unit test.

---

### Task 1: Scaffold do app Next.js + Vitest

**Files:**
- Create: `web/` (via create-next-app), `web/vitest.config.ts`
- Modify: `web/package.json` (script de teste + deps)

- [ ] **Step 1: Scaffold**

Run:
```bash
npx create-next-app@latest web --ts --app --no-tailwind --no-src-dir --no-eslint --use-npm --import-alias "@/*"
cd web && npm i @neondatabase/serverless && npm i -D vitest
```
Expected: cria `web/` com Next 14 + TS; instala o driver Neon e o Vitest.

- [ ] **Step 2: Write the Vitest config**

```typescript
// web/vitest.config.ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: { environment: "node", include: ["lib/**/*.test.ts"] },
});
```

- [ ] **Step 3: Add the test script**

In `web/package.json`, inside `"scripts"`, add:
```json
    "test": "vitest run"
```

- [ ] **Step 4: Write a smoke test to prove the toolchain runs**

```typescript
// web/lib/smoke.test.ts
import { describe, it, expect } from "vitest";

describe("toolchain", () => {
  it("runs vitest", () => {
    expect(1 + 1).toBe(2);
  });
});
```

- [ ] **Step 5: Run it**

Run: `cd web && npm test`
Expected: 1 passed.

- [ ] **Step 6: Commit**

```bash
git add web/package.json web/package-lock.json web/vitest.config.ts web/lib/smoke.test.ts web/tsconfig.json web/next.config.mjs web/app
git commit -m "chore(web): scaffold Next.js app + vitest"
```

---

### Task 2: Pontuação (espelho do `score.py`)

**Files:**
- Create: `web/lib/scoring.ts`, `web/lib/scoring.test.ts`

- [ ] **Step 1: Write the failing test**

```typescript
// web/lib/scoring.test.ts
import { describe, it, expect } from "vitest";
import {
  streakMultiplier, pointsForVote, updateReliability, applyItemOutcome,
  POINTS_SUGGESTION, POINTS_SUGGESTION_CONFIRMED,
} from "./scoring";

describe("scoring mirrors score.py", () => {
  it("streak tiers", () => {
    expect(streakMultiplier(0)).toBe(1.0);
    expect(streakMultiplier(4)).toBe(1.0);
    expect(streakMultiplier(5)).toBe(1.5);
    expect(streakMultiplier(9)).toBe(1.5);
    expect(streakMultiplier(10)).toBe(2.0);
  });
  it("points per vote", () => {
    expect(pointsForVote(0)).toBe(10);
    expect(pointsForVote(5)).toBe(15);
    expect(pointsForVote(10)).toBe(20);
  });
  it("suggestion constants", () => {
    expect(POINTS_SUGGESTION).toBe(20);
    expect(POINTS_SUGGESTION_CONFIRMED).toBe(50);
  });
  it("reliability rises/falls and clamps", () => {
    expect(updateReliability(0.5, true)).toBeCloseTo(0.55, 10);
    expect(updateReliability(0.5, false)).toBeCloseTo(0.4, 10);
    expect(updateReliability(1.0, true)).toBe(1.0);
    expect(updateReliability(0.0, false)).toBe(0.0);
  });
});

describe("applyItemOutcome", () => {
  const base = { points: 0, streak: 0, reliability: 0.5, itemsDone: 0 };
  it("normal item: +points*nSpans, streak+1, reliability unchanged", () => {
    const r = applyItemOutcome(base, 2, null);
    expect(r).toEqual({ points: 20, streak: 1, reliability: 0.5, itemsDone: 1 });
  });
  it("honeypot correct raises reliability", () => {
    const r = applyItemOutcome(base, 1, true);
    expect(r.reliability).toBeCloseTo(0.55, 10);
    expect(r.streak).toBe(1);
  });
  it("honeypot wrong lowers reliability", () => {
    const r = applyItemOutcome(base, 1, false);
    expect(r.reliability).toBeCloseTo(0.4, 10);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && npm test`
Expected: FAIL — cannot find module `./scoring`.

- [ ] **Step 3: Write the implementation**

```typescript
// web/lib/scoring.ts
// Mirror of src/atos/collect/score.py — keep values identical so client display and
// server-side stats agree with the Python aggregation. Suggestions never penalize.

export const POINTS_VOTE_BASE = 10;
export const POINTS_SUGGESTION = 20;            // provisional, on submit
export const POINTS_SUGGESTION_CONFIRMED = 50;  // retroactive, when adjudicator confirms

export type Stats = { points: number; streak: number; reliability: number; itemsDone: number };

export function streakMultiplier(streak: number): number {
  if (streak < 5) return 1.0;
  if (streak < 10) return 1.5;
  return 2.0;
}

export function pointsForVote(streak: number, base = POINTS_VOTE_BASE): number {
  return Math.round(base * streakMultiplier(streak));
}

export function updateReliability(reliability: number, honeypotCorrect: boolean): number {
  const r = honeypotCorrect ? reliability + 0.1 * (1.0 - reliability) : reliability * 0.8;
  return Math.max(0.0, Math.min(1.0, r));
}

// One item judged: award points for each evaluated span at the current streak, bump streak,
// update reliability only when the item was a honeypot (honeypotCorrect is null otherwise).
export function applyItemOutcome(stats: Stats, nSpans: number, honeypotCorrect: boolean | null): Stats {
  return {
    points: stats.points + pointsForVote(stats.streak) * nSpans,
    streak: stats.streak + 1,
    reliability: honeypotCorrect === null ? stats.reliability : updateReliability(stats.reliability, honeypotCorrect),
    itemsDone: stats.itemsDone + 1,
  };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd web && npm test`
Expected: all passing.

- [ ] **Step 5: Commit**

```bash
git add web/lib/scoring.ts web/lib/scoring.test.ts
git commit -m "feat(web): scoring lib mirroring score.py"
```

---

### Task 3: Seleção do próximo item (`serving.pickNextItem`)

**Files:**
- Create: `web/lib/serving.ts`, `web/lib/serving.test.ts`

- [ ] **Step 1: Write the failing test**

```typescript
// web/lib/serving.test.ts
import { describe, it, expect } from "vitest";
import { pickNextItem, Candidate } from "./serving";

const c = (id: number, isHoneypot: boolean, voteCount: number): Candidate => ({ id, isHoneypot, voteCount });

describe("pickNextItem", () => {
  it("returns null when no candidates", () => {
    expect(pickNextItem([], 0)).toBeNull();
  });
  it("normal turn serves the non-honeypot with fewest votes", () => {
    const got = pickNextItem([c(1, false, 5), c(2, false, 1), c(3, true, 0)], 0);
    expect(got!.id).toBe(2);
  });
  it("every 7th served item is a honeypot (fewest votes)", () => {
    // itemsDone=6 -> this is the 7th -> honeypot due
    const got = pickNextItem([c(1, false, 0), c(3, true, 9), c(4, true, 2)], 6);
    expect(got!.id).toBe(4);
  });
  it("falls back to normal when a honeypot is due but none left", () => {
    const got = pickNextItem([c(1, false, 3), c(2, false, 0)], 6);
    expect(got!.id).toBe(2);
  });
  it("falls back to honeypot when only honeypots remain on a normal turn", () => {
    const got = pickNextItem([c(5, true, 1)], 0);
    expect(got!.id).toBe(5);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && npm test`
Expected: FAIL — cannot find module `./serving`.

- [ ] **Step 3: Write the implementation**

```typescript
// web/lib/serving.ts
// Pure next-item picker. The route supplies candidates = items the participant has NOT yet
// voted on (dedup done in SQL). Phase 1 = depth: spread overlap by serving the fewest-voted
// item. A honeypot is due on every 7th item; if the due category is empty, fall back.

export type Candidate = { id: number; isHoneypot: boolean; voteCount: number };

const fewestVotes = (xs: Candidate[]): Candidate | null =>
  xs.length === 0 ? null : xs.reduce((a, b) => (b.voteCount < a.voteCount ? b : a));

export function pickNextItem(candidates: Candidate[], itemsDone: number): Candidate | null {
  if (candidates.length === 0) return null;
  const honeypotDue = (itemsDone + 1) % 7 === 0;
  const honeypots = candidates.filter((c) => c.isHoneypot);
  const normals = candidates.filter((c) => !c.isHoneypot);
  const primary = honeypotDue ? honeypots : normals;
  const fallback = honeypotDue ? normals : honeypots;
  return fewestVotes(primary) ?? fewestVotes(fallback);
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd web && npm test`
Expected: all passing.

- [ ] **Step 5: Commit**

```bash
git add web/lib/serving.ts web/lib/serving.test.ts
git commit -m "feat(web): pure next-item picker (honeypot cadence + fewest votes)"
```

---

### Task 4: Taxonomia (espelho dos 13 atos)

**Files:**
- Create: `web/lib/taxonomy.ts`, `web/lib/taxonomy.test.ts`

- [ ] **Step 1: Write the failing test**

```typescript
// web/lib/taxonomy.test.ts
import { describe, it, expect } from "vitest";
import { ACTS } from "./taxonomy";

describe("taxonomy", () => {
  it("has the 13 frozen acts", () => {
    expect(ACTS.length).toBe(13);
    expect(ACTS).toContain("pedir");
    expect(ACTS).toContain("expressar_emocao");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && npm test`
Expected: FAIL — cannot find module `./taxonomy`.

- [ ] **Step 3: Write the implementation**

```typescript
// web/lib/taxonomy.ts
// Mirror of config/taxonomy.yaml (FROZEN v1, 13 acts). Used by the correction dropdown.
export const ACTS = [
  "informar", "perguntar", "concordar", "discordar", "pedir", "sugerir",
  "oferecer", "prometer", "saudar", "agradecer", "desculpar", "despedir",
  "expressar_emocao",
] as const;

export type Act = (typeof ACTS)[number];
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd web && npm test`
Expected: passing.

- [ ] **Step 5: Commit**

```bash
git add web/lib/taxonomy.ts web/lib/taxonomy.test.ts
git commit -m "feat(web): taxonomy mirror (13 acts) for correction UI"
```

---

### Task 5: Cliente Neon + migration do schema

**Files:**
- Create: `web/lib/db.ts`, `web/scripts/migrate.mjs`
- Modify: `web/package.json` (script `migrate`)

- [ ] **Step 1: Write the DB client**

```typescript
// web/lib/db.ts
// Neon serverless client. `sql` is a tagged-template query fn (parametrized, safe).
// DATABASE_URL is set in Vercel + .env.local.
import { neon } from "@neondatabase/serverless";

export const sql = neon(process.env.DATABASE_URL!);
```

- [ ] **Step 2: Write the migration runner (applies the shared schema)**

```javascript
// web/scripts/migrate.mjs
// Applies the repo-root db/schema.sql to DATABASE_URL. Same contract the Python pipeline reads.
import { readFileSync } from "node:fs";
import { neon } from "@neondatabase/serverless";

const ddl = readFileSync(new URL("../../db/schema.sql", import.meta.url), "utf-8");
const sql = neon(process.env.DATABASE_URL);
await sql.query(ddl);
console.log("schema applied");
```

- [ ] **Step 3: Add the migrate script**

In `web/package.json` `"scripts"`, add:
```json
    "migrate": "node scripts/migrate.mjs"
```

- [ ] **Step 4: Verify against a Neon database**

Run: `cd web && DATABASE_URL="<neon-url>" npm run migrate`
Expected: prints "schema applied"; tables exist in Neon (check the Neon console or `psql`).

- [ ] **Step 5: Commit**

```bash
git add web/lib/db.ts web/scripts/migrate.mjs web/package.json
git commit -m "feat(web): Neon client + schema migration runner"
```

---

### Task 6: Onboarding anônimo (`/`) + helper de participante

**Files:**
- Create: `web/lib/participant.ts`, `web/app/page.tsx`
- Create: `web/app/api/participant/route.ts`

- [ ] **Step 1: Write the participant helper (client uuid in localStorage)**

```typescript
// web/lib/participant.ts
"use client";
// Anonymous identity: a uuid persisted in localStorage. No login.
const KEY = "atos_participant_id";

export function getOrCreateParticipantId(): string {
  let id = localStorage.getItem(KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(KEY, id);
  }
  return id;
}
```

- [ ] **Step 2: Write the participant API route (persists demographics)**

```typescript
// web/app/api/participant/route.ts
import { NextResponse } from "next/server";
import { sql } from "@/lib/db";

export async function POST(req: Request) {
  const { id, ageBand, gender, region, education } = await req.json();
  if (!id || !ageBand || !gender || !region || !education) {
    return NextResponse.json({ error: "missing fields" }, { status: 400 });
  }
  await sql`insert into participant (id, age_band, gender, region, education)
            values (${id}, ${ageBand}, ${gender}, ${region}, ${education})
            on conflict (id) do nothing`;
  await sql`insert into participant_stats (participant_id) values (${id})
            on conflict (participant_id) do nothing`;
  return NextResponse.json({ ok: true });
}
```

- [ ] **Step 3: Write the onboarding page**

```tsx
// web/app/page.tsx
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { getOrCreateParticipantId } from "@/lib/participant";

const REGIONS = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"];

export default function Onboarding() {
  const router = useRouter();
  const [f, setF] = useState({ ageBand: "", gender: "", region: "", education: "" });
  const [consent, setConsent] = useState(false);
  const ready = consent && f.ageBand && f.gender && f.region && f.education;

  async function start() {
    const id = getOrCreateParticipantId();
    await fetch("/api/participant", { method: "POST", body: JSON.stringify({ id, ...f }) });
    router.push("/jogar");
  }

  return (
    <main style={{ maxWidth: 480, margin: "40px auto", fontFamily: "system-ui", padding: "0 16px" }}>
      <h1>Atos de Fala — ajude a IA a entender o português</h1>
      <p>Anônimo. Conte um pouco sobre você (pra pesquisa de como cada perfil interpreta intenções):</p>
      <label>Faixa de idade
        <select value={f.ageBand} onChange={(e) => setF({ ...f, ageBand: e.target.value })}>
          <option value="">—</option>{["18-24","25-34","35-44","45-54","55+"].map((v) => <option key={v}>{v}</option>)}
        </select>
      </label>
      <label>Gênero
        <select value={f.gender} onChange={(e) => setF({ ...f, gender: e.target.value })}>
          <option value="">—</option>{["feminino","masculino","outro","prefiro não dizer"].map((v) => <option key={v}>{v}</option>)}
        </select>
      </label>
      <label>Estado (UF)
        <select value={f.region} onChange={(e) => setF({ ...f, region: e.target.value })}>
          <option value="">—</option>{REGIONS.map((v) => <option key={v}>{v}</option>)}
        </select>
      </label>
      <label>Escolaridade
        <select value={f.education} onChange={(e) => setF({ ...f, education: e.target.value })}>
          <option value="">—</option>{["fundamental","médio","superior","pós"].map((v) => <option key={v}>{v}</option>)}
        </select>
      </label>
      <label style={{ display: "block", margin: "12px 0" }}>
        <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />
        {" "}Concordo que minhas respostas entrem em um dataset aberto (CC BY).
      </label>
      <button disabled={!ready} onClick={start}>Começar</button>
    </main>
  );
}
```

- [ ] **Step 4: Verify (integration)**

Run: `cd web && DATABASE_URL="<neon-url>" npm run dev`, open `http://localhost:3000`, fill the form, click Começar.
Expected: a `participant` + `participant_stats` row is created in Neon; the browser navigates to `/jogar` (which 404s until Task 9 — that's fine here).

- [ ] **Step 5: Commit**

```bash
git add web/lib/participant.ts web/app/page.tsx web/app/api/participant/route.ts
git commit -m "feat(web): anonymous onboarding (demographics + consent)"
```

---

### Task 7: Rota `GET /api/next-item`

**Files:**
- Create: `web/app/api/next-item/route.ts`

- [ ] **Step 1: Write the route**

```typescript
// web/app/api/next-item/route.ts
import { NextResponse } from "next/server";
import { sql } from "@/lib/db";
import { pickNextItem, Candidate } from "@/lib/serving";

export async function GET(req: Request) {
  const participant = new URL(req.url).searchParams.get("participant");
  if (!participant) return NextResponse.json({ error: "participant required" }, { status: 400 });

  // candidates = items this participant has not voted on yet, with current vote counts
  const rows = (await sql`
    select i.id, i.is_honeypot,
           (select count(*) from vote v join item_span s on s.id = v.item_span_id where s.item_id = i.id) as vote_count
    from item i
    where not exists (
      select 1 from vote v join item_span s on s.id = v.item_span_id
      where s.item_id = i.id and v.participant_id = ${participant}
    )`) as { id: number; is_honeypot: boolean; vote_count: number }[];

  const candidates: Candidate[] = rows.map((r) => ({ id: r.id, isHoneypot: r.is_honeypot, voteCount: Number(r.vote_count) }));
  const stats = (await sql`select items_done from participant_stats where participant_id = ${participant}`) as { items_done: number }[];
  const itemsDone = stats[0]?.items_done ?? 0;

  const pick = pickNextItem(candidates, itemsDone);
  if (!pick) return NextResponse.json({ item: null });

  const item = (await sql`select id, text, is_honeypot from item where id = ${pick.id}`) as any[];
  const spans = await sql`select id, char_start, char_end, ai_act, display_order
                          from item_span where item_id = ${pick.id} order by display_order`;
  return NextResponse.json({ item: { ...item[0], spans } });
}
```

- [ ] **Step 2: Verify (integration)**

After seeding at least one item (via the Python `atos.collect export`, Plano 1 Task 9):
Run: `curl "http://localhost:3000/api/next-item?participant=<uuid>"`
Expected: JSON with `item.text` and an ordered `spans` array (or `{"item":null}` if none left).

- [ ] **Step 3: Commit**

```bash
git add web/app/api/next-item/route.ts
git commit -m "feat(web): GET /api/next-item (dedup + honeypot cadence)"
```

---

### Task 8: Rota `POST /api/vote` (grava votos + atualiza stats/confiabilidade)

**Files:**
- Create: `web/app/api/vote/route.ts`

- [ ] **Step 1: Write the route**

```typescript
// web/app/api/vote/route.ts
import { NextResponse } from "next/server";
import { sql } from "@/lib/db";
import { applyItemOutcome, Stats } from "@/lib/scoring";

// body: { participant, itemId, votes: [{ spanId, verdict, correctedAct? }] }
export async function POST(req: Request) {
  const { participant, itemId, votes } = await req.json();
  if (!participant || !itemId || !Array.isArray(votes) || votes.length === 0) {
    return NextResponse.json({ error: "missing fields" }, { status: 400 });
  }

  for (const v of votes) {
    await sql`insert into vote (participant_id, item_span_id, verdict, corrected_act)
              values (${participant}, ${v.spanId}, ${v.verdict}, ${v.correctedAct ?? null})
              on conflict (participant_id, item_span_id) do nothing`;
  }

  // honeypot? compare each vote's chosen act to span_gold; correct = all spans right
  const item = (await sql`select is_honeypot from item where id = ${itemId}`) as { is_honeypot: boolean }[];
  let honeypotCorrect: boolean | null = null;
  if (item[0]?.is_honeypot) {
    const golds = (await sql`select sg.item_span_id, sg.gold_act from span_gold sg
                             join item_span s on s.id = sg.item_span_id where s.item_id = ${itemId}`) as
                  { item_span_id: number; gold_act: string }[];
    const goldBy = new Map(golds.map((g) => [g.item_span_id, g.gold_act]));
    const spanAiAct = new Map(((await sql`select id, ai_act from item_span where item_id = ${itemId}`) as any[])
      .map((s) => [s.id, s.ai_act]));
    honeypotCorrect = votes.every((v: any) => {
      const chosen = v.verdict === "agree" ? spanAiAct.get(v.spanId) : v.correctedAct;
      return chosen === goldBy.get(v.spanId);
    });
  }

  const cur = (await sql`select points, streak, reliability, items_done from participant_stats
                         where participant_id = ${participant}`) as any[];
  const stats: Stats = {
    points: cur[0]?.points ?? 0, streak: cur[0]?.streak ?? 0,
    reliability: cur[0]?.reliability ?? 0.5, itemsDone: cur[0]?.items_done ?? 0,
  };
  const next = applyItemOutcome(stats, votes.length, honeypotCorrect);
  await sql`update participant_stats set points=${next.points}, streak=${next.streak},
            reliability=${next.reliability}, items_done=${next.itemsDone}
            where participant_id = ${participant}`;

  return NextResponse.json({ stats: next });
}
```

- [ ] **Step 2: Verify (integration)**

Run:
```bash
curl -X POST http://localhost:3000/api/vote -H 'content-type: application/json' \
  -d '{"participant":"<uuid>","itemId":1,"votes":[{"spanId":1,"verdict":"agree"}]}'
```
Expected: JSON `{stats:{points:10,streak:1,...}}`; a `vote` row exists; `participant_stats` updated.

- [ ] **Step 3: Commit**

```bash
git add web/app/api/vote/route.ts
git commit -m "feat(web): POST /api/vote (persist + stats + honeypot reliability)"
```

---

### Task 9: Rotas `POST /api/suggestion` e `GET /api/me`

**Files:**
- Create: `web/app/api/suggestion/route.ts`, `web/app/api/me/route.ts`

- [ ] **Step 1: Write the suggestion route**

```typescript
// web/app/api/suggestion/route.ts
import { NextResponse } from "next/server";
import { sql } from "@/lib/db";
import { POINTS_SUGGESTION } from "@/lib/scoring";

// body: { participant, spanId, text }
export async function POST(req: Request) {
  const { participant, spanId, text } = await req.json();
  if (!participant || !spanId || !text?.trim()) {
    return NextResponse.json({ error: "missing fields" }, { status: 400 });
  }
  await sql`insert into suggestion (participant_id, item_span_id, text)
            values (${participant}, ${spanId}, ${text.trim()})`;
  await sql`update participant_stats set points = points + ${POINTS_SUGGESTION}
            where participant_id = ${participant}`;
  return NextResponse.json({ ok: true, awarded: POINTS_SUGGESTION });
}
```

- [ ] **Step 2: Write the me route**

```typescript
// web/app/api/me/route.ts
import { NextResponse } from "next/server";
import { sql } from "@/lib/db";

export async function GET(req: Request) {
  const participant = new URL(req.url).searchParams.get("participant");
  if (!participant) return NextResponse.json({ error: "participant required" }, { status: 400 });
  const rows = (await sql`select points, streak, reliability, items_done
                          from participant_stats where participant_id = ${participant}`) as any[];
  return NextResponse.json(rows[0] ?? { points: 0, streak: 0, reliability: 0.5, items_done: 0 });
}
```

- [ ] **Step 3: Verify (integration)**

Run:
```bash
curl -X POST http://localhost:3000/api/suggestion -H 'content-type: application/json' \
  -d '{"participant":"<uuid>","spanId":1,"text":"Me manda aí?"}'
curl "http://localhost:3000/api/me?participant=<uuid>"
```
Expected: suggestion row created, +20 points; `/api/me` returns the current stats.

- [ ] **Step 4: Commit**

```bash
git add web/app/api/suggestion/route.ts web/app/api/me/route.ts
git commit -m "feat(web): suggestion + me routes"
```

---

### Task 10: Tela do jogo (`/jogar`)

**Files:**
- Create: `web/app/jogar/page.tsx`

- [ ] **Step 1: Write the game page**

```tsx
// web/app/jogar/page.tsx
"use client";
import { useEffect, useState } from "react";
import { getOrCreateParticipantId } from "@/lib/participant";
import { ACTS } from "@/lib/taxonomy";

type Span = { id: number; char_start: number; char_end: number; ai_act: string };
type Item = { id: number; text: string; spans: Span[] };

export default function Jogar() {
  const [pid, setPid] = useState<string>("");
  const [item, setItem] = useState<Item | null>(null);
  const [verdicts, setVerdicts] = useState<Record<number, { verdict: string; correctedAct?: string }>>({});
  const [points, setPoints] = useState(0);
  const [streak, setStreak] = useState(0);

  useEffect(() => { setPid(getOrCreateParticipantId()); }, []);
  useEffect(() => { if (pid) loadNext(pid); }, [pid]);

  async function loadNext(p: string) {
    const r = await fetch(`/api/next-item?participant=${p}`).then((x) => x.json());
    setItem(r.item); setVerdicts({});
  }

  async function submit() {
    if (!item) return;
    const votes = item.spans.map((s) => ({
      spanId: s.id,
      verdict: verdicts[s.id]?.verdict ?? "agree",
      correctedAct: verdicts[s.id]?.correctedAct,
    }));
    const r = await fetch("/api/vote", { method: "POST", body: JSON.stringify({ participant: pid, itemId: item.id, votes }) }).then((x) => x.json());
    setPoints(r.stats.points); setStreak(r.stats.streak);
    loadNext(pid);
  }

  async function suggest(spanId: number, text: string) {
    if (!text.trim()) return;
    await fetch("/api/suggestion", { method: "POST", body: JSON.stringify({ participant: pid, spanId, text }) });
  }

  if (!item) return <main style={{ maxWidth: 640, margin: "40px auto", fontFamily: "system-ui" }}><p>Sem mais frases por agora. Valeu! 🙌 ({points} pts)</p></main>;

  return (
    <main style={{ maxWidth: 640, margin: "40px auto", fontFamily: "system-ui", padding: "0 16px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", color: "#666" }}>
        <span>Pontos: {points}</span><span>Streak: {streak}🔥</span>
      </div>
      <p style={{ fontSize: 18 }}>{item.text}</p>
      {item.spans.map((s) => {
        const v = verdicts[s.id]?.verdict ?? "agree";
        return (
          <div key={s.id} style={{ border: "1px solid #e5e5e5", borderRadius: 10, padding: 12, marginBottom: 10 }}>
            <b>“{item.text.slice(s.char_start, s.char_end)}”</b> — IA diz: <code>{s.ai_act}</code>
            <div style={{ marginTop: 8 }}>
              <button onClick={() => setVerdicts({ ...verdicts, [s.id]: { verdict: "agree" } })} aria-pressed={v === "agree"}>✓ certo</button>
              <button onClick={() => setVerdicts({ ...verdicts, [s.id]: { verdict: "disagree", correctedAct: ACTS[0] } })} aria-pressed={v === "disagree"}>✗ corrigir</button>
              {v === "disagree" && (
                <select value={verdicts[s.id]?.correctedAct ?? ACTS[0]}
                        onChange={(e) => setVerdicts({ ...verdicts, [s.id]: { verdict: "disagree", correctedAct: e.target.value } })}>
                  {ACTS.map((a) => <option key={a} value={a}>{a}</option>)}
                </select>
              )}
            </div>
            <details style={{ marginTop: 6 }}>
              <summary style={{ cursor: "pointer", color: "#5b21b6" }}>＋ sugerir outra forma (bônus)</summary>
              <SuggestBox onSubmit={(t) => suggest(s.id, t)} />
            </details>
          </div>
        );
      })}
      <button onClick={submit} style={{ fontWeight: 700, padding: "10px 22px" }}>Próxima →</button>
    </main>
  );
}

function SuggestBox({ onSubmit }: { onSubmit: (t: string) => void }) {
  const [t, setT] = useState("");
  return (
    <div style={{ marginTop: 6 }}>
      <input value={t} onChange={(e) => setT(e.target.value)} placeholder="mesma intenção, outras palavras…" />
      <button onClick={() => { onSubmit(t); setT(""); }}>＋ Adicionar</button>
    </div>
  );
}
```

- [ ] **Step 2: Verify (integration / manual smoke)**

With Neon seeded (Plano 1 export) and `npm run dev`: open `/`, onboard, land on `/jogar`. Evaluate spans, hit "Próxima", confirm points/streak update and a new frase loads; add a suggestion and confirm +20.
Expected: full loop works end to end against Neon.

- [ ] **Step 3: Commit**

```bash
git add web/app/jogar/page.tsx
git commit -m "feat(web): game screen (evaluate spans + suggest, score/streak, next)"
```

---

### Task 11: Deploy (Vercel + Neon) e fumaça e2e

**Files:**
- Create: `web/README.md` (env + deploy runbook)

- [ ] **Step 1: Write the runbook**

```markdown
# web — Coleta Colaborativa (Next.js)

## Env
- `DATABASE_URL` — connection string do Neon (Postgres). Local em `web/.env.local`; na Vercel, em Project Settings → Environment Variables.

## Setup local
1. `cd web && npm install`
2. `DATABASE_URL=... npm run migrate`   # aplica ../db/schema.sql
3. (no repo Python) semear itens: `python -m atos.collect export --dataset data/dataset.jsonl --honeypots gold/honeypots.jsonl`
4. `DATABASE_URL=... npm run dev`        # http://localhost:3000

## Deploy
1. Importar o diretório `web/` como projeto na Vercel (root directory = `web`).
2. Setar `DATABASE_URL` (Neon) nas env vars da Vercel.
3. Push → deploy automático. Rodar a migration uma vez (`npm run migrate` localmente apontando pro Neon de produção, ou via job).

## Testes
- `npm test` — unit (scoring, serving, taxonomy), sem banco.
```

- [ ] **Step 2: Run unit tests + a production build**

Run: `cd web && npm test && npm run build`
Expected: testes verdes; `next build` conclui sem erro de tipo.

- [ ] **Step 3: Manual e2e checklist (against Neon)**

- [ ] onboarding cria `participant` + `participant_stats`
- [ ] `/jogar` carrega uma frase com spans
- [ ] ✓/✗ + Próxima incrementa pontos e streak; nova frase aparece
- [ ] correção grava `corrected_act`
- [ ] sugestão grava em `suggestion` e dá +20
- [ ] item honeypot: errar a isca derruba `reliability` em `participant_stats`
- [ ] mesma frase não reaparece pro mesmo participante (dedup)

- [ ] **Step 4: Commit**

```bash
git add web/README.md
git commit -m "docs(web): env + deploy runbook (Vercel/Neon) + e2e checklist"
```

---

## Self-Review

**Spec coverage (web app):**
- Onboarding anônimo (4 campos + consentimento + id no navegador) → Task 6. ✓
- Loop do jogo (✓/✗ por caixinha + sugestão opcional) → Task 10. ✓
- API `next-item` (dedup + honeypot a cada ~7) → Task 7 (usa `pickNextItem`, Task 3). ✓
- API `vote` (persiste, atualiza stats, confiabilidade via honeypot) → Task 8 (usa `applyItemOutcome`, Task 2). ✓
- API `suggestion` (+20) e `me` → Task 9. ✓
- Pontuação espelhando `score.py` → Task 2 (mesmos valores; teste compara 10/15/20, 0.55/0.4). ✓
- Aplica o mesmo `db/schema.sql` (contrato) → Task 5 (migration). ✓
- Stack Next.js/Vercel/Neon → Tasks 1, 5, 11. ✓
- Demografia idade/gênero/região/escolaridade → Task 6 (form) + schema (Plano 1). ✓

**Fora do v1 (não há task — correto):** níveis/domínios (notícias), ranking público, peer-review de sugestão, login social, Fase 2 cobertura, publicação automática no HF. Confirmação de paráfrase é do Plano 1 (Task 7 lá), não do app.

**Placeholder scan:** sem TBD/TODO; todo passo de código tem bloco completo; rotas/páginas têm verificação de integração explícita (não "teste depois").

**Type consistency:** `Stats {points,streak,reliability,itemsDone}` e `applyItemOutcome(stats,nSpans,honeypotCorrect)` idênticos em Tasks 2/8. `Candidate {id,isHoneypot,voteCount}` e `pickNextItem(candidates,itemsDone)` idênticos em Tasks 3/7. `ACTS` (13) usado em Tasks 4/10. Corpo do `vote` (`{participant,itemId,votes:[{spanId,verdict,correctedAct?}]}`) idêntico entre Task 8 (rota) e Task 10 (cliente). `sql` tagged-template de `@/lib/db` usado igual em todas as rotas.

**Dependência entre planos:** Task 5/7 dependem do `db/schema.sql` (Plano 1 Task 1) e de itens semeados pelo `atos.collect export` (Plano 1 Task 9). Ordem recomendada: Plano 1 inteiro → Plano 2.
