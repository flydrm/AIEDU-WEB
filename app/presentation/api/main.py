from fastapi import FastAPI
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

    @app.exception_handler(Exception)
    async def generic_exception_handler(_, exc: Exception):
        return JSONResponse(status_code=500, content={"code": "INTERNAL_ERROR", "message": str(exc)})

    # initialize minimal router for DI (can be injected per request later)
    providers = load_providers()
    app.state.llm_router = FailoverLLMRouter(providers) if providers else None
    app.state.chat_uc = (
        ChatCompletionUseCase(app.state.llm_router) if app.state.llm_router else None
    )
    return app


app = create_app()
mount_v1(app)

