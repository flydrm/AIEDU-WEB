from fastapi import APIRouter
from .ai import router as ai_router
from .lesson import router as lesson_router
from .safety import router as safety_router


api = APIRouter()
api.include_router(ai_router)
api.include_router(lesson_router)
api.include_router(safety_router)

