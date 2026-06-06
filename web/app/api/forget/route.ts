import { NextResponse } from "next/server";
import { sql } from "@/lib/db";
import { getIp, rateLimit } from "@/lib/rateLimit";

// LGPD self-serve deletion: removes everything tied to this browser's participant id.
// The schema cascades (vote, suggestion, participant_stats) from participant. Already-published
// aggregated/anonymized dataset rows are not reversible (stated in /termo).
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export async function POST(req: Request) {
  if (!(await rateLimit(`${getIp(req)}:forget`, 10, 60))) {
    return NextResponse.json({ error: "muitas requisições, calma aí" }, { status: 429 });
  }
  let id = "";
  try { id = (await req.json()).participant ?? ""; } catch { /* ignore */ }
  id = String(id).trim();
  if (!UUID.test(id)) return NextResponse.json({ error: "id inválido" }, { status: 400 });
  await sql`delete from participant where id = ${id}`;
  return NextResponse.json({ ok: true });
}
