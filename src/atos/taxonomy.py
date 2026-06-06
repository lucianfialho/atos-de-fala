from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import yaml


@dataclass
class Taxonomy:
    acts: List[str]
    definitions: Dict[str, str]
    macro: Dict[str, str] = field(default_factory=dict)  # act -> macro-class (Searle); optional


def load_taxonomy(path: str) -> Taxonomy:
    with open(path, "r", encoding="utf-8") as f:
        obj = yaml.safe_load(f)
    acts = [a["name"] for a in obj["acts"]]
    definitions = {a["name"]: a.get("definition", "") for a in obj["acts"]}
    macro = {a["name"]: a["macro"] for a in obj["acts"] if a.get("macro")}
    return Taxonomy(acts=acts, definitions=definitions, macro=macro)


def bioes_labels(acts: List[str]) -> List[str]:
    labels = ["O"]
    for act in acts:
        labels += [f"B-{act}", f"I-{act}", f"E-{act}", f"S-{act}"]
    return labels


def label_maps(labels: List[str]) -> Tuple[Dict[str, int], Dict[int, str]]:
    label2id = {lbl: i for i, lbl in enumerate(labels)}
    id2label = {i: lbl for lbl, i in label2id.items()}
    return label2id, id2label
