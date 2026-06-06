"""atos — span-level speech-act classification for PT-BR."""
from atos.schema import Span, Annotation
from atos.taxonomy import Taxonomy, load_taxonomy, bioes_labels, label_maps
from atos.resolve import resolve_quoted_spans
from atos.validator import validate
from atos.bioes import char_spans_to_bioes
from atos.agreement import span_agreement, gate
from atos.eval import span_prf1, per_act_f1

__all__ = [
    "Span",
    "Annotation",
    "Taxonomy",
    "load_taxonomy",
    "bioes_labels",
    "label_maps",
    "resolve_quoted_spans",
    "validate",
    "char_spans_to_bioes",
    "span_agreement",
    "gate",
    "span_prf1",
    "per_act_f1",
]
