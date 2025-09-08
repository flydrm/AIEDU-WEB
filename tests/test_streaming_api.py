import pytest
from fastapi.testclient import TestClient
from app.presentation.api.main import app


client = TestClient(app)


def test_stream_sse_contract_smoke():
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "你是中文幼儿启蒙老师。"},
            {"role": "user", "content": "讲一个红色小车的三段故事。"},
        ],
        "stream": True,
    }
    with client.stream("POST", "/api/v1/ai/chat", json=payload) as r:
        assert r.status_code == 200
        # Placeholder environment returns dev message and then ends quickly; we just ensure lines arrive
        got_any = False
        for line in r.iter_lines():
            if line:
                assert isinstance(line, (str, bytes))
                got_any = True
                break
        assert got_any is True
