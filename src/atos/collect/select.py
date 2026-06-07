"""Turn AI-annotated texts (and honeypot gold) into item rows for the collection DB.

A normal item carries the model's spans/acts for players to judge. A honeypot item is a
high-agreement gold annotation whose span.act IS the known answer used to score voter
reliability — so each honeypot span also emits `gold_act`. Pure transform: no DB here."""
from typing import Dict, List
from atos.schema import Annotation


def _item_row(ann: Annotation, is_honeypot: bool, source: str) -> Dict:
    spans: List[Dict] = []
    for order, s in enumerate(ann.spans):
        span = {"char_start": s.start, "char_end": s.end, "ai_act": s.act, "display_order": order}
        if is_honeypot:
            span["gold_act"] = s.act
        spans.append(span)
    return {"text": ann.text, "source": source, "is_honeypot": is_honeypot, "spans": spans}


def build_items(annotations: List[Annotation], honeypots: List[Annotation],
                source: str = "synthetic") -> List[Dict]:
    """`annotations`: model output to be judged. `honeypots`: gold whose acts are known.
    `source` tags the domain (review/sac/entrevista/...) so collected gold can be sliced
    per-domain later (atos.train.multidomain). Honeypots keep their own 'honeypot' source."""
    return ([_item_row(a, False, source) for a in annotations]
            + [_item_row(h, True, "honeypot") for h in honeypots])
