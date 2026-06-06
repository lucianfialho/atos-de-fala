from dataclasses import dataclass
from typing import Callable, Dict, List, Optional
from atos.schema import Annotation
from atos.taxonomy import Taxonomy
from atos.resolve import resolve_quoted_spans
from atos.validator import validate
from atos.agreement import span_agreement

Items = List[Dict]
Annotator = Callable[[str], Items]
Adjudicator = Callable[[str, List[str]], Items]


@dataclass
class ExampleResult:
    annotation: Optional[Annotation]
    status: str  # "accepted" | "adjudicated" | "rejected"
    reason: str
    agreement: Optional[float]


def _resolve_and_validate(text: str, items: Items, taxonomy: Taxonomy):
    ann, errs = resolve_quoted_spans(text, items)
    errs = list(errs) + validate(ann, taxonomy)
    return ann, errs


def process_example(
    text: str,
    items_primary: Items,
    *,
    taxonomy: Taxonomy,
    cross_annotate: Optional[Annotator] = None,
    adjudicate: Optional[Adjudicator] = None,
    threshold: float = 0.8,
) -> ExampleResult:
    """Run one example through the teacher-mixture pipeline (pure; inject callables).

    Flow: resolve+validate primary -> (if invalid) adjudicate or reject ->
    (if cross_annotate) measure agreement -> keep if >= threshold else adjudicate
    or reject. Returns the accepted/adjudicated Annotation or a rejection.
    """
    ann, errs = _resolve_and_validate(text, items_primary, taxonomy)
    if errs:
        if adjudicate is None:
            return ExampleResult(None, "rejected", f"invalid primary: {errs}", None)
        fixed, ferrs = _resolve_and_validate(text, adjudicate(text, errs), taxonomy)
        if ferrs:
            return ExampleResult(None, "rejected", f"invalid after adjudication: {ferrs}", None)
        return ExampleResult(fixed, "adjudicated", "fixed invalid primary", None)

    if cross_annotate is None:
        return ExampleResult(ann, "accepted", "primary valid, no cross-check", None)

    ann_b, _ = resolve_quoted_spans(text, cross_annotate(text))
    score = span_agreement(ann, ann_b)
    if score >= threshold:
        return ExampleResult(ann, "accepted", "high agreement", score)
    if adjudicate is None:
        return ExampleResult(None, "rejected", f"low agreement {score:.3f}", score)
    fixed, ferrs = _resolve_and_validate(text, adjudicate(text, [f"agreement {score:.3f}"]), taxonomy)
    if ferrs:
        return ExampleResult(None, "rejected", f"invalid adjudication: {ferrs}", score)
    return ExampleResult(fixed, "adjudicated", "low agreement adjudicated", score)
