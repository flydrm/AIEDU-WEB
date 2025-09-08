from fastapi import APIRouter
from .ai import router as ai_router


api = APIRouter()
api.include_router(ai_router)

