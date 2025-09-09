from __future__ import annotations

from typing import Any
from app.domain.learning import MasteryRecord, schedule_score


class DailyLessonPlanUseCase:
    def __init__(self, dataset: dict[str, Any], mastery: list[MasteryRecord] | None = None) -> None:
        self._ds = dataset
        self._mastery = mastery or []

    def __call__(self, interests: list[str] | None = None) -> dict[str, Any]:
        # naive rule-based: pick 2 knowledge cards + 1 story prompt + 1 family + 1 logic
        cards = [c for c in self._ds.get("knowledge_cards", [])]
        prompts = [p for p in self._ds.get("story_prompts", [])]
        if interests:
            cards = [c for c in cards if c.get("category") in interests] + [c for c in cards if c.get("category") not in interests][:4]
            prompts = [p for p in prompts if p.get("category") in interests] + [p for p in prompts if p.get("category") not in interests][:4]

        # mastery-aware reordering: prioritize low success_rate and long-not-seen concepts
        if self._mastery:
            score_map = {m.concept_id: schedule_score(m) for m in self._mastery}
            def weight(item: dict[str, Any]) -> float:
                cid = item.get("id") or item.get("title") or ""
                return score_map.get(cid, 0.0)
            cards = sorted(cards, key=weight, reverse=True) + [c for c in cards if weight(c) == 0.0]

        plan = {
            "cards": cards[:2],
            "story": prompts[:1],
            "family": [c for c in cards if c.get("category") in {"爱家人", "爱妈妈", "爱爸爸", "爱爷爷奶奶"}][:1],
            "logic": [c for c in cards if c.get("category") == "逻辑"][:1],
        }
        return plan

