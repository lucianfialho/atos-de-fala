"""Score a teacher's labels against the human gold set. Split out of gold.py to keep
each file under the size gate; re-exported from atos.gold for back-compat."""
from typing import Dict, List
from atos.schema import Annotation


def score_against(gold: List[Annotation], teacher: List[Annotation]) -> Dict:
    """Score a teacher's labels against the human gold, matched by identical text.

    Since both annotate the SAME string, exact span-F1 (start,end,act) is fair here —
    this measures how good the teacher (DeepSeek/Kimi/MiniMax) actually is. Returns
    overall + per-act F1 plus how many gold texts were matched/missing in the teacher set.
    """
    from atos.eval import span_prf1, per_act_f1

    by_text = {a.text: a for a in teacher}
    g: List[Annotation] = []
    p: List[Annotation] = []
    missing = 0
    for ga in gold:
        ta = by_text.get(ga.text)
        if ta is None:
            missing += 1
            continue
        g.append(ga)
        p.append(ta)
    return {
        "overall": span_prf1(g, p),
        "per_act": per_act_f1(g, p),
        "matched": len(g),
        "missing": missing,
    }
