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
