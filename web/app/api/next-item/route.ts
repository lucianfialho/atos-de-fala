import { NextResponse } from "next/server";
import { sql } from "@/lib/db";
import { pickNextItem, Candidate } from "@/lib/serving";

export async function GET(req: Request) {
  const participant = new URL(req.url).searchParams.get("participant");
  if (!participant) return NextResponse.json({ error: "participant required" }, { status: 400 });

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
