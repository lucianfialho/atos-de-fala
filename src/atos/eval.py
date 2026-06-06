from typing import Dict, List, Optional, Set, Tuple
from atos.schema import Annotation, Span

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


def coarsen(anns: List[Annotation], macro: Dict[str, str]) -> List[Annotation]:
    """Relabel every span's act to its macro-class. Acts missing from `macro` keep
    their original name. Offsets and text are preserved, so the result still works
    with span_prf1/per_act_f1 — just at coarser label granularity."""
    return [
        Annotation(a.text, [Span(s.start, s.end, macro.get(s.act, s.act)) for s in a.spans])
        for a in anns
    ]


def dominant_act(ann: Annotation) -> Optional[str]:
    """The single act covering the most characters in this annotation — a sentence-level
    reduction of multi-span output. None if there are no spans."""
    if not ann.spans:
        return None
    by_act: Dict[str, int] = {}
    for s in ann.spans:
        by_act[s.act] = by_act.get(s.act, 0) + (s.end - s.start)
    return max(by_act, key=by_act.get)


def sentence_label_f1(
    gold: List[Annotation],
    pred: List[Annotation],
    macro: Optional[Dict[str, str]] = None,
) -> Dict:
    """Sentence-level evaluation for sentence-level gold (e.g. Porttinari), where exact
    span-F1 is meaningless: gold is one whole-sentence span but the model emits several
    sub-spans, so boundaries almost never match. Here we reduce each item to ONE label
    (the dominant act) and compare by index. With `macro`, both sides are collapsed to
    macro-classes first. Reports:
      - accuracy: dominant(pred) == dominant(gold)
      - lenient_hit_rate: gold's dominant act appears among ANY predicted span act
      - macro_f1: unweighted mean per-label F1 over the dominant-act confusion
      - per_label: per-label P/R/F1
    """
    if macro:
        gold, pred = coarsen(gold, macro), coarsen(pred, macro)
    pairs: List[Tuple[str, Optional[str], Set[str]]] = []
    for g, p in zip(gold, pred):
        gl = dominant_act(g)
        if gl is None:
            continue
        pairs.append((gl, dominant_act(p), {s.act for s in p.spans}))
    n = len(pairs)
    if n == 0:
        return {"n": 0, "accuracy": 0.0, "lenient_hit_rate": 0.0, "macro_f1": 0.0, "per_label": {}}
    accuracy = sum(1 for gl, pl, _ in pairs if gl == pl) / n
    lenient = sum(1 for gl, _, pa in pairs if gl in pa) / n
    labels = {gl for gl, _, _ in pairs} | {pl for _, pl, _ in pairs if pl is not None}
    per_label: Dict[str, Dict[str, float]] = {}
    for lab in labels:
        tp = sum(1 for gl, pl, _ in pairs if gl == lab and pl == lab)
        per_label[lab] = _prf1(
            tp,
            sum(1 for _, pl, _ in pairs if pl == lab),
            sum(1 for gl, _, _ in pairs if gl == lab),
        )
    macro_f1 = sum(v["f1"] for v in per_label.values()) / len(per_label) if per_label else 0.0
    return {
        "n": n,
        "accuracy": accuracy,
        "lenient_hit_rate": lenient,
        "macro_f1": macro_f1,
        "per_label": per_label,
    }
