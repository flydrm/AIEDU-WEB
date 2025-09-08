from fastapi import FastAPI
from .v1 import api as v1
from .metrics import router as metrics_router


def mount_v1(app: FastAPI) -> None:
    app.include_router(v1, prefix="")
    app.include_router(metrics_router, prefix="")

