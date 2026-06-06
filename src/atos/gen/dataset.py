import json
import os
from typing import List, Set
from atos.schema import Annotation


def append_annotation(path: str, ann: Annotation) -> None:
    """Append one Annotation as a JSON line and flush immediately (crash-safe resume)."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(ann.to_json() + "\n")
        f.flush()
        os.fsync(f.fileno())


def load_done_texts(path: str) -> Set[str]:
    """Return the set of texts already written, so generation can resume w/o dupes."""
    if not os.path.exists(path):
        return set()
    done: Set[str] = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            done.add(json.loads(line)["text"])
    return done


def load_done_annotations(path: str) -> List[Annotation]:
    """Return the annotations already written, for resume + per-act balancing."""
    if not os.path.exists(path):
        return []
    out: List[Annotation] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(Annotation.from_json(line))
    return out
