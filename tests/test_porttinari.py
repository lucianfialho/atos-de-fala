from chomsky.train.porttinari import map_label, convert_rows, convert_csv
from chomsky.schema import Annotation, Span


def test_map_label_known_and_unknown():
    assert map_label("inform") == "informar"
    assert map_label("instruct") == "pedir"        # merged
    assert map_label("answer") == "informar"       # merged
    assert map_label("sympathyExpression") == "expressar_emocao"
    assert map_label("APOLOGY") == "desculpar"     # case-insensitive
    assert map_label("nao_existe") is None


def test_convert_rows_builds_whole_sentence_spans():
    rows = [
        {"sentence": "Bom dia.", "speech_act": "inform"},
        {"sentence": "Que horas sao?", "speech_act": "question"},
    ]
    anns, stats = convert_rows(rows)
    assert anns == [
        Annotation("Bom dia.", [Span(0, 8, "informar")]),
        Annotation("Que horas sao?", [Span(0, 14, "perguntar")]),
    ]
    assert stats["kept"] == 2
    assert stats["skipped_unmapped"] == 0
    assert stats["skipped_empty"] == 0


def test_convert_rows_skips_empty_and_unmapped():
    rows = [
        {"sentence": "   ", "speech_act": "inform"},      # empty after strip
        {"sentence": "Oi", "speech_act": "alien_act"},    # unmappable
        {"sentence": "Obrigado!", "speech_act": "thanking"},
    ]
    anns, stats = convert_rows(rows)
    assert anns == [Annotation("Obrigado!", [Span(0, 9, "agradecer")])]
    assert stats == {"kept": 1, "skipped_unmapped": 1, "skipped_empty": 1}


def test_convert_csv_roundtrips(tmp_path):
    p = tmp_path / "in.csv"
    p.write_text(
        "new_id,sentence,speech_act\n"
        "D1,Oi tudo bem,inform\n"
        "D2,Me ajuda?,request\n",
        encoding="utf-8",
    )
    anns, stats = convert_csv(str(p))
    assert [a.spans[0].act for a in anns] == ["informar", "pedir"]
    assert stats["kept"] == 2


def test_real_porttinari_corpus_fully_maps():
    # the vendored corpus must map with zero unmapped labels (map completeness)
    path = "raw/porttinari-base-speech-acts/data/porttinari-annotated-sample-paper-v1-20231211.csv"
    anns, stats = convert_csv(path)
    assert stats["skipped_unmapped"] == 0
    assert stats["kept"] == 4091
    # every produced annotation has exactly one whole-sentence span with a legal act
    legal = {
        "informar", "perguntar", "concordar", "discordar", "pedir", "sugerir",
        "oferecer", "prometer", "saudar", "agradecer", "desculpar", "despedir",
        "expressar_emocao",
    }
    assert all(len(a.spans) == 1 and a.spans[0].act in legal for a in anns)
