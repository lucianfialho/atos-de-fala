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
