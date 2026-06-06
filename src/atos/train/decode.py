from typing import List, Optional, Tuple
from atos.schema import Span


def _split(tag: str) -> Tuple[str, Optional[str]]:
    if tag == "O":
        return "O", None
    prefix, _, act = tag.partition("-")
    return prefix, act


def bioes_tags_to_spans(
    offsets: List[Tuple[int, int]], tags: List[str]
) -> List[Span]:
    """Reconstruct char-offset spans from per-token BIOES tags (inverse of the tagger).

    Lenient: a new B/S or an act switch closes any open span; a dangling B/I is closed
    at the next O / special token / end of sequence. Special tokens (offset (0,0)) are
    skipped and close any open span.
    """
    spans: List[Span] = []
    open_start: Optional[int] = None
    open_end: int = 0
    open_act: Optional[str] = None

    def close():
        nonlocal open_start, open_end, open_act
        if open_start is not None and open_act is not None:
            spans.append(Span(open_start, open_end, open_act))
        open_start = None
        open_act = None

    for (s, e), tag in zip(offsets, tags):
        if s == e:  # special token / empty offset
            close()
            continue
        prefix, act = _split(tag)
        if prefix == "O":
            close()
        elif prefix == "S":
            close()
            spans.append(Span(s, e, act))
        elif prefix == "B":
            close()
            open_start, open_end, open_act = s, e, act
        elif prefix == "I":
            if open_act == act:
                open_end = e
            else:  # lenient: treat as a fresh open
                close()
                open_start, open_end, open_act = s, e, act
        elif prefix == "E":
            if open_act == act:
                open_end = e
                close()
            else:  # lenient: standalone E becomes a single-token span
                close()
                spans.append(Span(s, e, act))
    close()
    return spans
