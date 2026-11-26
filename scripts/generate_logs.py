import socket, json, time, random
from datetime import datetime, timezone

LOG_TYPES = [
    {"log_type": "access",  "service": "api-gateway",  "level": "INFO",  "msg": "GET /api/v1/kpis 200 OK"},
    {"log_type": "auth",    "service": "auth-service", "level": "WARN",  "msg": "Failed login attempt for user admin"},
    {"log_type": "app",     "service": "core-backend", "level": "ERROR", "msg": "NullPointerException in report generator"},
    {"log_type": "payment", "service": "billing-saas", "level": "INFO",  "msg": "Pro plan subscription invoice #4092 paid"},
    {"log_type": "system",  "service": "ubuntu-node1", "level": "WARN",  "msg": "High CPU usage detected (88%)"}
]

RESPONSE_TIMES = [120, 250, 480, 950, 1500, 3500, 4200]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 5044))

for i in range(50):
    entry = random.choice(LOG_TYPES).copy()
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    entry["response_time_ms"] = random.choice(RESPONSE_TIMES)
    sock.sendall((json.dumps(entry) + "\n").encode("utf-8"))
    time.sleep(0.1)

sock.close()
print("50 logs (5 types) envoyes avec succes vers Logstash !")
