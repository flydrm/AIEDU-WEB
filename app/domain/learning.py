from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Concept:
    id: str
    name: str
    difficulty: int = 1  # 1-5


@dataclass
class MasteryRecord:
    concept_id: str
    success_rate: float = 0.5  # 0-1
    last_days_ago: int = 7


def schedule_score(m: MasteryRecord) -> float:
    # Higher when success is low or last seen long ago (spaced repetition)
    return (1.0 - m.success_rate) * 0.7 + min(m.last_days_ago / 14.0, 1.0) * 0.3

