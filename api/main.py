import os, json, time
from datetime import datetime, timezone
from fastapi import FastAPI, Header, Header, HTTPException
import requests, redis
from pymongo import MongoClient

app = FastAPI(title="SaaS ELK Monitoring KPI API")

import time, socket, json as js_elk
from fastapi import Request

@app.middleware("http")
async def log_real_requests_to_elk(request: Request, call_next):
    t0 = time.time()
    response = await call_next(request)
    ms = round((time.time() - t0) * 1000, 1)
    path = request.url.path.lower()
    if response.status_code >= 400 or ms > 3000:
        ltype, svc, ten = "app", "fastapi-prod", "acme-corp"
        if any(k in path for k in ("kpi", "login", "auth", "secret")): ltype, svc, ten = "auth", "core-backend", "globex"
        elif any(k in path for k in ("admin", "audit", "config")): ltype, svc, ten = "audit", "core-backend", "acme-corp"
        elif any(k in path for k in ("facture", "pay", "billing", "card")): ltype, svc, ten = "payment", "billing-saas", "initech"
        elif any(k in path for k in ("sql", "db", "data", "table")): ltype, svc, ten = "database", "postgres-primary", "globex"
        elif any(k in path for k in ("gateway", "rate", "waf")): ltype, svc, ten = "gateway", "api-gateway", "initech"
        elif any(k in path for k in ("job", "worker", "export", "upload")): ltype, svc, ten = "jobs", "celery-worker", "globex"
        elif any(k in path for k in ("ui", "page", "front", "checkout")): ltype, svc, ten = "frontend", "web-client", "acme-corp"
        elif any(k in path for k in ("cpu", "infra", "health", "server")): ltype, svc, ten = "infra", "worker-node-01", "acme-corp"
        payload = {"log_type": ltype, "level": "ERROR", "service": svc, "tenant_id": ten, "user_id": "usr-visitor", "status_code": response.status_code, "response_time_ms": ms, "duration_ms": ms, "cpu_pct": 91.5 if ltype=="infra" else 35.0, "msg": f"Real HTTP {response.status_code} on {request.method} {request.url.path}"}
        try:
            with socket.create_connection(("localhost", 5044), timeout=1) as s:
                s.sendall((js_elk.dumps(payload) + "\n").encode())
        except Exception:
            pass
    return response

from fastapi.staticfiles import StaticFiles
from api.enriched_routes import router as enriched_router
app.include_router(enriched_router)

@app.get("/api/alerts")
def alias_alerts(x_api_key: str = Header(None)):
    from api.enriched_routes import get_all_alerts
    return get_all_alerts(x_api_key)

app.mount("/", StaticFiles(directory="webapp", html=True), name="webapp")
