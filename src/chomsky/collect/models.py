from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Vote:
    span_id: int
    verdict: str                  # "agree" | "disagree"
    corrected_act: Optional[str]  # the act the voter prefers when disagreeing
    reliability: float            # voter weight, 0..1 (from honeypots)


@dataclass(frozen=True)
class SpanResolution:
    span_id: int
    act: Optional[str]            # winning act; None if no act reached consensus
    agreement: float              # weighted share of the winning act, 0..1
    is_gold: bool                 # agreement >= threshold
