from fastapi.testclient import TestClient
from app.presentation.api.main import app


def test_weekly_csv_export():
    client = TestClient(app)
    client.post("/api/v1/lesson/event", params={"concept_id": "KC-RED-01", "success": True})
    r = client.get("/api/v1/parent/mastery/weekly.csv")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    body = r.text
    assert "date,count,success_rate" in body
