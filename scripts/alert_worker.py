import requests
from datetime import datetime, timezone
from pymongo import MongoClient

ES_URL = "http://localhost:9200/saas-logs-*/_search"
db = MongoClient("mongodb://localhost:27017")["saas_monitoring"]

query = {"size": 20, "query": {"range": {"response_time_ms": {"gt": 3000}}}}
hits = requests.post(ES_URL, json=query).json().get("hits", {}).get("hits", [])

db["alerts"].delete_many({})
for h in hits:
    src = h["_source"]
    alert = {
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "severity": "CRITICAL",
        "rule": "RESPONSE_TIME_GT_3S",
        "service": src.get("service"),
        "log_type": src.get("log_type"),
        "response_time_ms": src.get("response_time_ms"),
        "message": f"[DEVOPS ALERT] Slow response ({src.get('response_time_ms')} ms > 3000 ms) on {src.get('service')}"
    }
    db["alerts"].insert_one(alert)

print(f"Scan termine : {len(hits)} alertes critiques (> 3s) enregistrees dans MongoDB !")
