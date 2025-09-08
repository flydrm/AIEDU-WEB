import os
import pytest
from fastapi.testclient import TestClient
from app.presentation.api.main import app


client = TestClient(app)


def test_chat_api_non_stream_contract():
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "你是中文幼儿启蒙老师。"},
            {"role": "user", "content": "讲一个红色小车的三段故事。"},
        ],
        "stream": False,
    }
    r = client.post("/api/v1/ai/chat", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["object"] == "chat.completion"
    assert data["choices"][0]["message"]["role"] == "assistant"


def test_chat_api_error_body():
    payload = {"model": "m", "messages": []}
    r = client.post("/api/v1/ai/chat", json=payload)
    assert r.status_code == 400
    detail = r.json().get("detail")
    assert detail.get("code") == "BAD_REQUEST"
