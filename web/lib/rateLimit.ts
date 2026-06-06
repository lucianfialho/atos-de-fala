import { sql } from "./db";

// Client IP from Vercel's forwarded header. Falls back to a shared "unknown" bucket.
export function getIp(req: Request): string {
  const xff = req.headers.get("x-forwarded-for");
  return xff?.split(",")[0]?.trim() || "unknown";
}

// Sliding-window rate limit backed by Neon (no extra service). `bucket` should encode the
// IP + the route (e.g. `${ip}:vote`). Prunes only this bucket's expired hits (bounded, uses
// the index), counts the rest, and records the hit. Returns true if the request is allowed.
export async function rateLimit(bucket: string, limit: number, windowSec: number): Promise<boolean> {
  await sql`delete from rate_hit
            where bucket = ${bucket} and created_at < now() - make_interval(secs => ${windowSec})`;
  const rows = (await sql`select count(*)::int as n from rate_hit where bucket = ${bucket}`) as { n: number }[];
  if ((rows[0]?.n ?? 0) >= limit) return false;
  await sql`insert into rate_hit (bucket) values (${bucket})`;
  return true;
}
