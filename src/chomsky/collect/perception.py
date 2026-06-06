"""The research output: do different demographic groups perceive different acts on the
SAME contested span? `records` are per-vote chosen acts tagged with a demographic axis
value (built from votes + participant rows). Pure functions over plain dicts."""
from typing import Dict, List


def act_distribution_by_group(records: List[Dict], axis: str) -> Dict[str, Dict[str, int]]:
    """records: [{'act': str, <axis>: group_value}]. Returns group -> {act: count}."""
    out: Dict[str, Dict[str, int]] = {}
    for r in records:
        group, act = r[axis], r["act"]
        bucket = out.setdefault(group, {})
        bucket[act] = bucket.get(act, 0) + 1
    return out


def groups_disagree(dist: Dict[str, Dict[str, int]]) -> bool:
    """True if the most-voted act differs across groups — a perception split worth a look."""
    modes = set()
    for counts in dist.values():
        if counts:
            modes.add(max(counts.items(), key=lambda kv: kv[1])[0])
    return len(modes) > 1
