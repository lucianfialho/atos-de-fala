# web — Coleta Colaborativa de Atos de Fala (Next.js)

Jogo anônimo onde a galera avalia (✓/✗) os atos de fala que a IA atribuiu a frases PT-BR
e sugere paráfrases (bônus), gravando votos + perfil demográfico no Postgres que o pipeline
Python (`chomsky.collect`) consome.

## Env
- `DATABASE_URL` — connection string do Neon (Postgres). Local em `web/.env.local`; na Vercel,
  em Project Settings → Environment Variables. O `lib/db.ts` lê `process.env.DATABASE_URL`.

## Setup local
1. `cd web && npm install`
2. `DATABASE_URL=... npm run migrate`   # aplica ../db/schema.sql (contrato compartilhado)
3. (no repo Python, na raiz) semear itens a anotar:
   `python -m chomsky.collect export --dataset data/dataset.jsonl --honeypots gold/honeypots.jsonl`
4. `DATABASE_URL=... npm run dev`        # http://localhost:3000

## Deploy (Vercel)
1. Importar o diretório `web/` como projeto na Vercel (**Root Directory = `web`**).
2. Setar `DATABASE_URL` (Neon) nas env vars da Vercel.
3. Push → deploy automático. Rodar a migration uma vez apontando pro Neon de produção:
   `DATABASE_URL=<neon-prod> npm run migrate`.

## Testes
- `npm test` — unit (scoring, serving, taxonomy), sem banco (Vitest).
- Build/typecheck: `DATABASE_URL="postgres://u:p@localhost/db" npm run build` (o `neon()` não conecta no build).

## Checklist de fumaça e2e (contra um Neon descartável, quando houver banco)
- [ ] onboarding cria `participant` + `participant_stats`
- [ ] `/jogar` carrega uma frase com spans
- [ ] ✓/✗ + Próxima incrementa pontos e streak; nova frase aparece
- [ ] correção grava `corrected_act`
- [ ] sugestão grava em `suggestion` e dá +20
- [ ] item honeypot: errar a isca derruba `reliability` em `participant_stats`
- [ ] mesma frase não reaparece pro mesmo participante (dedup)

## Arquitetura
O app **só coleta**. Toda a lógica de ML, agregação (concordância ponderada por
confiabilidade) e análise de percepção fica no pacote Python `chomsky.collect`, que lê/escreve
o mesmo Postgres. `lib/scoring.ts` é espelho exato de `src/chomsky/collect/score.py` —
mantenha os dois em sincronia.
