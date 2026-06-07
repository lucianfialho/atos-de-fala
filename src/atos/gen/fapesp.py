"""Fetch + parse Memória Roda Viva (rodaviva.fapesp.br) transcripts into speaker turns.

Python mirror of the web repo's lib/fapesp.ts — real *dialogic* PT-BR (interview/debate,
multiple speakers) for teacher annotation. Pages are ISO-8859-1 with HTML entities; each turn
is `<p ...><strong>Speaker:</strong> text...</p>`.
"""
import html
import re
from typing import Dict, List

import requests

_P_BLOCK = re.compile(r"<p\b[^>]*>.*?</p>", re.S | re.I)
_TAG = re.compile(r"<[^>]*>")
_WS = re.compile(r"\s+")


def _clean(s: str) -> str:
    return _WS.sub(" ", html.unescape(_TAG.sub("", s))).strip()


def _is_speaker(name: str) -> bool:
    n = name.strip()
    if len(n) < 2 or len(n) > 45:
        return False
    if re.search(r"[.?!;]", n):
        return False
    if n.startswith("["):
        return False
    return bool(re.match(r"[A-Za-zÀ-ÿ]", n))


def parse_interview(html_text: str) -> List[Dict]:
    """Return [{speaker, text}] turns from a FAPESP interview page's HTML."""
    turns: List[Dict] = []
    for block in _P_BLOCK.findall(html_text):
        txt = _clean(block)
        if not txt or txt.startswith("["):
            continue
        colon = txt.find(":")
        if colon < 0:
            continue
        speaker, body = txt[:colon], txt[colon + 1:].strip()
        if _is_speaker(speaker) and len(body) >= 2:
            turns.append({"speaker": speaker, "text": body})
    return turns


def fetch_interview(url: str) -> List[Dict]:
    """Fetch a rodaviva.fapesp.br page (ISO-8859-1) and parse its turns."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return parse_interview(resp.content.decode("latin1"))
