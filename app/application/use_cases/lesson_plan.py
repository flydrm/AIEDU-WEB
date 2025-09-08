from __future__ import annotations

from typing import Any


class DailyLessonPlanUseCase:
    def __init__(self, dataset: dict[str, Any]) -> None:
        self._ds = dataset

    def __call__(self, interests: list[str] | None = None) -> dict[str, Any]:
        # naive rule-based: pick 2 knowledge cards + 1 story prompt + 1 family + 1 logic
        cards = [c for c in self._ds.get("knowledge_cards", [])]
        prompts = [p for p in self._ds.get("story_prompts", [])]
        if interests:
            cards = [c for c in cards if c.get("category") in interests] + [c for c in cards if c.get("category") not in interests][:4]
            prompts = [p for p in prompts if p.get("category") in interests] + [p for p in prompts if p.get("category") not in interests][:4]

        plan = {
            "cards": cards[:2],
            "story": prompts[:1],
            "family": [c for c in cards if c.get("category") in {"爱家人", "爱妈妈", "爱爸爸", "爱爷爷奶奶"}][:1],
            "logic": [c for c in cards if c.get("category") == "逻辑"][:1],
        }
        return plan

