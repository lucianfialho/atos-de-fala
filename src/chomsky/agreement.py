from typing import Set, Tuple
from chomsky.schema import Annotation


def _span_set(ann: Annotation) -> Set[Tuple[int, int, str]]:
    return {(s.start, s.end, s.act) for s in ann.spans}


def span_agreement(a: Annotation, b: Annotation) -> float:
    sa, sb = _span_set(a), _span_set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    tp = len(sa & sb)
    if tp == 0:
        return 0.0
    precision = tp / len(sb)
    recall = tp / len(sa)
    return 2 * precision * recall / (precision + recall)


def gate(a: Annotation, b: Annotation, threshold: float) -> str:
    return "keep" if span_agreement(a, b) >= threshold else "adjudicate"
