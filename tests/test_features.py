from chomsky.train.features import align_labels


def test_special_tokens_become_ignore_index():
    tags = ["O", "B-saudar", "E-saudar", "O"]
    special = [1, 0, 0, 1]  # first and last are special ([CLS]/[SEP])
    label2id = {"O": 0, "B-saudar": 1, "I-saudar": 2, "E-saudar": 3, "S-saudar": 4}
    assert align_labels(tags, special, label2id) == [-100, 1, 3, -100]


def test_all_real_tokens_map_to_ids():
    tags = ["S-pedir", "O"]
    special = [0, 0]
    label2id = {"O": 0, "B-pedir": 1, "I-pedir": 2, "E-pedir": 3, "S-pedir": 4}
    assert align_labels(tags, special, label2id) == [4, 0]
