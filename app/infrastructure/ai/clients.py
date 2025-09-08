"""AI provider client layer with retry, circuit breaker and failover.

This module provides:
- CircuitBreaker: controls provider availability based on recent failures.
- OpenAICompatibleClient: minimal OpenAI-compatible HTTP client (non-stream & stream),
  with exponential backoff retry and typed errors.
- FailoverLLMRouter: iterates through providers, respects circuit breaker, records
  success/failure and performs failover. For streaming, yields chunks from the first
  healthy provider.

Metrics hooks are integrated via record_llm_* functions to expose Prometheus counters
for success/error/failover. This allows quick incident triage and SLO tracking.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from .errors import RateLimitError, TimeoutError, ServerError
from app.presentation.api.metrics import record_llm_success, record_llm_error, record_llm_failover


class CircuitBreaker:
    """Simple time-based circuit breaker.

    - When failures reach the threshold, the breaker opens and remains open for
      cooldown_seconds. During open state, calls are skipped (allow() returns False).
    - After cooldown, the breaker becomes half-open (allow returns True). One trial
      request is permitted; on success it closes, on failure it opens again.
    """
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
    """Minimal OpenAI-compatible async client.

    Supports:
    - POST /v1/chat/completions (JSON)
    - SSE streaming via httpx stream API
    - Exponential backoff retry for 429/5xx and timeouts (3 attempts)

    Records Prometheus metrics for success and error outcomes.
    """
    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0, provider_name: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.provider = provider_name or self.base_url
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def close(self) -> None:
        await self._client.aclose()

    async def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Non-streaming chat completions.

        Retries on 429/5xx/timeouts with exponential backoff. On success, records
        a success metric. On terminal errors, records an error metric and raises
        a typed exception for the API layer to map.
        """
        url = f"{self.base_url}/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        backoff = 0.1
        for attempt in range(3):
            try:
                resp = await self._client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    record_llm_success(self.provider)
                    return resp.json()
                if resp.status_code == 429:
                    if attempt < 2:
                        await asyncio.sleep(backoff)
                        backoff *= 2
                        continue
                    record_llm_error(self.provider, "429")
                    raise RateLimitError("rate limited")
                if 500 <= resp.status_code < 600:
                    if attempt < 2:
                        await asyncio.sleep(backoff)
                        backoff *= 2
                        continue
                    record_llm_error(self.provider, str(resp.status_code))
                    raise ServerError(f"server error {resp.status_code}")
                # 4xx other
                record_llm_error(self.provider, str(resp.status_code))
                raise ServerError(f"unexpected status {resp.status_code}")
            except httpx.ReadTimeout:
                if attempt < 2:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                record_llm_error(self.provider, "read_timeout")
                raise TimeoutError("read timeout")
            except httpx.ConnectTimeout:
                if attempt < 2:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                record_llm_error(self.provider, "connect_timeout")
                raise TimeoutError("connect timeout")

    async def stream_chat_completions(self, payload: dict[str, Any]):
        """Streaming chat completions via SSE-compatible chunk lines.

        Yields lines with "data: ...\n\n" format. Applies the same retry policy
        as non-streaming and records metrics accordingly.
        """
        url = f"{self.base_url}/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        backoff = 0.1
        for attempt in range(3):
            try:
                async with self._client.stream("POST", url, json=payload, headers=headers) as resp:
                    if resp.status_code == 200:
                        record_llm_success(self.provider)
                        async for line in resp.aiter_lines():
                            if not line:
                                continue
                            if not line.startswith("data:"):
                                yield f"data: {line}\n\n"
                            else:
                                # passthrough including DONE
                                yield line + "\n\n"
                        return
                    if resp.status_code == 429:
                        if attempt < 2:
                            await asyncio.sleep(backoff)
                            backoff *= 2
                            continue
                        record_llm_error(self.provider, "429")
                        raise RateLimitError("rate limited")
                    if 500 <= resp.status_code < 600:
                        if attempt < 2:
                            await asyncio.sleep(backoff)
                            backoff *= 2
                            continue
                        record_llm_error(self.provider, str(resp.status_code))
                        raise ServerError(f"server error {resp.status_code}")
                    raise ServerError(f"unexpected status {resp.status_code}")
            except httpx.ReadTimeout:
                if attempt < 2:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                record_llm_error(self.provider, "read_timeout")
                raise TimeoutError("read timeout")
            except httpx.ConnectTimeout:
                if attempt < 2:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                record_llm_error(self.provider, "connect_timeout")
                raise TimeoutError("connect timeout")


class FailoverLLMRouter:
    """Provider router with circuit breaker and failover.

    Iterates through configured providers in order. Skips providers whose
    circuit breaker is open. On failure, records breaker failure and attempts
    the next provider. Streaming pass-through yields chunks from the first
    provider that responds successfully.
    """
    def __init__(self, providers: list[dict[str, Any]], *, breaker_failures: int | None = None, breaker_cooldown: int | None = None) -> None:
        self._providers = providers
        self._breakers = [
            CircuitBreaker(failure_threshold=breaker_failures or 3, cooldown_seconds=breaker_cooldown or 30)
            for _ in providers
        ]
        self._clients = [
            OpenAICompatibleClient(p["base_url"], p["api_key"], p.get("timeout", 30), provider_name=p.get("name") or p.get("base_url"))
            for p in providers
        ]

    async def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Call providers in order until one succeeds or all fail."""
        last_err: Exception | None = None
        for idx, cfg in enumerate(self._providers):
            br = self._breakers[idx]
            if not br.allow():
                continue
            client = self._clients[idx]
            try:
                result = await client.chat_completions(payload)
                br.record_success()
                return result
            except Exception as e:  # noqa: BLE001
                last_err = e
                br.record_failure()
            finally:
                pass
        if last_err:
            raise last_err
        raise ServerError("no providers configured")

    def breaker_states(self) -> list[str]:
        """Return coarse breaker states per provider ("closed" or "open")."""
        states: list[str] = []
        for b in self._breakers:
            if b._opened_at is None:  # noqa: SLF001
                states.append("closed")
            else:
                # simplistic: treat as open; half-open not tracked separately
                states.append("open")
        return states

    async def stream_chat_completions(self, payload: dict[str, Any]):
        """Stream from the first healthy provider; record failover transitions."""
        last_err: Exception | None = None
        for idx, cfg in enumerate(self._providers):
            br = self._breakers[idx]
            if not br.allow():
                continue
            client = self._clients[idx]
            try:
                async for chunk in client.stream_chat_completions(payload):
                    yield chunk
                br.record_success()
                return
            except Exception as e:  # noqa: BLE001
                last_err = e
                br.record_failure()
                # record failover when moving to next provider
                next_idx = idx + 1
                if next_idx < len(self._providers):
                    record_llm_failover(self._providers[idx].get("name") or self._providers[idx]["base_url"], self._providers[next_idx].get("name") or self._providers[next_idx]["base_url"]) 
            finally:
                pass
        if last_err:
            raise last_err
        raise ServerError("no providers configured")

