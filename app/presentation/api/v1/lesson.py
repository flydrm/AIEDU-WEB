from fastapi import APIRouter, Query
from typing import List, Optional


router = APIRouter(prefix="/api/v1/lesson", tags=["Lesson"])


@router.get("/today")
async def get_today_lesson(interests: Optional[List[str]] = Query(default=None)):
    from app.application.use_cases.lesson_plan import DailyLessonPlanUseCase
    from fastapi import Request  # lazy import to avoid cycle
    # use app state dataset
    # This function signature will be wrapped by FastAPI; obtain request via context
    # Workaround: FastAPI dependency could be added later; for now import app state from global
    from app.presentation.api.main import app as _app

    ds = getattr(_app.state, "kids_dataset", {"knowledge_cards": [], "story_prompts": []})
    plan = DailyLessonPlanUseCase(ds)(interests or None)
    return plan

