"use client";
import { getActTint, getIndexGlyph } from "@/lib/actColors";

type Span = { id: number; char_start: number; char_end: number; ai_act: string };

interface Props {
  text: string;
  spans: Span[];
}

interface Segment {
  type: "text" | "span";
  content: string;
  spanIndex?: number;
  act?: string;
}

function buildSegments(text: string, spans: Span[]): Segment[] {
  // Sort spans by char_start
  const sorted = [...spans].sort((a, b) => a.char_start - b.char_start);
  const segments: Segment[] = [];
  let cursor = 0;

  for (let i = 0; i < sorted.length; i++) {
    const s = sorted[i];
    if (s.char_start > cursor) {
      segments.push({ type: "text", content: text.slice(cursor, s.char_start) });
    }
    segments.push({
      type: "span",
      content: text.slice(s.char_start, s.char_end),
      spanIndex: i,
      act: s.ai_act,
    });
    cursor = s.char_end;
  }

  if (cursor < text.length) {
    segments.push({ type: "text", content: text.slice(cursor) });
  }

  return segments;
}

export default function InlineSentence({ text, spans }: Props) {
  const segments = buildSegments(text, spans);

  return (
    <p
      className="display"
      style={{
        fontSize: "clamp(20px, 2.8vw, 26px)",
        lineHeight: 1.6,
        marginBottom: 28,
        color: "var(--ink)",
        wordBreak: "break-word",
      }}
    >
      {segments.map((seg, i) => {
        if (seg.type === "text") {
          return <span key={i}>{seg.content}</span>;
        }
        const tint = getActTint(seg.act ?? "");
        const glyph = getIndexGlyph(seg.spanIndex ?? 0);
        return (
          <mark
            key={i}
            style={{
              background: tint.bg,
              color: tint.text,
              borderRadius: 4,
              padding: "1px 3px",
              border: `1px solid ${tint.border}`,
              // No italic — let the serif flow naturally
              fontStyle: "inherit",
            }}
          >
            {seg.content}
            <sup
              style={{
                fontSize: "0.65em",
                fontFamily: "var(--font-inter, Inter, system-ui, sans-serif)",
                fontWeight: 600,
                marginLeft: 1,
                verticalAlign: "super",
                color: tint.text,
                opacity: 0.8,
              }}
            >
              {glyph}
            </sup>
          </mark>
        );
      })}
    </p>
  );
}
