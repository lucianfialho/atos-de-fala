"use client";
import { useState } from "react";
import { getExistingParticipantId, clearParticipantId } from "@/lib/participant";

// "Esquecer meus dados" — deletes everything tied to this browser's anonymous id (LGPD).
export default function ForgetLink() {
  const [state, setState] = useState<"idle" | "done" | "none" | "err">("idle");

  async function forget() {
    const id = getExistingParticipantId();
    if (!id) { setState("none"); return; }
    if (!confirm("Remover suas anotações e seu perfil deste navegador? Não dá pra desfazer.")) return;
    try {
      const r = await fetch("/api/forget", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ participant: id }),
      });
      if (!r.ok) throw new Error();
      clearParticipantId();
      setState("done");
    } catch {
      setState("err");
    }
  }

  if (state === "done") return <span className="lp-footer-forget-done">dados removidos ✓</span>;
  const label =
    state === "none" ? "nada pra remover neste navegador"
    : state === "err" ? "erro — tente de novo"
    : "Esquecer meus dados";
  return (
    <a role="button" tabIndex={0} className="lp-footer-forget" onClick={forget}
       onKeyDown={(e) => { if (e.key === "Enter") forget(); }}>
      {label}
    </a>
  );
}
