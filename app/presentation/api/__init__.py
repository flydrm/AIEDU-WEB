from fastapi import FastAPI
from .v1 import api as v1


def mount_v1(app: FastAPI) -> None:
    app.include_router(v1, prefix="")

