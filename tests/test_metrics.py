from fastapi.testclient import TestClient
from app.presentation.api.main import app


client = TestClient(app)


def test_metrics_endpoint_exposes_counter():
    # hit health to increase counter
    client.get("/health")
    r = client.get("/metrics")
    assert r.status_code == 200
    # Prom format with names
    assert "http_requests_total" in r.text
