// Hand-drawn ink annotation marks.
// Rough, irregular SVG paths so they read as marginalia, not geometry.
// All strokes use currentColor + round caps; color comes from the parent (ink/muted).

type MarkProps = {
  className?: string;
  width?: number;
  height?: number;
  style?: React.CSSProperties;
  strokeWidth?: number;
  "aria-hidden"?: boolean;
};

const base = (p: MarkProps) => ({
  className: p.className,
  style: p.style,
  "aria-hidden": true as const,
  fill: "none" as const,
  stroke: "currentColor" as const,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
});

// Squiggly underline — drawn under a key word.
export function Underline({ strokeWidth = 2.4, ...p }: MarkProps) {
  return (
    <svg viewBox="0 0 120 12" width={p.width ?? 120} height={p.height ?? 12} {...base(p)} preserveAspectRatio="none">
      <path
        d="M2 7 C 14 3, 22 10, 34 6 S 54 3, 66 7 78 11, 90 6 110 4, 118 8"
        strokeWidth={strokeWidth}
      />
    </svg>
  );
}

// Bracket — a vertical squared-off marginal bracket [ , slightly wobbly.
export function Bracket({ strokeWidth = 2.2, ...p }: MarkProps) {
  return (
    <svg viewBox="0 0 16 60" width={p.width ?? 16} height={p.height ?? 60} {...base(p)}>
      <path
        d="M13 3 C 6 3, 5 5, 5 11 L 4.6 27 C 4.6 30, 3 30, 2.5 31 C 3.2 32, 4.8 32, 4.8 35 L 5.2 50 C 5.2 56, 6.5 57, 13 57"
        strokeWidth={strokeWidth}
      />
    </svg>
  );
}

// Circle scribble — a loose hand-drawn ring (1.2 loops) to ring a word.
export function CircleScribble({ strokeWidth = 2.2, ...p }: MarkProps) {
  return (
    <svg viewBox="0 0 110 70" width={p.width ?? 110} height={p.height ?? 70} {...base(p)} preserveAspectRatio="none">
      <path
        d="M64 8 C 30 4, 8 18, 9 36 C 10 56, 44 66, 72 60 C 96 55, 104 38, 96 24 C 88 11, 60 5, 38 9"
        strokeWidth={strokeWidth}
      />
    </svg>
  );
}

// Arrow — a curved hand-drawn arrow with a two-stroke head.
// Points down-left by default (use transform/scale to re-aim).
export function Arrow({ strokeWidth = 2.2, ...p }: MarkProps) {
  return (
    <svg viewBox="0 0 90 70" width={p.width ?? 90} height={p.height ?? 70} {...base(p)}>
      <path d="M84 6 C 70 6, 30 8, 16 44 C 13 52, 12 58, 11 63" strokeWidth={strokeWidth} />
      <path d="M3 50 C 6 56, 9 61, 11 64" strokeWidth={strokeWidth} />
      <path d="M22 56 C 18 60, 14 62, 11 64" strokeWidth={strokeWidth} />
    </svg>
  );
}
