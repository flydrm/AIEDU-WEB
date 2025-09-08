import asyncio
import pytest
from app.infrastructure.ai.clients import OpenAICompatibleClient, CircuitBreaker


class DummyResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class DummyClient:
    def __init__(self, seq: list[int]):
        self.seq = seq
        self.calls = 0

    async def post(self, url, json=None, headers=None):  # noqa: ARG002
        code = self.seq[min(self.calls, len(self.seq) - 1)]
        self.calls += 1
        await asyncio.sleep(0)
        return DummyResponse(code, {"ok": code == 200})

    async def aclose(self):
        pass


@pytest.mark.asyncio
async def test_openai_client_retry_429(monkeypatch):
    client = OpenAICompatibleClient("http://x", "k")
    dummy = DummyClient([429, 200])
    monkeypatch.setattr(client, "_client", dummy)
    data = await client.chat_completions({"model": "m", "messages": []})
    assert data["ok"] is True
    assert dummy.calls == 2


@pytest.mark.asyncio
async def test_openai_client_retry_5xx(monkeypatch):
    client = OpenAICompatibleClient("http://x", "k")
    dummy = DummyClient([500, 502, 200])
    monkeypatch.setattr(client, "_client", dummy)
    data = await client.chat_completions({"model": "m", "messages": []})
    assert data["ok"] is True
    assert dummy.calls >= 3


def test_circuit_breaker_open_halfclose():
    br = CircuitBreaker(failure_threshold=2, cooldown_seconds=0)
    assert br.allow() is True
    br.record_failure()
    br.record_failure()
    assert br.allow() is True  # half-open because cooldown 0
    br.record_success()
    assert br.allow() is True
