"""Application-wide Prometheus metrics.

Exposes /metrics and provides helper functions to record HTTP and LLM metrics.
These counters/histograms enable fast troubleshooting and SLA/SLO monitoring.
"""
from fastapi import APIRouter, Response, Request, HTTPException
import os
from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST


router = APIRouter(tags=["Metrics"])


REGISTRY = CollectorRegistry()
HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["path", "method", "status"],
    registry=REGISTRY,
)
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["path", "method", "status"],
    registry=REGISTRY,
)

# LLM metrics
LLM_REQUESTS = Counter(
    "llm_requests_total",
    "LLM request count",
    ["provider", "result"],
    registry=REGISTRY,
)
LLM_FAILOVER = Counter(
    "llm_failover_total",
    "LLM failover switches",
    ["from", "to"],
    registry=REGISTRY,
)


@router.get("/metrics")
async def metrics(request: Request):
    # In non-prod environments, expose metrics without restriction to simplify tests/dev
    if os.environ.get("APP_ENV", "dev") != "prod":
        return Response(content=generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
    # Basic protection in prod: allow only localhost/internal proxies
    client = request.client.host if request and request.client else ""
    if client not in {"127.0.0.1", "::1", "localhost"}:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "metrics restricted"})
    return Response(content=generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)


def record_request_metrics(path: str, method: str, status: int, duration: float) -> None:
    labels = {"path": path, "method": method, "status": str(status)}
    HTTP_REQUESTS.labels(**labels).inc()
    HTTP_REQUEST_DURATION.labels(**labels).observe(duration)


def record_llm_success(provider: str) -> None:
    LLM_REQUESTS.labels(provider=provider, result="success").inc()


def record_llm_error(provider: str, result: str) -> None:
    LLM_REQUESTS.labels(provider=provider, result=result).inc()


def record_llm_failover(from_provider: str, to_provider: str) -> None:
    LLM_FAILOVER.labels(**{"from": from_provider, "to": to_provider}).inc()

