"""Application use case for chat completions.

Keep business orchestration separate from transport (FastAPI) and infra clients.
This allows easy substitution in tests and future extensions (e.g., safety/TTS).
"""
from __future__ import annotations

from typing import Any
from app.infrastructure.rag.retriever import SimpleRetriever

from app.infrastructure.ai.clients import FailoverLLMRouter


class ChatCompletionUseCase:
    def __init__(self, router: FailoverLLMRouter, retriever: SimpleRetriever | None = None) -> None:
        self._router = router
        self._retriever = retriever

    async def __call__(self, payload: dict[str, Any]) -> dict[str, Any]:
        # 这里可加入白名单/参数裁剪/模板化处理
        # Lightweight RAG: retrieve top docs and inject as system hint
        if self._retriever and payload.get("messages"):
            try:
                # take last user utterance for retrieval
                last = next((m for m in reversed(payload["messages"]) if m.get("role") == "user"), None)
                if last and last.get("content"):
                    docs = self._retriever.retrieve(str(last["content"]), top_k=3)
                    if docs:
                        ctx = []
                        for d in docs:
                            title = d.get("title") or d.get("id") or d.get("type")
                            ctx.append(f"- {title}: {d.get('text', '')}")
                        hint = "\n".join(ctx)
                        payload = dict(payload)
                        payload["messages"] = [
                            {"role": "system", "content": "你是一名幼儿启蒙助手。请结合下述知识点，用适龄、温柔的表述来回答。\n" + hint}
                        ] + payload["messages"]
            except Exception:
                # fail open on retrieval
                pass
        return await self._router.chat_completions(payload)

