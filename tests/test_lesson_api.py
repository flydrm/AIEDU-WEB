from fastapi.testclient import TestClient
from app.presentation.api.main import app


client = TestClient(app)


def test_today_lesson_returns_plan():
    r = client.get("/api/v1/lesson/today")
    assert r.status_code == 200
    data = r.json()
    assert "cards" in data and "story" in data
    assert isinstance(data["cards"], list) and isinstance(data["story"], list)


def test_today_lesson_with_interests_filters():
    r = client.get("/api/v1/lesson/today", params=[("interests", "红色"), ("interests", "磁力片")])
    assert r.status_code == 200
    data = r.json()
    # at least prefer categories when available in dataset
    assert isinstance(data["cards"], list)
