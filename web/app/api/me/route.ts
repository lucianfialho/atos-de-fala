import { NextResponse } from "next/server";
import { sql } from "@/lib/db";

export async function GET(req: Request) {
  const participant = new URL(req.url).searchParams.get("participant");
  if (!participant) return NextResponse.json({ error: "participant required" }, { status: 400 });
  const rows = (await sql`select points, streak, reliability, items_done
                          from participant_stats where participant_id = ${participant}`) as any[];
  return NextResponse.json(rows[0] ?? { points: 0, streak: 0, reliability: 0.5, items_done: 0 });
}
