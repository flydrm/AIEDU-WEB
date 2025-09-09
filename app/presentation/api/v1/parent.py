from fastapi import APIRouter


router = APIRouter(prefix="/api/v1/parent", tags=["Parent"])


@router.get("/mastery")
async def get_mastery_summary():
    from app.presentation.api.main import app as _app
    svc = getattr(_app.state, "mastery_service", None)
    if not svc:
        return {"count": 0, "avg_success": 0.0}
    return svc.summary()


@router.get("/mastery/detail")
async def get_mastery_detail():
    from app.presentation.api.main import app as _app
    svc = getattr(_app.state, "mastery_service", None)
    if not svc:
        return []
    return svc.detail()


@router.get("/mastery/timeseries")
async def get_mastery_timeseries(days: int = 7):
    from app.presentation.api.main import app as _app
    svc = getattr(_app.state, "mastery_service", None)
    if not svc:
        return []
    return svc.timeseries(days)

