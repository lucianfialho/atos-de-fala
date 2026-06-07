from typing import Dict, List, Optional
import json
import re

_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def parse_llm_json(raw: str) -> Dict:
    """Extract and validate a {text, spans:[{quote,act}]} object from an LLM reply.

    Tries, in order: a ```json fenced block, then the first balanced-looking
    object via the outermost braces. Raises ValueError if nothing parses or the
    required shape is missing.
    """
    candidate = None
    m = _FENCE.search(raw)
    if m:
        candidate = m.group(1)
    else:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = raw[start : end + 1]
    if candidate is None:
        raise ValueError(f"no JSON object found in LLM reply: {raw[:120]!r}")
    try:
        obj = json.loads(candidate)
    except json.JSONDecodeError as e:
        raise ValueError(f"invalid JSON in LLM reply: {e}") from e
    if not isinstance(obj, dict) or "text" not in obj or "spans" not in obj:
        raise ValueError(f"missing 'text'/'spans' keys: {obj!r}")
    return obj


_SYSTEM = (
    "Voce e um anotador linguistico especialista em atos de fala do portugues "
    "brasileiro. Voce sempre responde APENAS com um objeto JSON valido."
)


def build_generation_prompt(
    rubric: str,
    n: int,
    focus_acts: Optional[List[str]] = None,
    avoid_acts: Optional[List[str]] = None,
) -> List[Dict]:
    user = (
        f"{rubric}\n\n"
        f"Gere {n} exemplo(s). Para CADA exemplo, escreva um texto curto e natural "
        f"em portugues brasileiro e anote os spans de atos de fala. Responda com UM "
        f'objeto JSON por exemplo no formato: '
        f'{{"text": "...", "spans": [{{"quote": "trecho exato do texto", "act": "<ato>"}}]}}. '
        f"Os 'quote' devem ser substrings EXATAS e contiguas do 'text'."
    )
    if focus_acts:
        user += (
            "\n\nIMPORTANTE: priorize textos que naturalmente contenham os seguintes "
            f"atos (estao sub-representados no dataset): {', '.join(focus_acts)}."
        )
    if avoid_acts:
        user += (
            "\n\nEVITE os seguintes atos (ja estao super-representados): "
            f"{', '.join(avoid_acts)}. Nao force saudacoes, agradecimentos nem pedidos "
            "de cortesia: escreva o texto direto ao ponto, sem abertura/fechamento de "
            "cortesia, a menos que seja realmente central ao exemplo."
        )
    return [{"role": "system", "content": _SYSTEM}, {"role": "user", "content": user}]


def build_correction_prompt(rubric: str, text: str, proposed: List[Dict]) -> List[Dict]:
    """Teacher-as-corrector: a smaller model already annotated `text`; the teacher confirms the
    correct spans, fixes wrong act/boundaries, removes non-acts, and ADDS missed ones. Cheaper
    than annotating from scratch and focuses the teacher on the student's errors."""
    import json as _json
    user = (
        f"{rubric}\n\n"
        f"Um modelo menor já anotou os atos de fala do texto abaixo. REVISE a anotação dele: "
        f"confirme os spans corretos, corrija ato/fronteira errados, remova o que não é ato, e "
        f"ADICIONE atos que faltaram. NAO altere o texto. Responda com a anotação FINAL no formato "
        f'{{"text": "<texto inalterado>", "spans": [{{"quote": "trecho exato", "act": "<ato>"}}]}}.\n\n'
        f"TEXTO:\n{text}\n\nANOTACAO DO MODELO:\n{_json.dumps(proposed, ensure_ascii=False)}"
    )
    return [{"role": "system", "content": _SYSTEM}, {"role": "user", "content": user}]


def build_annotation_prompt(rubric: str, text: str) -> List[Dict]:
    user = (
        f"{rubric}\n\n"
        f"Anote os atos de fala do texto a seguir. NAO altere o texto. Responda com "
        f'um objeto JSON: {{"text": "<o texto original, inalterado>", '
        f'"spans": [{{"quote": "trecho exato", "act": "<ato>"}}]}}.\n\n'
        f"TEXTO:\n{text}"
    )
    return [{"role": "system", "content": _SYSTEM}, {"role": "user", "content": user}]


def build_adjudication_prompt(rubric: str, text: str, problems: List[str]) -> List[Dict]:
    issues = "; ".join(problems) if problems else "anotacao anterior invalida ou inconsistente"
    user = (
        f"{rubric}\n\n"
        f"Uma anotacao anterior do texto abaixo teve problemas: {issues}.\n"
        f"Reanote com cuidado, corrigindo esses problemas. NAO altere o texto. "
        f'Responda com um objeto JSON: {{"text": "<o texto original, inalterado>", '
        f'"spans": [{{"quote": "trecho exato", "act": "<ato>"}}]}}.\n\n'
        f"TEXTO:\n{text}"
    )
    return [{"role": "system", "content": _SYSTEM}, {"role": "user", "content": user}]
