from typing import Dict, List, Tuple
from chomsky.schema import Annotation, Span


def resolve_quoted_spans(
    text: str, items: List[Dict]
) -> Tuple[Annotation, List[str]]:
    spans: List[Span] = []
    errors: List[str] = []
    cursor = 0
    for item in items:
        quote = item["quote"]
        act = item["act"]
        idx = text.find(quote, cursor)
        if idx == -1:
            errors.append(f"quote not found at/after offset {cursor}: {quote!r}")
            continue
        start, end = idx, idx + len(quote)
        spans.append(Span(start, end, act))
        cursor = end
    return Annotation(text=text, spans=spans), errors
