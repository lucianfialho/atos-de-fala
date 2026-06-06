import { NextResponse } from "next/server";
import { sql } from "@/lib/db";

export async function GET() {
  const p = (await sql`select count(*)::int as n from participant`) as { n: number }[];
  const v = (await sql`select count(*)::int as n from vote`) as { n: number }[];
  const s = (await sql`select count(distinct region) as states from participant`) as { states: number }[];
  const region = (await sql`select p.region, count(*)::int as n
                            from vote v join participant p on p.id = v.participant_id
                            group by p.region`) as { region: string; n: number }[];
  const byRegion: Record<string, number> = {};
  for (const r of region) byRegion[r.region] = r.n;

  // Extended fields — additive, existing consumers still work
  const sug = (await sql`select count(*)::int as n from suggestion`) as { n: number }[];
  const it = (await sql`select count(distinct s.item_id)::int as n from vote v join item_span s on s.id=v.item_span_id`) as { n: number }[];
  const tot = (await sql`select count(*)::int as n from item`) as { n: number }[];
  const ad = (await sql`select verdict, count(*)::int as n from vote group by verdict`) as { verdict: string; n: number }[];
  const acts = (await sql`select s.ai_act, count(*)::int as n from vote v join item_span s on s.id=v.item_span_id group by s.ai_act`) as { ai_act: string; n: number }[];
  const ages = (await sql`select p.age_band, count(*)::int as n from vote v join participant p on p.id=v.participant_id group by p.age_band`) as { age_band: string; n: number }[];
  const sugActs = (await sql`select s.ai_act, count(*)::int as n from suggestion sg join item_span s on s.id=sg.item_span_id group by s.ai_act`) as { ai_act: string; n: number }[];

  let agree = 0;
  let disagree = 0;
  for (const row of ad) {
    if (row.verdict === "agree") agree = row.n;
    else if (row.verdict === "disagree") disagree = row.n;
  }

  const byAct: Record<string, number> = {};
  for (const row of acts) byAct[row.ai_act] = row.n;

  const byAge: Record<string, number> = {};
  for (const row of ages) byAge[row.age_band] = row.n;

  const suggByAct: Record<string, number> = {};
  for (const row of sugActs) suggByAct[row.ai_act] = row.n;

  return NextResponse.json({
    participants: p[0]?.n ?? 0,
    votes: v[0]?.n ?? 0,
    states: Number(s[0]?.states ?? 0),
    byRegion,
    suggestions: sug[0]?.n ?? 0,
    itemsTouched: it[0]?.n ?? 0,
    itemsTotal: tot[0]?.n ?? 0,
    agree,
    disagree,
    byAct,
    byAge,
    suggByAct,
  });
}
