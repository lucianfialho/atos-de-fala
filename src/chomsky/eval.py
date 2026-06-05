from typing import Dict, List, Set, Tuple
from chomsky.schema import Annotation

Key = Tuple[int, int, int, str]  # (doc_index, start, end, act)


def _keys(anns: List[Annotation]) -> Set[Key]:
    out: Set[Key] = set()
    for i, ann in enumerate(anns):
        for s in ann.spans:
            out.add((i, s.start, s.end, s.act))
    return out


def _prf1(tp: int, n_pred: int, n_gold: int) -> Dict[str, float]:
    precision = tp / n_pred if n_pred else 0.0
    recall = tp / n_gold if n_gold else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def span_prf1(gold: List[Annotation], pred: List[Annotation]) -> Dict[str, float]:
    g, p = _keys(gold), _keys(pred)
    return _prf1(len(g & p), len(p), len(g))


def per_act_f1(
    gold: List[Annotation], pred: List[Annotation]
) -> Dict[str, Dict[str, float]]:
    g, p = _keys(gold), _keys(pred)
    acts = {k[3] for k in g} | {k[3] for k in p}
    result: Dict[str, Dict[str, float]] = {}
    for act in acts:
        ga = {k for k in g if k[3] == act}
        pa = {k for k in p if k[3] == act}
        result[act] = _prf1(len(ga & pa), len(pa), len(ga))
    return result
