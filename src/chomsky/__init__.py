"""chomsky — span-level speech-act classification for PT-BR."""
from chomsky.schema import Span, Annotation
from chomsky.taxonomy import Taxonomy, load_taxonomy, bioes_labels, label_maps
from chomsky.resolve import resolve_quoted_spans
from chomsky.validator import validate
from chomsky.bioes import char_spans_to_bioes
from chomsky.agreement import span_agreement, gate
from chomsky.eval import span_prf1, per_act_f1

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
