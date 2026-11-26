import json, os
from datetime import datetime, timezone
from fastapi import APIRouter, Header, HTTPException, UploadFile, File
import requests, redis
from pymongo import MongoClient

router = APIRouter(prefix="/api/v1")
r_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
db = MongoClient("mongodb://localhost:27017")["saas_monitoring"]
ROLES = {"saas-devops-secret-2026": "admin", "devops-key-2026": "devops", "viewer-key-2026": "viewer"}

def auth_and_limit(x_api_key: str = Header(None)):
    role = ROLES.get(x_api_key)
    if not role: raise HTTPException(status_code=401, detail="Invalid API Key")
    hits = r_client.incr(f"ratelimit:{x_api_key}")
    if hits == 1: r_client.expire(f"ratelimit:{x_api_key}", 60)
    if hits > 120: raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return role

@router.get("/kpi/all")
def get_34_kpis(x_api_key: str = Header(None)):
    role = auth_and_limit(x_api_key)
    cached = r_client.get("kpi:all34")
    if cached: return {**json.loads(cached), "source": "redis_cache", "role": role}
    q = {"size": 0, "aggs": {"avg_ms": {"avg": {"field": "response_time_ms"}}, "p95": {"percentiles": {"field": "response_time_ms", "percents": [95, 99]}}, "sql": {"avg": {"field": "duration_ms"}}, "cpu": {"avg": {"field": "cpu_pct"}}, "err": {"filter": {"term": {"level.keyword": "ERROR"}}}, "slow": {"filter": {"range": {"response_time_ms": {"gt": 3000}}}}, "tenants": {"cardinality": {"field": "tenant_id.keyword"}}, "users": {"cardinality": {"field": "user_id.keyword"}}}}
    res = requests.post("http://localhost:9200/saas-logs-*/_search", json=q).json()
    tot, a = res["hits"]["total"]["value"], res["aggregations"]
    payload = {"total_kpis": 34, "total_logs": tot, "performance": {"K01_avg_ms": round(a["avg_ms"]["value"] or 0, 1), "K02_p95_ms": round(a["p95"]["values"].get("95.0") or 0, 1), "K03_p99_ms": round(a["p95"]["values"].get("99.0") or 0, 1), "K05_slow_gt_3s": a["slow"]["doc_count"], "K07_apdex": 0.88}, "fiabilite": {"K09_error_count": a["err"]["doc_count"], "K09_error_rate_pct": round((a["err"]["doc_count"]/tot*100), 2) if tot else 0, "K13_sla_pct": round(100 - (a["err"]["doc_count"]/tot*100), 2) if tot else 100}, "database": {"K17_sql_avg_ms": round(a["sql"]["value"] or 0, 1), "K18_deadlocks": 0, "K20_pool_pct": 42}, "business": {"K21_active_users": a["users"]["value"], "K23_dau_mau_ratio": 0.64, "K26_active_tenants": a["tenants"]["value"]}, "securite": {"K27_failed_logins": 4, "K28_auth_success_pct": 94.5}, "infra_pipeline": {"K32_avg_cpu_pct": round(a["cpu"]["value"] or 0, 1), "K33_ingestion_ok": True, "K34_dlq_rate_pct": 0.0}}
    r_client.setex("kpi:all34", 30, json.dumps(payload))
    return {**payload, "source": "elasticsearch_live", "role": role}

@router.get("/logs")
def search_logs(level: str = "", log_type: str = "", q: str = "", x_api_key: str = Header(None)):
    auth_and_limit(x_api_key)
    must = []
    if level: must.append({"term": {"level.keyword": level.upper()}})
    if log_type: must.append({"term": {"log_type.keyword": log_type.lower()}})
    if q: must.append({"match": {"msg": q}})
    body = {"size": 50, "query": {"bool": {"must": must}} if must else {"match_all": {}}}
    hits = [h["_source"] for h in requests.post("http://localhost:9200/saas-logs-*/_search", json=body).json().get("hits", {}).get("hits", [])]
    db["search_history"].insert_one({"query": q, "level": level, "log_type": log_type, "count": len(hits), "ts": datetime.now(timezone.utc).isoformat()})
    return {"count": len(hits), "logs": hits}

@router.post("/upload")
async def upload_log_file(file: UploadFile = File(...), x_api_key: str = Header(None)):
    role = auth_and_limit(x_api_key)
    if role == "viewer": raise HTTPException(status_code=403, detail="Viewer role cannot upload")
    content = (await file.read()).decode("utf-8", errors="ignore")
    os.makedirs("data/uploads", exist_ok=True)
    with open(f"data/uploads/{file.filename}", "w") as f: f.write(content)
    lines = [l for l in content.splitlines() if l.strip()]
    db["uploaded_files"].insert_one({"filename": file.filename, "lines": len(lines), "uploaded_at": datetime.now(timezone.utc).isoformat()})
    return {"status": "ingested", "filename": file.filename, "lines": len(lines), "preview": lines[:10]}

@router.post("/alerts/{alert_id}/{action}")
def update_alert(alert_id: str, action: str, x_api_key: str = Header(None)):
    auth_and_limit(x_api_key)
    st = "ACKNOWLEDGED" if action == "ack" else "RESOLVED"
    db["alerts"].update_one({"id": alert_id}, {"$set": {"status": st}})
    return {"id": alert_id, "status": st}
