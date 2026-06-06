from atos.gen.pipeline import process_example, ExampleResult
from atos.schema import Span
from atos.taxonomy import Taxonomy

TAX = Taxonomy(
    acts=["saudar", "pedir", "sugerir"],
    definitions={"saudar": "", "pedir": "", "sugerir": ""},
)
TEXT = "Bom dia! Pode vir?"
GOOD = [{"quote": "Bom dia!", "act": "saudar"}, {"quote": "Pode vir?", "act": "pedir"}]


def test_valid_primary_no_crosscheck_is_accepted():
    res = process_example(TEXT, GOOD, taxonomy=TAX)
    assert res.status == "accepted"
    assert res.annotation.spans == [Span(0, 8, "saudar"), Span(9, 18, "pedir")]
    assert res.agreement is None


def test_invalid_primary_without_adjudicator_is_rejected():
    bad = [{"quote": "Bom dia!", "act": "xingar"}]  # illegal act
    res = process_example(TEXT, bad, taxonomy=TAX)
    assert res.status == "rejected"
    assert res.annotation is None


def test_invalid_primary_is_fixed_by_adjudicator():
    bad = [{"quote": "naoexiste", "act": "saudar"}]  # quote not in text

    def adjudicate(text, problems):
        return GOOD

    res = process_example(TEXT, bad, taxonomy=TAX, adjudicate=adjudicate)
    assert res.status == "adjudicated"
    assert res.annotation.spans[0] == Span(0, 8, "saudar")


def test_high_agreement_crosscheck_accepts_primary():
    def cross(text):
        return GOOD  # identical -> agreement 1.0

    res = process_example(TEXT, GOOD, taxonomy=TAX, cross_annotate=cross, threshold=0.8)
    assert res.status == "accepted"
    assert res.agreement == 1.0


def test_low_agreement_routes_to_adjudicator():
    def cross(text):
        return [{"quote": "Pode vir?", "act": "sugerir"}]  # disagrees

    def adjudicate(text, problems):
        return GOOD

    res = process_example(
        TEXT, GOOD, taxonomy=TAX, cross_annotate=cross, adjudicate=adjudicate, threshold=0.9
    )
    assert res.status == "adjudicated"
    assert res.agreement is not None and res.agreement < 0.9


def test_low_agreement_without_adjudicator_is_rejected():
    def cross(text):
        return [{"quote": "Pode vir?", "act": "sugerir"}]

    res = process_example(
        TEXT, GOOD, taxonomy=TAX, cross_annotate=cross, threshold=0.9
    )
    assert res.status == "rejected"
    assert res.agreement is not None and res.agreement < 0.9
