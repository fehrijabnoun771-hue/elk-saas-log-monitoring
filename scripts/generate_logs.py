import socket, json, time, random
from datetime import datetime, timezone

TYPES = [
    ("web", "nginx", "INFO", 200, "GET /api/v1/tasks 200"),
    ("app", "taskflow-core", "ERROR", 500, "NullPointerException in workflow"),
    ("database", "postgres-main", "WARN", 200, "Slow SQL query SELECT * FROM tasks"),
    ("performance", "api-gateway", "WARN", 200, "High endpoint latency"),
    ("business", "taskflow-app", "INFO", 200, "Feature kanban_board used"),
    ("auth", "auth-service", "WARN", 401, "Failed login attempt"),
    ("audit", "admin-panel", "INFO", 200, "Admin updated tenant quota"),
    ("payment", "billing-saas", "ERROR", 402, "Subscription payment failed"),
    ("gateway", "kong-gateway", "WARN", 429, "Rate limit triggered"),
    ("jobs", "redis-worker", "INFO", 200, "Export report job completed"),
    ("infra", "docker-node1", "WARN", 200, "Container CPU spike"),
    ("frontend", "web-client", "ERROR", 500, "TypeError: Cannot read properties of undefined")
]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 5044))
for i in range(120):
    t, svc, lvl, code, msg = random.choice(TYPES)
    doc = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "log_type": t, "service": svc, "level": lvl, "status_code": code, "msg": msg,
        "tenant_id": random.choice(["acme-corp", "globex", "initech"]),
        "user_id": f"user_{random.randint(1, 25)}", "client_ip": f"192.168.1.{random.randint(10, 50)}",
        "response_time_ms": random.choice([120, 450, 1200, 3500, 4200]),
        "duration_ms": random.choice([15, 80, 350, 1200, 2500]),
        "cpu_pct": random.choice([35.0, 62.5, 89.4]), "app_version": "2.0.0"
    }
    sock.sendall((json.dumps(doc) + "\n").encode("utf-8"))
    time.sleep(0.03)
sock.close()
print("120 logs enrichis (12 types TaskFlow) envoyes avec succes !")
