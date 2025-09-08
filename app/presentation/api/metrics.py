from fastapi import APIRouter, Response


router = APIRouter(tags=["Metrics"])


_counters = {"requests_total": 0}


@router.get("/metrics")
async def metrics():
    body = "".join([f"# TYPE {k} counter\n{k} {v}\n" for k, v in _counters.items()])
    return Response(content=body, media_type="text/plain; version=0.0.4")


def increment_requests_counter():
    _counters["requests_total"] += 1

