from fastapi import FastAPI
from .v1 import api as v1
from .metrics import router as metrics_router
from .ready import router as ready_router


def mount_v1(app: FastAPI) -> None:
    app.include_router(v1, prefix="")
    app.include_router(metrics_router, prefix="")
    app.include_router(ready_router, prefix="")

