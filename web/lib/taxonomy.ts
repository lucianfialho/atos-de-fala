// Mirror of config/taxonomy.yaml (FROZEN v1, 13 acts). Used by the correction dropdown.
export const ACTS = [
  "informar", "perguntar", "concordar", "discordar", "pedir", "sugerir",
  "oferecer", "prometer", "saudar", "agradecer", "desculpar", "despedir",
  "expressar_emocao",
] as const;

export type Act = (typeof ACTS)[number];
