from typing import List
from chomsky.schema import Annotation


def load_jsonl(path: str) -> List[Annotation]:
    """Load a dataset of char-offset annotations (one JSON object per line)."""
    out: List[Annotation] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(Annotation.from_json(line))
    return out
