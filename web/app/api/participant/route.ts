import { NextResponse } from "next/server";
import { sql } from "@/lib/db";
import { getIp, rateLimit } from "@/lib/rateLimit";

export async function POST(req: Request) {
  if (!(await rateLimit(`${getIp(req)}:participant`, 10, 60))) {
    return NextResponse.json({ error: "muitas requisições, calma aí" }, { status: 429 });
  }
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
