from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)
HEADERS = {"X-API-Key": "saas-devops-secret-2026"}

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_kpis_unauthorized():
    r = client.get("/api/kpis")
    assert r.status_code == 401

def test_kpis_authorized():
    r = client.get("/api/kpis", headers=HEADERS)
    assert r.status_code == 200
    assert "total_logs" in r.json()

def test_alerts_authorized():
    r = client.get("/api/alerts", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["threshold_ms"] == 3000
