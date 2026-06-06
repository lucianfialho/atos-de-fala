"""Turn human span annotations (span_annotation rows) into training examples.

Each row is one human-confirmed/corrected/added span inside a transcript turn
(`context`). We group rows by turn, majority-vote the act per (start, end) span,
drop spans below `min_votes`, drop overlaps (BIOES needs non-overlapping spans),
and emit one Annotation per turn — the same format the trainer consumes.

Pure (no DB) so it stays unit-testable; the CLI feeds it rows from db.py.
"""
from collections import Counter, defaultdict
from typing import Dict, List

from atos.schema import Annotation, Span


def build_annotations(rows: List[Dict], min_votes: int = 1) -> List[Annotation]:
    # context -> (start, end) -> [act, ...]
    by_ctx: Dict[str, Dict[tuple, List[str]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_ctx[r["context"]][(r["char_start"], r["char_end"])].append(r["act"])

    annotations: List[Annotation] = []
    for context, span_map in by_ctx.items():
        # majority act per span position, gated by how many humans marked it
        chosen = []
        for (start, end), acts in span_map.items():
            if len(acts) < min_votes:
                continue
            act = Counter(acts).most_common(1)[0][0]
            chosen.append((start, end, act))

        # non-overlapping: sort by start (longer first on ties), greedily keep
        chosen.sort(key=lambda t: (t[0], -(t[1] - t[0])))
        spans: List[Span] = []
        last_end = -1
        for start, end, act in chosen:
            if start < last_end:
                continue  # overlaps a kept span
            spans.append(Span(start, end, act))
            last_end = end

        if spans:
            annotations.append(Annotation(context, spans))

    return annotations
