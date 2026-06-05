from chomsky.taxonomy import load_taxonomy, bioes_labels, label_maps


def test_load_taxonomy_reads_acts_and_definitions(tmp_path):
    p = tmp_path / "tax.yaml"
    p.write_text(
        "acts:\n"
        "  - name: afirmar\n"
        "    definition: declarar algo como verdadeiro\n"
        "  - name: perguntar\n"
        "    definition: solicitar informacao\n",
        encoding="utf-8",
    )
    tax = load_taxonomy(str(p))
    assert tax.acts == ["afirmar", "perguntar"]
    assert tax.definitions["afirmar"] == "declarar algo como verdadeiro"


def test_bioes_labels_order_is_O_then_BIES_per_act():
    labels = bioes_labels(["afirmar", "perguntar"])
    assert labels == [
        "O",
        "B-afirmar", "I-afirmar", "E-afirmar", "S-afirmar",
        "B-perguntar", "I-perguntar", "E-perguntar", "S-perguntar",
    ]


def test_label_maps_are_inverse_and_contiguous():
    labels = bioes_labels(["afirmar"])
    label2id, id2label = label_maps(labels)
    assert label2id["O"] == 0
    assert id2label[0] == "O"
    assert sorted(label2id.values()) == list(range(len(labels)))
    assert all(id2label[label2id[l]] == l for l in labels)


def test_shipped_config_yields_49_bioes_labels():
    tax = load_taxonomy("config/taxonomy.yaml")
    assert len(tax.acts) == 12
    assert len(bioes_labels(tax.acts)) == 49  # 4 * 12 + 1
