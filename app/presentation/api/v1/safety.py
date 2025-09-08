from fastapi import APIRouter
from pydantic import BaseModel
from app.application.use_cases.safety_rewrite import inspect_and_rewrite


router = APIRouter(prefix="/api/v1/safety", tags=["Safety"])


class InspectRequest(BaseModel):
    text: str


class InspectResponse(BaseModel):
    changed: bool
    output: str


@router.post("/inspect", response_model=InspectResponse)
async def inspect(req: InspectRequest):
    changed, out = inspect_and_rewrite(req.text)
    return InspectResponse(changed=changed, output=out)

