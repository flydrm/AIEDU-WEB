from fastapi.testclient import TestClient
from app.presentation.api.main import app


def test_mastery_event_and_summary():
    client = TestClient(app)
    # before any event
    r = client.get("/api/v1/parent/mastery")
    assert r.status_code == 200
    assert r.json()["count"] == 0
    # update mastery
    r = client.post("/api/v1/lesson/event", params={"concept_id": "KC-RED-01", "success": True})
    assert r.status_code == 200
    # summary updated
    r = client.get("/api/v1/parent/mastery")
    js = r.json()
    assert js["count"] >= 1
    assert 0.0 <= js["avg_success"] <= 1.0

