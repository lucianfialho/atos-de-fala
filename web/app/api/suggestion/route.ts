import { NextResponse } from "next/server";
import { sql } from "@/lib/db";
import { POINTS_SUGGESTION } from "@/lib/scoring";
import { getIp, rateLimit } from "@/lib/rateLimit";

const MAX_SUGGESTION_LEN = 200;

// body: { participant, spanId, text }
export async function POST(req: Request) {
  if (!(await rateLimit(`${getIp(req)}:suggestion`, 20, 60))) {
    return NextResponse.json({ error: "muitas requisições, calma aí" }, { status: 429 });
  }
  const { participant, spanId, text } = await req.json();
  if (!participant || !spanId || !text?.trim()) {
    return NextResponse.json({ error: "missing fields" }, { status: 400 });
  }
  const clean = text.trim();
  if (clean.length > MAX_SUGGESTION_LEN) {
    return NextResponse.json({ error: `sugestão muito longa (máx ${MAX_SUGGESTION_LEN})` }, { status: 400 });
  }
  await sql`insert into suggestion (participant_id, item_span_id, text)
            values (${participant}, ${spanId}, ${clean})`;
  await sql`update participant_stats set points = points + ${POINTS_SUGGESTION}
            where participant_id = ${participant}`;
  return NextResponse.json({ ok: true, awarded: POINTS_SUGGESTION });
}
