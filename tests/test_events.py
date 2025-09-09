from fastapi.testclient import TestClient
from app.presentation.api.main import app


def test_learning_event_metrics_and_detail():
    client = TestClient(app)
    client.post("/api/v1/lesson/event", params={"concept_id": "KC-LOGIC-01", "success": False})
    r = client.get("/api/v1/parent/mastery/detail")
    assert r.status_code == 200
    arr = r.json()
    assert any(it["concept_id"] == "KC-LOGIC-01" for it in arr)
