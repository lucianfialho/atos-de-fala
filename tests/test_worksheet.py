from atos.collect.worksheet import to_worksheet, from_worksheet
from atos.taxonomy import load_taxonomy

TAX = load_taxonomy("config/taxonomy.yaml")


def test_to_worksheet_slices_quotes_and_sets_domain():
    silver = [{"text": "Obrigado pela ajuda!", "spans": [{"start": 0, "end": 8, "act": "agradecer"}]}]
    rows = to_worksheet(silver, domain="sac")
    assert rows == [{
        "domain": "sac", "text": "Obrigado pela ajuda!", "reviewed": False,
        "spans": [{"quote": "Obrigado", "act": "agradecer"}], "notes": "",
    }]


def test_to_worksheet_falls_back_to_record_domain_then_geral():
    silver = [
        {"text": "Oi.", "spans": [], "domain": "review"},
        {"text": "Tchau.", "spans": []},
    ]
    rows = to_worksheet(silver)  # no override
    assert rows[0]["domain"] == "review"
    assert rows[1]["domain"] == "geral"


def test_harvest_keeps_only_reviewed_and_resolves_offsets():
    ws = [
        {"domain": "sac", "text": "Bom dia, posso ajudar?", "reviewed": True,
         "spans": [{"quote": "Bom dia", "act": "saudar"},
                   {"quote": "posso ajudar?", "act": "oferecer"}]},
        {"domain": "sac", "text": "nao revisado", "reviewed": False, "spans": []},
    ]
    gold, stats = from_worksheet(ws, TAX)
    assert stats == {"kept": 1, "skipped_unreviewed": 1, "rejected": 0}
    assert gold[0]["domain"] == "sac"
    assert gold[0]["spans"][0] == {"start": 0, "end": 7, "act": "saudar"}
    assert gold[0]["spans"][1]["act"] == "oferecer"


def test_harvest_rejects_unresolvable_or_invalid():
    ws = [
        {"domain": "x", "text": "Oi.", "reviewed": True,
         "spans": [{"quote": "nao existe no texto", "act": "saudar"}]},
        {"domain": "x", "text": "Oi.", "reviewed": True,
         "spans": [{"quote": "Oi", "act": "ato_inexistente"}]},
    ]
    gold, stats = from_worksheet(ws, TAX)
    assert gold == []
    assert stats["rejected"] == 2
    assert stats["kept"] == 0
