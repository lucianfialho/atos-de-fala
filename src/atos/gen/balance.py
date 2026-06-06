"""Per-act balancing for synthetic generation.

Natural / unsteered generation skews toward common acts (e.g. `informar`), starving
rare ones (`oferecer`, `desculpar`, `despedir`). These pure helpers let the CLI count
acts already collected and pick the most under-represented ones to FOCUS the next
generation prompt — so the dataset approaches an even per-act distribution.
"""
from collections import Counter
from typing import Dict, List
from atos.schema import Annotation


def act_counts(anns: List[Annotation]) -> Dict[str, int]:
    """Count spans per act across a list of annotations."""
    c: Counter = Counter()
    for ann in anns:
        for span in ann.spans:
            c[span.act] += 1
    return dict(c)


def under_target_acts(
    counts: Dict[str, int], acts: List[str], target: int, k: int = 3
) -> List[str]:
    """Return up to k acts whose count is below `target`, lowest count first.

    Ties broken by the order of `acts` (stable, deterministic). Returns [] when every
    act has reached the target — at which point generation no longer needs steering.
    """
    below = [a for a in acts if counts.get(a, 0) < target]
    below.sort(key=lambda a: (counts.get(a, 0), acts.index(a)))
    return below[:k]


def over_target_acts(
    counts: Dict[str, int], acts: List[str], target: int, k: int = 3
) -> List[str]:
    """Return up to k acts already AT/OVER `target`, highest count first (negative steering).

    These are the over-represented acts (typically conversational scaffolding —
    saudar/agradecer/pedir — which the teacher emits in every dialogue). Feeding them
    to the generation prompt as an "avoid" list keeps the teacher from inflating them
    further once they've hit quota, so the per-act distribution evens out. Ties broken
    by `acts` order (stable). Returns [] while every act is still under target.
    """
    over = [a for a in acts if counts.get(a, 0) >= target]
    over.sort(key=lambda a: (-counts.get(a, 0), acts.index(a)))
    return over[:k]
