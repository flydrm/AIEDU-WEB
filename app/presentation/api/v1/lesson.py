from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional


router = APIRouter(prefix="/api/v1/lesson", tags=["Lesson"])


@router.get("/today")
async def get_today_lesson(interests: Optional[List[str]] = Query(default=None)):
    from app.application.use_cases.lesson_plan import DailyLessonPlanUseCase
    # use app state dataset
    # This function signature will be wrapped by FastAPI; obtain request via context
    # Workaround: FastAPI dependency could be added later; for now import app state from global
    from app.presentation.api.main import app as _app

    ds = getattr(_app.state, "kids_dataset", {"knowledge_cards": [], "story_prompts": []})
    mastery = []
    svc = getattr(_app.state, "mastery_service", None)
    if svc:
        mastery = svc.get_all()
    plan = DailyLessonPlanUseCase(ds, mastery)(interests or None)
    return plan


@router.post("/event")
async def post_lesson_event(concept_id: str, success: bool):
    from app.presentation.api.main import app as _app
    svc = getattr(_app.state, "mastery_service", None)
    if not svc:
        raise HTTPException(status_code=500, detail={"code": "NO_MASTERY", "message": "mastery service not available"})
    rec = svc.update(concept_id, success)
    return {"concept_id": rec.concept_id, "success_rate": rec.success_rate, "last_days_ago": rec.last_days_ago}

