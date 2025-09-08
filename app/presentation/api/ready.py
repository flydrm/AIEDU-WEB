from fastapi import APIRouter


router = APIRouter(tags=["Ready"])


@router.get("/ready")
async def ready():
    from app.presentation.api.main import app as _app

    ok = _app.state.llm_router is not None
    states = _app.state.llm_router.breaker_states() if ok else []
    return {"llm_router": ok, "breaker_states": states}

