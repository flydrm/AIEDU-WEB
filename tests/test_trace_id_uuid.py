import re
from fastapi.testclient import TestClient
from app.presentation.api.main import app


UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")


def test_trace_id_is_uuid_v4():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    trace_id = r.headers.get("X-Trace-Id")
    assert trace_id is not None
    assert UUID_RE.match(trace_id)

