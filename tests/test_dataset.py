from chomsky.gen.dataset import append_annotation, load_done_texts
from chomsky.schema import Annotation, Span


def test_load_done_texts_missing_file_is_empty(tmp_path):
    assert load_done_texts(str(tmp_path / "nope.jsonl")) == set()


def test_append_then_load_roundtrip(tmp_path):
    p = str(tmp_path / "out.jsonl")
    append_annotation(p, Annotation("Oi!", [Span(0, 3, "saudar")]))
    append_annotation(p, Annotation("Vem?", [Span(0, 4, "pedir")]))
    assert load_done_texts(p) == {"Oi!", "Vem?"}


def test_each_record_is_one_json_line(tmp_path):
    p = str(tmp_path / "out.jsonl")
    append_annotation(p, Annotation("Oi!", [Span(0, 3, "saudar")]))
    append_annotation(p, Annotation("Vem?", []))
    with open(p, encoding="utf-8") as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip()]
    assert len(lines) == 2
    import json
    assert json.loads(lines[0])["text"] == "Oi!"
