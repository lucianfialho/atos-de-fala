import { NextResponse } from "next/server";
import { getIp, rateLimit } from "@/lib/rateLimit";

const HF = "https://lucianfialho-atos-de-fala-ptbr.hf.space/gradio_api/call/predict";

export async function POST(req: Request) {
  if (!(await rateLimit(`${getIp(req)}:demo`, 15, 60))) {
    return NextResponse.json({ error: "muitas requisições, calma aí" }, { status: 429 });
  }
  let text = "";
  try { text = (await req.json()).text ?? ""; } catch { /* ignore */ }
  text = String(text).trim();
  if (!text) return NextResponse.json({ error: "texto vazio" }, { status: 400 });
  if (text.length > 200) return NextResponse.json({ error: "texto muito longo (máx 200)" }, { status: 400 });
  try {
    const post = await fetch(HF, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: [text] }), signal: AbortSignal.timeout(15000),
    });
    if (!post.ok) throw new Error("post failed");
    const { event_id } = await post.json();
    const res = await fetch(`${HF}/${event_id}`, { signal: AbortSignal.timeout(60000) });
    const body = await res.text();
    const line = body.split("\n").reverse().find((l) => l.startsWith("data: ") && l.includes("token"));
    if (!line) throw new Error("no result");
    const tuples = JSON.parse(line.slice(6))[0] as { token: string; class_or_confidence: string | null }[];
    const segments = tuples.map((t) => ({ text: t.token, act: t.class_or_confidence }));
    return NextResponse.json({ segments });
  } catch {
    // cold start or timeout — let the client show a friendly "model waking up" state
    return NextResponse.json({ error: "coldstart" }, { status: 503 });
  }
}
