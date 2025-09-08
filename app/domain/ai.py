from __future__ import annotations

from pydantic import BaseModel
from typing import Any, Literal


class ProviderConfig(BaseModel):
    name: str
    base_url: str
    api_key: str
    timeout: int = 30


class LLMRequest(BaseModel):
    model: str
    messages: list[dict[str, str]]
    stream: bool = False
    temperature: float | None = None
    max_tokens: int | None = None


class LLMChoice(BaseModel):
    index: int
    finish_reason: str | None = None
    message: dict[str, str] | None = None


class LLMUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class LLMResponse(BaseModel):
    id: str
    object: Literal["chat.completion"]
    created: int
    model: str
    choices: list[LLMChoice]
    usage: LLMUsage | None = None

