from fastapi.testclient import TestClient
from app.presentation.api.main import app


client = TestClient(app)


def test_ready_endpoint():
    r = client.get("/ready")
    assert r.status_code == 200
    data = r.json()
    assert "llm_router" in data
