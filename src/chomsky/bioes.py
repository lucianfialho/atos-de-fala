from typing import List, Tuple
from chomsky.schema import Span


def _token_in_span(tok: Tuple[int, int], span: Span) -> bool:
    start, end = tok
    if start == end:  # special token / empty offset
        return False
    return start >= span.start and end <= span.end


def char_spans_to_bioes(
    spans: List[Span], offsets: List[Tuple[int, int]]
) -> List[str]:
    # token index -> span index (or -1)
    owner = [-1] * len(offsets)
    for si, span in enumerate(spans):
        member = [ti for ti, tok in enumerate(offsets) if _token_in_span(tok, span)]
        for ti in member:
            owner[ti] = si

    tags = ["O"] * len(offsets)
    for si, span in enumerate(spans):
        member = [ti for ti in range(len(offsets)) if owner[ti] == si]
        if not member:
            continue
        if len(member) == 1:
            tags[member[0]] = f"S-{span.act}"
        else:
            tags[member[0]] = f"B-{span.act}"
            tags[member[-1]] = f"E-{span.act}"
            for ti in member[1:-1]:
                tags[ti] = f"I-{span.act}"
    return tags
