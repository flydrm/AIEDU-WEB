"""FastAPI application setup: middlewares, routers, error handling.

Adds:
- CORS policy (development-friendly, can be tightened in prod)
- Trace-Id middleware with request duration metrics
- Structured JSON logs via structlog (request.start / request.end)
- Generic exception handler with trace propagation
- DI of providers and use cases, plus dataset preload
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.presentation.api import mount_v1
from app.infrastructure.ai.settings import load_providers
from app.infrastructure.ai.clients import FailoverLLMRouter
from app.application.use_cases.chat_completion import ChatCompletionUseCase
from app.infrastructure.rag.retriever import SimpleRetriever, HybridRetriever
from app.infrastructure.ai.clients import EmbeddingsClient
from app.application.services.mastery import MasteryService
import json
import time
import uuid
from app.presentation.api.metrics import record_request_metrics
from fastapi.middleware.cors import CORSMiddleware
import logging
import structlog


def create_app() -> FastAPI:
    app = FastAPI(title="Kids AI App", version="0.1.0")

    # Configure structlog for JSON logs
    logging.basicConfig(level=logging.INFO)
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", key="ts"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )
    logger = structlog.get_logger("api")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    @app.middleware("http")
    async def add_trace_id(request: Request, call_next):
        trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())
        start = time.perf_counter()
        logger.info("request.start", path=request.url.path, method=request.method, trace_id=trace_id)
        response = await call_next(request)
        duration = time.perf_counter() - start
        response.headers["X-Trace-Id"] = trace_id
        try:
            record_request_metrics(request.url.path, request.method, response.status_code, duration)
        except Exception:
            pass
        logger.info(
            "request.end",
            path=request.url.path,
            method=request.method,
            status=response.status_code,
            duration_ms=int(duration * 1000),
            trace_id=trace_id,
        )
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
    retriever = None
    try:
        # build Hybrid retriever; if embeddings is not configured, it falls back to TF-IDF only
        providers = load_providers()
        embed_client = None
        if providers:
            p0 = providers[0]
            embed_client = EmbeddingsClient(p0["base_url"], p0["api_key"], p0.get("timeout", 30))
        base = SimpleRetriever.from_kids_dataset(app.state.kids_dataset)
        retriever = HybridRetriever(base._docs, embed_client) if embed_client else base
    except Exception:
        retriever = None
    app.state.chat_uc = (
        ChatCompletionUseCase(app.state.llm_router, retriever) if app.state.llm_router else None
    )
    # load kids dataset for personalization if available
    try:
        with open("content/kids_3yo_dataset.json", "r", encoding="utf-8") as f:
            app.state.kids_dataset = json.load(f)
    except Exception:
        app.state.kids_dataset = {"knowledge_cards": [], "story_prompts": []}
    # mastery service (in-memory)
    app.state.mastery_service = MasteryService()
    return app


app = create_app()
mount_v1(app)

