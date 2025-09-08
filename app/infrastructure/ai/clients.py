from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from .errors import RateLimitError, TimeoutError, ServerError


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: int = 30) -> None:
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self._fail_count = 0
        self._opened_at: float | None = None

    def allow(self) -> bool:
        if self._opened_at is None:
            return True
        if time.time() - self._opened_at >= self.cooldown_seconds:
            # half-open: allow a trial
            return True
        return False

    def record_success(self) -> None:
        self._fail_count = 0
        self._opened_at = None

    def record_failure(self) -> None:
        self._fail_count += 1
        if self._fail_count >= self.failure_threshold:
            self._opened_at = time.time()


class OpenAICompatibleClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def close(self) -> None:
        await self._client.aclose()

    async def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        backoff = 0.1
        for attempt in range(3):
            try:
                resp = await self._client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    return resp.json()
                if resp.status_code == 429:
                    if attempt < 2:
                        await asyncio.sleep(backoff)
                        backoff *= 2
                        continue
                    raise RateLimitError("rate limited")
                if 500 <= resp.status_code < 600:
                    if attempt < 2:
                        await asyncio.sleep(backoff)
                        backoff *= 2
                        continue
                    raise ServerError(f"server error {resp.status_code}")
                # 4xx other
                raise ServerError(f"unexpected status {resp.status_code}")
            except httpx.ReadTimeout:
                if attempt < 2:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                raise TimeoutError("read timeout")
            except httpx.ConnectTimeout:
                if attempt < 2:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                raise TimeoutError("connect timeout")


class FailoverLLMRouter:
    def __init__(self, providers: list[dict[str, Any]]) -> None:
        self._providers = providers
        self._breakers = [CircuitBreaker() for _ in providers]

    async def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        last_err: Exception | None = None
        for idx, cfg in enumerate(self._providers):
            br = self._breakers[idx]
            if not br.allow():
                continue
            client = OpenAICompatibleClient(cfg["base_url"], cfg["api_key"], cfg.get("timeout", 30))
            try:
                result = await client.chat_completions(payload)
                br.record_success()
                await client.close()
                return result
            except Exception as e:  # noqa: BLE001
                last_err = e
                br.record_failure()
            finally:
                await client.close()
        if last_err:
            raise last_err
        raise ServerError("no providers configured")

