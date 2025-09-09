from __future__ import annotations

from typing import Dict, List
from app.domain.learning import MasteryRecord
from app.presentation.api.metrics import record_learning_event


class MasteryService:
    def __init__(self) -> None:
        self._store: Dict[str, MasteryRecord] = {}

    def get_all(self) -> List[MasteryRecord]:
        return list(self._store.values())

    def clear(self) -> None:
        self._store.clear()

    def update(self, concept_id: str, success: bool) -> MasteryRecord:
        rec = self._store.get(concept_id) or MasteryRecord(concept_id=concept_id, success_rate=0.5, last_days_ago=7)
        # exponential moving average toward 1.0 or 0.0
        alpha = 0.3
        target = 1.0 if success else 0.0
        rec.success_rate = (1 - alpha) * rec.success_rate + alpha * target
        rec.last_days_ago = 0
        self._store[concept_id] = rec
        record_learning_event("complete_success" if success else "complete_fail")
        return rec

    def elapse_days(self, days: int = 1) -> None:
        for r in self._store.values():
            r.last_days_ago += max(0, days)

    def summary(self) -> Dict[str, float]:
        if not self._store:
            return {"count": 0, "avg_success": 0.0}
        avg = sum(r.success_rate for r in self._store.values()) / len(self._store)
        return {"count": len(self._store), "avg_success": round(avg, 3)}

    def detail(self) -> List[Dict[str, float]]:
        return [
            {"concept_id": r.concept_id, "success_rate": round(r.success_rate, 3), "last_days_ago": r.last_days_ago}
            for r in self._store.values()
        ]