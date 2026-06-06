"use client";
// Anonymous identity: a uuid persisted in localStorage. No login.
const KEY = "chomsky_participant_id";

export function getOrCreateParticipantId(): string {
  let id = localStorage.getItem(KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(KEY, id);
  }
  return id;
}

// The stored id without creating one (null if this browser never participated).
export function getExistingParticipantId(): string | null {
  return localStorage.getItem(KEY);
}

// Forget this browser's identity (used by the "esquecer meus dados" flow).
export function clearParticipantId(): void {
  localStorage.removeItem(KEY);
}
