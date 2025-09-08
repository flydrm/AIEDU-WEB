from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from fastapi.responses import StreamingResponse
from app.presentation.api.error_mapper import to_http_exc


router = APIRouter(prefix="/api/v1/ai", tags=["AI"])


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: bool = False
    temperature: float | None = Field(default=None, ge=0, le=2)
    max_tokens: int | None = Field(default=None, ge=1, le=4096)


class ChatChoice(BaseModel):
    index: int
    finish_reason: Optional[str] = None
    message: Optional[ChatMessage] = None


class ChatUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    id: str
    object: Literal["chat.completion"]
    created: int
    model: str
    choices: List[ChatChoice]
    usage: ChatUsage | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    if not req.messages:
        raise HTTPException(status_code=400, detail={"code": "BAD_REQUEST", "message": "messages required"})
    # If router not configured, return placeholder to keep E2E alive in dev
    chat_uc = getattr(request.app.state, "chat_uc", None)
    if chat_uc is None:
        return ChatResponse(
            id="chatcmpl-placeholder",
            object="chat.completion",
            created=0,
            model=req.model,
            choices=[
                ChatChoice(
                    index=0,
                    finish_reason="stop",
                    message=ChatMessage(role="assistant", content="(dev) llm not configured"),
                )
            ],
            usage=ChatUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
        )
    payload = req.model_dump()
    if not req.stream:
        try:
            data = await chat_uc(payload)
        except Exception as e:  # noqa: BLE001
            raise to_http_exc(e)
        return ChatResponse.model_validate(data)
    # stream branch
    async def gen():
        try:
            async for chunk in request.app.state.llm_router.stream_chat_completions(payload):
                yield chunk
        except Exception as e:  # noqa: BLE001
            # map to sse error frame then end
            err = to_http_exc(e)
            yield f"data: {{\"error\":{{\"status\":{err.status_code},\"code\":\"{err.detail['code']}\",\"message\":\"{err.detail['message']}\"}}}}\n\n"
            yield "data: [DONE]\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")

