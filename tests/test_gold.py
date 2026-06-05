from chomsky.gold import make_template, sample_texts, compile_gold, score_against
from chomsky.schema import Annotation, Span
from chomsky.taxonomy import Taxonomy

TAX = Taxonomy(
    acts=["informar", "pedir", "saudar"],
    definitions={"informar": "", "pedir": "", "saudar": ""},
)


def test_make_template_blanks_spans():
    assert make_template(["Oi", "Vem?"]) == [
        {"text": "Oi", "spans": []},
        {"text": "Vem?", "spans": []},
    ]


def test_sample_texts_spreads_evenly(tmp_path):
    p = tmp_path / "ds.jsonl"
    p.write_text(
        "\n".join(
            f'{{"text": "t{i}", "spans": []}}' for i in range(10)
        ),
        encoding="utf-8",
    )
    out = sample_texts(str(p), 3)
    assert out == ["t0", "t3", "t6"]  # stride = 10/3


def test_sample_texts_returns_all_when_n_exceeds(tmp_path):
    p = tmp_path / "ds.jsonl"
    p.write_text('{"text": "a", "spans": []}\n{"text": "b", "spans": []}\n', encoding="utf-8")
    assert sample_texts(str(p), 10) == ["a", "b"]


def test_compile_gold_resolves_valid_rows():
    rows = [
        {"text": "Oi! Pode vir?", "spans": [
            {"quote": "Oi!", "act": "saudar"},
            {"quote": "Pode vir?", "act": "pedir"}]},
    ]
    anns, errors = compile_gold(rows, TAX)
    assert errors == []
    assert anns == [Annotation("Oi! Pode vir?", [Span(0, 3, "saudar"), Span(4, 13, "pedir")])]


def test_compile_gold_reports_bad_quote_and_illegal_act():
    rows = [
        {"text": "Oi", "spans": [{"quote": "naoexiste", "act": "saudar"}]},     # bad quote
        {"text": "Oi", "spans": [{"quote": "Oi", "act": "xingar"}]},            # illegal act
        {"text": "Bom dia", "spans": [{"quote": "Bom dia", "act": "saudar"}]},  # ok
    ]
    anns, errors = compile_gold(rows, TAX)
    assert len(anns) == 1
    assert len(errors) == 2
    assert "line 1" in errors[0] and "line 2" in errors[1]


def test_compile_gold_allows_empty_spans_as_no_acts():
    anns, errors = compile_gold([{"text": "abc", "spans": []}], TAX)
    assert errors == []
    assert anns == [Annotation("abc", [])]


def test_score_against_matches_by_text_and_scores():
    gold = [
        Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "pedir")]),
        Annotation("So no gold", [Span(0, 2, "saudar")]),  # missing in teacher
    ]
    teacher = [
        Annotation("Oi! Vem?", [Span(0, 3, "saudar"), Span(4, 8, "informar")]),  # 1 right, 1 wrong
    ]
    rep = score_against(gold, teacher)
    assert rep["matched"] == 1
    assert rep["missing"] == 1
    assert rep["overall"]["f1"] == 0.5            # 1 of 2 spans match on the matched text
    assert rep["per_act"]["saudar"]["f1"] == 1.0
    assert rep["per_act"]["pedir"]["f1"] == 0.0
