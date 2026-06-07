from atos.gen.fapesp import parse_interview

HTML = (
    "<html><body>"
    "<p align='justify'><strong>[exibição de vídeo de abertura]</strong></p>"
    "<p align='justify'><strong>Paulo Markun:</strong> Boa noite! Voc&ecirc; pode revisar?</p>"
    "<p><strong><strong>Mano Brown</strong></strong>: Obrigado, boa noite.</p>"
    "<p>texto solto sem falante aqui.</p>"
    "</body></html>"
)


def test_parses_speaker_turns_and_decodes_entities():
    turns = parse_interview(HTML)
    assert len(turns) == 2  # stage direction + speaker-less line dropped
    assert turns[0] == {"speaker": "Paulo Markun", "text": "Boa noite! Você pode revisar?"}
    assert turns[1]["speaker"] == "Mano Brown"
    assert turns[1]["text"] == "Obrigado, boa noite."


def test_drops_stage_directions_and_unlabeled():
    turns = parse_interview("<p>[risos da plateia]</p><p>sem dois pontos aqui</p>")
    assert turns == []
