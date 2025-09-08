from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.presentation.api import mount_v1
from app.infrastructure.ai.settings import load_providers
from app.infrastructure.ai.clients import FailoverLLMRouter
from app.application.use_cases.chat_completion import ChatCompletionUseCase
import json
from app.presentation.api.metrics import increment_requests_counter


def create_app() -> FastAPI:
    app = FastAPI(title="Kids AI App", version="0.1.0")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.middleware("http")
    async def add_trace_id(request: Request, call_next):
        trace_id = request.headers.get("X-Trace-Id") or "trace-" + str(id(request))
        increment_requests_counter()
        response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        return response

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        trace_id = request.headers.get("X-Trace-Id") or "trace-" + str(id(request))
        return JSONResponse(
            status_code=500,
            content={"code": "INTERNAL_ERROR", "message": str(exc), "trace_id": trace_id},
            headers={"X-Trace-Id": trace_id},
        )

    # initialize minimal router for DI (can be injected per request later)
    providers = load_providers()
    import os
    br_fail = int(os.environ.get("AI_BREAKER_FAILURES", "3"))
    br_cool = int(os.environ.get("AI_BREAKER_COOLDOWN", "30"))
    app.state.llm_router = (
        FailoverLLMRouter(providers, breaker_failures=br_fail, breaker_cooldown=br_cool)
        if providers
        else None
    )
    app.state.chat_uc = (
        ChatCompletionUseCase(app.state.llm_router) if app.state.llm_router else None
    )
    # load kids dataset for personalization if available
    try:
        with open("content/kids_3yo_dataset.json", "r", encoding="utf-8") as f:
            app.state.kids_dataset = json.load(f)
    except Exception:
        app.state.kids_dataset = {"knowledge_cards": [], "story_prompts": []}
    return app


app = create_app()
mount_v1(app)

