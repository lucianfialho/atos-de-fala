from atos.collect.export_spans import build_annotations, gold_to_annotations


def _row(context, start, end, act, verdict="confirmed"):
    return {"context": context, "char_start": start, "char_end": end, "act": act, "verdict": verdict}


def test_groups_rows_by_context_into_one_annotation_per_turn():
    rows = [
        _row("Bom dia! Tudo certo?", 0, 8, "saudar"),
        _row("Bom dia! Tudo certo?", 9, 20, "perguntar"),
    ]
    anns = build_annotations(rows)
    assert len(anns) == 1
    a = anns[0]
    assert a.text == "Bom dia! Tudo certo?"
    assert [(s.start, s.end, s.act) for s in a.spans] == [(0, 8, "saudar"), (9, 20, "perguntar")]


def test_majority_vote_resolves_conflicting_acts_on_same_span():
    rows = [
        _row("Você pode revisar?", 0, 18, "pedir"),
        _row("Você pode revisar?", 0, 18, "pedir"),
        _row("Você pode revisar?", 0, 18, "perguntar"),
    ]
    anns = build_annotations(rows)
    assert len(anns[0].spans) == 1
    assert anns[0].spans[0].act == "pedir"  # 2 vs 1


def test_min_votes_filters_thinly_annotated_spans():
    rows = [_row("Oi.", 0, 3, "saudar")]
    assert build_annotations(rows, min_votes=1)  # kept
    assert build_annotations(rows, min_votes=2) == []  # dropped


def test_overlapping_spans_are_dropped_keeping_first_by_start():
    rows = [
        _row("Bom dia pessoal", 0, 7, "saudar"),
        _row("Bom dia pessoal", 4, 15, "informar"),  # overlaps [0,7)
    ]
    anns = build_annotations(rows)
    assert [(s.start, s.end) for s in anns[0].spans] == [(0, 7)]


def test_spans_sorted_by_start():
    rows = [
        _row("a b c", 4, 5, "pedir"),
        _row("a b c", 0, 1, "saudar"),
    ]
    anns = build_annotations(rows)
    assert [s.start for s in anns[0].spans] == [0, 4]


def _grow(item_id, text, start, end, act):
    return {"item_id": item_id, "text": text, "char_start": start, "char_end": end, "act": act}


def test_gold_to_annotations_groups_by_item_and_sorts_spans():
    rows = [
        _grow(1, "Bom dia! Vai?", 9, 13, "perguntar"),
        _grow(1, "Bom dia! Vai?", 0, 8, "saudar"),
        _grow(2, "Obrigado.", 0, 9, "agradecer"),
    ]
    anns = gold_to_annotations(rows)
    assert len(anns) == 2
    a1 = next(a for a in anns if a.text == "Bom dia! Vai?")
    assert [(s.start, s.end, s.act) for s in a1.spans] == [(0, 8, "saudar"), (9, 13, "perguntar")]


def test_gold_to_annotations_empty():
    assert gold_to_annotations([]) == []
