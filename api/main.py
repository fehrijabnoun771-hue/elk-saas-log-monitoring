import os, json, time
from datetime import datetime, timezone
from fastapi import FastAPI, Header, HTTPException
import requests, redis
from pymongo import MongoClient

app = FastAPI(title="SaaS ELK Monitoring KPI API")
API_KEY = os.getenv("API_KEY", "saas-devops-secret-2026")
r_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
db = MongoClient("mongodb://localhost:27017")["saas_monitoring"]

@app.get("/api/health")
def health():
    return {"status": "ok", "redis": r_client.ping(), "mongodb": db.command("ping").get("ok") == 1.0}

@app.get("/api/kpis")
def get_kpis(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")
    start = time.time()
    cached = r_client.get("kpi_summary")
    if cached:
        data = json.loads(cached)
        data["source"] = "redis_cache"
        data["api_latency_ms"] = round((time.time() - start) * 1000, 2)
        return data
    query = {"size": 0, "aggs": {"avg_ms": {"avg": {"field": "response_time_ms"}}, "err": {"filter": {"term": {"level.keyword": "ERROR"}}}, "slow": {"filter": {"range": {"response_time_ms": {"gt": 3000}}}}}}
    res = requests.post("http://localhost:9200/saas-logs-*/_search", json=query).json()
    total, aggs = res["hits"]["total"]["value"], res["aggregations"]
    errors = aggs["err"]["doc_count"]
    kpis = {"timestamp": datetime.now(timezone.utc).isoformat(), "total_logs": total, "error_count": errors, "error_rate_pct": round((errors / total * 100), 2) if total else 0, "avg_response_time_ms": round(aggs["avg_ms"]["value"] or 0, 2), "slow_requests_gt_3s": aggs["slow"]["doc_count"]}
    db["kpi_snapshots"].insert_one(kpis.copy())
    r_client.setex("kpi_summary", 30, json.dumps(kpis))
    kpis["source"], kpis["api_latency_ms"] = "elasticsearch_live", round((time.time() - start) * 1000, 2)
    return kpis

from fastapi.responses import FileResponse

@app.get("/api/alerts")
def get_alerts(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")
    alerts = list(db["alerts"].find({}, {"_id": 0}).limit(20))
    return {"total_alerts": len(alerts), "threshold_ms": 3000, "alerts": alerts}

@app.get("/")
def serve_webapp():
    return FileResponse("webapp/index.html")
