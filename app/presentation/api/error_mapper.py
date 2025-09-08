from fastapi import HTTPException
from app.infrastructure.ai.errors import (
    AppError,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    RateLimitError,
    TimeoutError,
    ServerError,
)


def to_http_exc(err: Exception) -> HTTPException:
    if isinstance(err, BadRequestError):
        return HTTPException(status_code=400, detail={"code": err.code, "message": str(err)})
    if isinstance(err, UnauthorizedError):
        return HTTPException(status_code=401, detail={"code": err.code, "message": str(err)})
    if isinstance(err, ForbiddenError):
        return HTTPException(status_code=403, detail={"code": err.code, "message": str(err)})
    if isinstance(err, RateLimitError):
        return HTTPException(status_code=429, detail={"code": err.code, "message": str(err)})
    if isinstance(err, TimeoutError):
        return HTTPException(status_code=504, detail={"code": err.code, "message": str(err)})
    if isinstance(err, ServerError):
        return HTTPException(status_code=502, detail={"code": err.code, "message": str(err)})
    if isinstance(err, AppError):
        return HTTPException(status_code=500, detail={"code": err.code, "message": str(err)})
    return HTTPException(status_code=500, detail={"code": "INTERNAL_ERROR", "message": str(err)})

