from atos.schema import Span, Annotation


def test_span_is_frozen_and_holds_offsets():
    s = Span(start=0, end=8, act="saudar")
    assert (s.start, s.end, s.act) == (0, 8, "saudar")


def test_annotation_roundtrips_through_json():
    ann = Annotation(
        text="Bom dia! Pode enviar?",
        spans=[Span(0, 8, "saudar"), Span(9, 21, "pedir")],
    )
    restored = Annotation.from_json(ann.to_json())
    assert restored == ann


def test_from_json_parses_expected_shape():
    raw = '{"text": "Oi", "spans": [{"start": 0, "end": 2, "act": "saudar"}]}'
    ann = Annotation.from_json(raw)
    assert ann.text == "Oi"
    assert ann.spans == [Span(0, 2, "saudar")]
