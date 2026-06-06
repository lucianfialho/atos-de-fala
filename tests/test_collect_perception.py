from chomsky.collect.perception import act_distribution_by_group, groups_disagree


def test_distribution_counts_acts_per_group():
    records = [
        {"act": "pedir", "region": "SP"},
        {"act": "pedir", "region": "SP"},
        {"act": "sugerir", "region": "BA"},
    ]
    dist = act_distribution_by_group(records, "region")
    assert dist == {"SP": {"pedir": 2}, "BA": {"sugerir": 1}}


def test_groups_disagree_true_when_modal_act_differs():
    dist = {"SP": {"pedir": 5, "sugerir": 1}, "BA": {"sugerir": 4, "pedir": 1}}
    assert groups_disagree(dist) is True


def test_groups_disagree_false_when_modal_act_matches():
    dist = {"SP": {"pedir": 5}, "BA": {"pedir": 3, "sugerir": 1}}
    assert groups_disagree(dist) is False
