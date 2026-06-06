import { NextResponse } from "next/server";
import { sql } from "@/lib/db";
import { applyItemOutcome, Stats } from "@/lib/scoring";
import { getIp, rateLimit } from "@/lib/rateLimit";

// body: { participant, itemId, votes: [{ spanId, verdict, correctedAct? }] }
export async function POST(req: Request) {
  if (!(await rateLimit(`${getIp(req)}:vote`, 40, 60))) {
    return NextResponse.json({ error: "muitas requisições, calma aí" }, { status: 429 });
  }
  const { participant, itemId, votes } = await req.json();
  if (!participant || !itemId || !Array.isArray(votes) || votes.length === 0) {
    return NextResponse.json({ error: "missing fields" }, { status: 400 });
  }

  for (const v of votes) {
    await sql`insert into vote (participant_id, item_span_id, verdict, corrected_act)
              values (${participant}, ${v.spanId}, ${v.verdict}, ${v.correctedAct ?? null})
              on conflict (participant_id, item_span_id) do nothing`;
  }

  const item = (await sql`select is_honeypot from item where id = ${itemId}`) as { is_honeypot: boolean }[];
  let honeypotCorrect: boolean | null = null;
  if (item[0]?.is_honeypot) {
    const golds = (await sql`select sg.item_span_id, sg.gold_act from span_gold sg
                             join item_span s on s.id = sg.item_span_id where s.item_id = ${itemId}`) as
                  { item_span_id: number; gold_act: string }[];
    const goldBy = new Map(golds.map((g) => [String(g.item_span_id), g.gold_act]));
    const spanAiAct = new Map(((await sql`select id, ai_act from item_span where item_id = ${itemId}`) as any[])
      .map((s) => [String(s.id), s.ai_act]));
    honeypotCorrect = votes.every((v: any) => {
      const key = String(v.spanId);
      const chosen = v.verdict === "agree" ? spanAiAct.get(key) : v.correctedAct;
      return chosen === goldBy.get(key);
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
