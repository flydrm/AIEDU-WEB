from fastapi.testclient import TestClient
from app.presentation.api.main import app


client = TestClient(app)


def test_openapi_available():
    r = client.get("/openapi.json")
    assert r.status_code == 200
    data = r.json()
    assert "paths" in data and "/api/v1/ai/chat" in data["paths"]
