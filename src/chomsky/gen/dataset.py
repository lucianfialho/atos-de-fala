import json
import os
from typing import Set
from chomsky.schema import Annotation


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
