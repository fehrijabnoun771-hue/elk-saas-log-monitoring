import requests
from datetime import datetime, timezone
from pymongo import MongoClient

db = MongoClient("mongodb://localhost:27017")["saas_monitoring"]
RULES = [
    ("R1_LATENCY_GT_3S", "CRITICAL", {"range": {"response_time_ms": {"gt": 3000}}}, "Latence HTTP > 3000 ms"),
    ("R2_ERROR_BURST", "CRITICAL", {"term": {"level.keyword": "ERROR"}}, "Erreur applicative critique (5xx)"),
    ("R3_SQL_SLOW", "WARNING", {"range": {"duration_ms": {"gt": 2000}}}, "Requete SQL lente > 2000 ms"),
    ("R4_CPU_HIGH", "WARNING", {"range": {"cpu_pct": {"gt": 85}}}, "Saturation CPU > 85 %"),
    ("R5_AUTH_FAIL", "WARNING", {"term": {"status_code": 401}}, "Tentative auth echouee (401)"),
    ("R6_PAYMENT_ERR", "CRITICAL", {"term": {"status_code": 402}}, "Echec paiement SaaS (402)"),
    ("R7_RATE_LIMIT", "INFO", {"term": {"status_code": 429}}, "Seuil Rate Limit atteint (429)"),
    ("R8_DLQ_CHECK", "INFO", {"term": {"log_type.keyword": "unknown"}}, "Log non classe detecte")
]
db["alerts"].delete_many({})
total = 0
for code, sev, q, label in RULES:
    hits = requests.post("http://localhost:9200/saas-logs-*/_search", json={"size": 3, "query": q}).json().get("hits", {}).get("hits", [])
    for h in hits:
        total += 1
        db["alerts"].insert_one({"id": f"ALT-{total:03d}", "rule": code, "severity": sev, "status": "ACTIVE", "service": h["_source"].get("service"), "message": f"[{code}] {label} sur {h['_source'].get('service')}", "detected_at": datetime.now(timezone.utc).isoformat()})
print(f"Scan 8 regles termine : {total} alertes enregistrees avec cycle de vie !")
