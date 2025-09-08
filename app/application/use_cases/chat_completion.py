from __future__ import annotations

from typing import Any

from app.infrastructure.ai.clients import FailoverLLMRouter


class ChatCompletionUseCase:
    def __init__(self, router: FailoverLLMRouter) -> None:
        self._router = router

    async def __call__(self, payload: dict[str, Any]) -> dict[str, Any]:
        # 这里可加入白名单/参数裁剪/模板化处理
        return await self._router.chat_completions(payload)

