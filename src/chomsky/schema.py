from dataclasses import dataclass
from typing import List
import json


@dataclass(frozen=True)
class Span:
    start: int  # char offset, inclusive
    end: int    # char offset, exclusive
    act: str    # speech-act label


@dataclass
class Annotation:
    text: str
    spans: List[Span]

    def to_json(self) -> str:
        return json.dumps(
            {
                "text": self.text,
                "spans": [
                    {"start": s.start, "end": s.end, "act": s.act}
                    for s in self.spans
                ],
            },
            ensure_ascii=False,
        )

    @staticmethod
    def from_json(s: str) -> "Annotation":
        obj = json.loads(s)
        return Annotation(
            text=obj["text"],
            spans=[Span(d["start"], d["end"], d["act"]) for d in obj["spans"]],
        )
