from chomsky.train.data import load_jsonl
from chomsky.schema import Annotation, Span


def test_loads_annotations_skipping_blank_lines(tmp_path):
    p = tmp_path / "ds.jsonl"
    p.write_text(
        '{"text": "Oi!", "spans": [{"start": 0, "end": 3, "act": "saudar"}]}\n'
        "\n"
        '{"text": "Vem?", "spans": []}\n',
        encoding="utf-8",
    )
    data = load_jsonl(str(p))
    assert data == [
        Annotation("Oi!", [Span(0, 3, "saudar")]),
        Annotation("Vem?", []),
    ]


def test_empty_file_returns_empty_list(tmp_path):
    p = tmp_path / "empty.jsonl"
    p.write_text("", encoding="utf-8")
    assert load_jsonl(str(p)) == []
