from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_demo_error():
    r = client.get("/demo/error")
    assert r.status_code == 503
    assert r.json()["error"] == "dependency_unavailable"
    assert "request_id" in r.json()
