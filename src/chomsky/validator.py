from typing import List
from chomsky.schema import Annotation
from chomsky.taxonomy import Taxonomy


def validate(ann: Annotation, taxonomy: Taxonomy) -> List[str]:
    errors: List[str] = []
    n = len(ann.text)
    legal = set(taxonomy.acts)

    for s in ann.spans:
        if not (0 <= s.start < s.end <= n):
            errors.append(
                f"span out of bounds: ({s.start}, {s.end}) for text length {n}"
            )
        if s.act not in legal:
            errors.append(f"illegal act: {s.act!r}")

    ordered = sorted(ann.spans, key=lambda s: (s.start, s.end))
    for prev, cur in zip(ordered, ordered[1:]):
        if cur.start < prev.end:
            errors.append(
                f"overlap between ({prev.start},{prev.end}) and ({cur.start},{cur.end})"
            )

    return errors
