import pytest
from atos.gen.prompts import (
    parse_llm_json,
    build_generation_prompt,
    build_annotation_prompt,
)


def test_parses_bare_json():
    raw = '{"text": "Oi!", "spans": [{"quote": "Oi!", "act": "saudar"}]}'
    obj = parse_llm_json(raw)
    assert obj["text"] == "Oi!"
    assert obj["spans"] == [{"quote": "Oi!", "act": "saudar"}]


def test_parses_json_inside_markdown_fence():
    raw = 'Claro! Aqui:\n```json\n{"text": "Oi!", "spans": []}\n```\nEspero ajudar.'
    obj = parse_llm_json(raw)
    assert obj["text"] == "Oi!"
    assert obj["spans"] == []


def test_parses_json_with_surrounding_prose():
    raw = 'Resposta: {"text": "Vem?", "spans": [{"quote": "Vem?", "act": "pedir"}]} fim'
    obj = parse_llm_json(raw)
    assert obj["text"] == "Vem?"


def test_raises_on_no_json():
    with pytest.raises(ValueError):
        parse_llm_json("desculpe, nao consigo responder")


def test_raises_on_missing_keys():
    with pytest.raises(ValueError):
        parse_llm_json('{"text": "Oi"}')  # no spans


def test_build_generation_prompt_includes_rubric_and_count():
    msgs = build_generation_prompt("RUBRICA_AQUI", 5)
    assert isinstance(msgs, list) and msgs[-1]["role"] == "user"
    joined = " ".join(m["content"] for m in msgs)
    assert "RUBRICA_AQUI" in joined
    assert "5" in joined


def test_build_annotation_prompt_includes_text():
    msgs = build_annotation_prompt("RUBRICA", "Bom dia!")
    joined = " ".join(m["content"] for m in msgs)
    assert "RUBRICA" in joined
    assert "Bom dia!" in joined


def test_build_adjudication_prompt_includes_problems_and_text():
    from atos.gen.prompts import build_adjudication_prompt
    msgs = build_adjudication_prompt("RUBRICA", "Bom dia!", ["illegal act: 'xingar'"])
    joined = " ".join(m["content"] for m in msgs)
    assert "RUBRICA" in joined
    assert "Bom dia!" in joined
    assert "xingar" in joined


def test_build_generation_prompt_focus_acts_listed():
    msgs = build_generation_prompt("RUBRICA", 1, focus_acts=["oferecer", "desculpar"])
    joined = " ".join(m["content"] for m in msgs)
    assert "oferecer" in joined and "desculpar" in joined


def test_build_generation_prompt_no_focus_omits_priority_note():
    msgs = build_generation_prompt("RUBRICA", 1)
    joined = " ".join(m["content"] for m in msgs)
    assert "sub-representados" not in joined


def test_build_generation_prompt_avoid_acts_listed():
    msgs = build_generation_prompt("RUBRICA", 1, avoid_acts=["saudar", "agradecer"])
    joined = " ".join(m["content"] for m in msgs)
    assert "saudar" in joined and "agradecer" in joined and "EVITE" in joined


def test_build_generation_prompt_no_avoid_omits_avoid_note():
    msgs = build_generation_prompt("RUBRICA", 1)
    joined = " ".join(m["content"] for m in msgs)
    assert "EVITE" not in joined
