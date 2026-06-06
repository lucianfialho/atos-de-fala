import { describe, it, expect } from "vitest";
import { ACTS } from "./taxonomy";

describe("taxonomy", () => {
  it("has the 13 frozen acts", () => {
    expect(ACTS.length).toBe(13);
    expect(ACTS).toContain("pedir");
    expect(ACTS).toContain("expressar_emocao");
  });
});
