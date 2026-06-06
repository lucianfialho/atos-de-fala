from atos.collect.select import build_items
from atos.schema import Annotation, Span


def test_build_items_maps_annotation_to_item_with_spans():
    anns = [Annotation("Oi! Vai?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")])]
    rows = build_items(anns, [])
    assert len(rows) == 1
    row = rows[0]
    assert row["text"] == "Oi! Vai?" and row["is_honeypot"] is False and row["source"] == "synthetic"
    assert row["spans"][0] == {"char_start": 0, "char_end": 3, "ai_act": "saudar", "display_order": 0}
    assert "gold_act" not in row["spans"][0]


def test_build_items_marks_honeypot_spans_with_gold_act():
    hp = [Annotation("Bom dia!", [Span(0, 8, "saudar")])]
    rows = build_items([], hp)
    assert rows[0]["is_honeypot"] is True
    assert rows[0]["spans"][0]["gold_act"] == "saudar"
