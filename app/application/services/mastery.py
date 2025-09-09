from __future__ import annotations

from typing import Dict, List, Optional
from app.domain.learning import MasteryRecord
from app.presentation.api.metrics import record_learning_event
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import threading


class MasteryService:
    def __init__(self, storage_path: Optional[str] = None) -> None:
        self._store: Dict[str, MasteryRecord] = {}
        self._events: List[Dict[str, Optional[str]]] = []
        self._path: Optional[Path] = Path(storage_path) if storage_path else None
        self._lock = threading.Lock()

    def get_all(self) -> List[MasteryRecord]:
        return list(self._store.values())

    def clear(self) -> None:
        self._store.clear()
        self._events.clear()
        self._save_safe()

    def _today(self) -> str:
        return datetime.now(timezone.utc).date().isoformat()

    def update(self, concept_id: str, success: bool) -> MasteryRecord:
        rec = self._store.get(concept_id) or MasteryRecord(concept_id=concept_id, success_rate=0.5, last_days_ago=7)
        # exponential moving average toward 1.0 or 0.0
        alpha = 0.3
        target = 1.0 if success else 0.0
        rec.success_rate = (1 - alpha) * rec.success_rate + alpha * target
        rec.last_days_ago = 0
        self._store[concept_id] = rec
        record_learning_event("complete_success" if success else "complete_fail")
        self._events.append({
            "date": self._today(),
            "concept_id": concept_id,
            "type": "complete",
            "success": "1" if success else "0",
        })
        self._save_safe()
        return rec

    def elapse_days(self, days: int = 1) -> None:
        for r in self._store.values():
            r.last_days_ago += max(0, days)
        self._save_safe()

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

    def record_start(self, concept_id: str) -> None:
        record_learning_event("start")
        self._events.append({
            "date": self._today(),
            "concept_id": concept_id,
            "type": "start",
            "success": None,
        })
        self._save_safe()

    def record_help(self, concept_id: str) -> None:
        record_learning_event("help")
        self._events.append({
            "date": self._today(),
            "concept_id": concept_id,
            "type": "help",
            "success": None,
        })
        self._save_safe()

    def timeseries(self, days: int = 7) -> List[Dict[str, float]]:
        if days <= 0:
            days = 7
        end = datetime.now(timezone.utc).date()
        series: List[Dict[str, float]] = []
        for i in range(days - 1, -1, -1):
            d = (end - timedelta(days=i)).isoformat()
            evs = [e for e in self._events if e.get("date") == d and e.get("type") == "complete"]
            succ = sum(1 for e in evs if e.get("success") == "1")
            cnt = len(evs)
            rate = (succ / cnt) if cnt else 0.0
            series.append({"date": d, "count": cnt, "success_rate": round(rate, 3)})
        return series

    # -------------------- Persistence --------------------
    def load(self) -> None:
        if not self._path:
            return
        try:
            if self._path.exists():
                with self._path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                self._store = {
                    k: MasteryRecord(concept_id=k, success_rate=float(v.get("success_rate", 0.5)), last_days_ago=int(v.get("last_days_ago", 7)))
                    for k, v in (data.get("store") or {}).items()
                }
                self._events = list(data.get("events") or [])
        except Exception:
            # fail open: keep in-memory defaults
            self._store = self._store or {}
            self._events = self._events or []

    def _save_safe(self) -> None:
        if not self._path:
            return
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "store": {rid: {"success_rate": rec.success_rate, "last_days_ago": rec.last_days_ago} for rid, rec in self._store.items()},
                "events": self._events[-1000:],  # cap length to avoid unbounded growth
            }
            tmp = self._path.with_suffix(self._path.suffix + ".tmp")
            with self._lock:
                with tmp.open("w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False)
                tmp.replace(self._path)
        except Exception:
            # swallow persistence errors to avoid impacting UX
            pass