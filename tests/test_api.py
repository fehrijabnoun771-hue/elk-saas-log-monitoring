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

def test_v1_34_kpis_and_role():
    r = client.get("/api/v1/kpi/all", headers=HEADERS)
    assert r.status_code == 200 and r.json()["total_kpis"] == 34 and r.json()["role"] == "admin"

def test_v1_search_and_upload_rbac():
    assert client.get("/api/v1/logs?level=ERROR", headers=HEADERS).status_code == 200
    r_viewer = client.post("/api/v1/upload", headers={"X-API-Key": "viewer-key-2026"}, files={"file": ("t.json", b"{}")})
    assert r_viewer.status_code == 403
