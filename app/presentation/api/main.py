from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.presentation.api import mount_v1
from app.infrastructure.ai.settings import load_providers
from app.infrastructure.ai.clients import FailoverLLMRouter
from app.application.use_cases.chat_completion import ChatCompletionUseCase


def create_app() -> FastAPI:
    app = FastAPI(title="Kids AI App", version="0.1.0")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.middleware("http")
    async def add_trace_id(request: Request, call_next):
        trace_id = request.headers.get("X-Trace-Id") or "trace-" + str(id(request))
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
    app.state.llm_router = FailoverLLMRouter(providers) if providers else None
    app.state.chat_uc = (
        ChatCompletionUseCase(app.state.llm_router) if app.state.llm_router else None
    )
    return app


app = create_app()
mount_v1(app)

