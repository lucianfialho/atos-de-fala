"""Confirm that a player's paraphrase preserves the span's speech act, using the same LLM
adjudicator family as generation. `client` is any object with .complete(messages)->str
(e.g. chomsky.gen.deepseek.DeepSeekClient), so tests inject a fake."""
import json
import re
from typing import Callable, Dict, List


def _parse_preserves_json(raw: str) -> Dict:
    """Extract a JSON object from raw LLM output, returning {} on any failure."""
    _FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
    candidate = None
    m = _FENCE.search(raw)
    if m:
        candidate = m.group(1)
    else:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = raw[start: end + 1]
    if candidate is None:
        return {}
    try:
        obj = json.loads(candidate)
    except json.JSONDecodeError:
        return {}
    return obj if isinstance(obj, dict) else {}


def build_paraphrase_check_prompt(act: str, original: str, paraphrase: str) -> List[Dict]:
    system = (
        "Você verifica se uma reescrita preserva o ATO DE FALA de um trecho em PT-BR. "
        'Responda SÓ com JSON: {"preserves": true|false}.'
    )
    user = (
        f"Ato: {act}\nOriginal: {original}\nReescrita: {paraphrase}\n"
        "A reescrita realiza o MESMO ato de fala que o original? Responda o JSON."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def confirm_suggestion(
    client,
    act: str,
    original: str,
    paraphrase: str,
    parse: Callable[[str], Dict] = _parse_preserves_json,
) -> bool:
    raw = client.complete(build_paraphrase_check_prompt(act, original, paraphrase))
    return bool(parse(raw).get("preserves", False))
