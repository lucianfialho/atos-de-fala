// Soft pastel tints for each of the 13 speech acts.
// Background is low-saturation on the off-white canvas; text stays readable.
// Aligned with the existing orb palette (mint, peach, lavender, sky, rose) + extras.

export type ActTint = { bg: string; text: string; border: string };

export const ACT_TINT: Record<string, ActTint> = {
  informar:        { bg: "#e8f4fd", text: "#1a5276", border: "#aed6f1" },
  perguntar:       { bg: "#fef9e7", text: "#7d6608", border: "#f9e79f" },
  concordar:       { bg: "#e9f7ef", text: "#1e8449", border: "#a9dfbf" },
  discordar:       { bg: "#fdecea", text: "#922b21", border: "#f5b7b1" },
  pedir:           { bg: "#fdf2fb", text: "#76448a", border: "#d7bde2" },
  sugerir:         { bg: "#eafaf1", text: "#1a7a42", border: "#a3e4c2" },
  oferecer:        { bg: "#fef5e7", text: "#935116", border: "#fad7a0" },
  prometer:        { bg: "#e8f8f5", text: "#0e6655", border: "#a2d9ce" },
  saudar:          { bg: "#fdedec", text: "#943126", border: "#f1948a" },
  agradecer:       { bg: "#f0f4ff", text: "#2c3e8c", border: "#b0bcf0" },
  desculpar:       { bg: "#fff0f3", text: "#8c2c44", border: "#f0b0c0" },
  despedir:        { bg: "#f5f0ff", text: "#5b2c8c", border: "#c8b0f0" },
  expressar_emocao:{ bg: "#fff4e8", text: "#8c5e2c", border: "#f0d0a0" },
};

// Fallback for unknown acts
export const DEFAULT_TINT: ActTint = { bg: "#f5f5f5", text: "#4e4e4e", border: "#d6d3d1" };

export function getActTint(act: string): ActTint {
  return ACT_TINT[act] ?? DEFAULT_TINT;
}

// Circled digit superscripts ①②③… up to 9
export function getIndexGlyph(i: number): string {
  const glyphs = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨"];
  return glyphs[i] ?? `(${i + 1})`;
}
