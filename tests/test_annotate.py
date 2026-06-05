import json
from chomsky.annotate import read_rows, write_rows


def test_read_rows_missing_file(tmp_path):
    assert read_rows(str(tmp_path / "nope.jsonl")) == []


def test_write_then_read_roundtrip_and_sanitizes(tmp_path):
    p = str(tmp_path / "w.jsonl")
    rows = [
        {"text": "Oi! Vem?", "spans": [
            {"quote": "Oi!", "act": "saudar", "_start": 0},   # _start must be dropped
            {"quote": "Vem?", "act": "pedir", "_start": 4}]},
        {"text": "Nada aqui", "spans": []},
    ]
    write_rows(p, rows)
    # on disk: only quote+act per span
    lines = [json.loads(ln) for ln in open(p, encoding="utf-8") if ln.strip()]
    assert lines[0]["spans"] == [
        {"quote": "Oi!", "act": "saudar"},
        {"quote": "Vem?", "act": "pedir"},
    ]
    assert lines[1] == {"text": "Nada aqui", "spans": []}
    # read back
    back = read_rows(p)
    assert back[0]["text"] == "Oi! Vem?"
    assert back[1]["spans"] == []


def test_html_and_acts_wired():
    import chomsky.annotate as A
    assert "<!doctype html>" in A._HTML.lower()
    assert "/api/save" in A._HTML and "/api/state" in A._HTML
