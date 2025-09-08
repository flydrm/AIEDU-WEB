from fastapi.testclient import TestClient
from app.presentation.api.main import app


client = TestClient(app)


def test_safety_inspect_rewrites_danger():
    r = client.post("/api/v1/safety/inspect", json={"text": "拿刀打人"})
    assert r.status_code == 200
    data = r.json()
    assert data["changed"] is True
    assert "安全工具" in data["output"]
