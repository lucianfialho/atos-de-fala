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
  return NextResponse.json({
    participants: p[0]?.n ?? 0,
    votes: v[0]?.n ?? 0,
    states: Number(s[0]?.states ?? 0),
    byRegion,
  });
}
