# 🚀 TaskFlow SaaS ELK Monitoring Platform (v2.0.0)

Plateforme complète de supervision DevOps et d'analyse applicative **TaskFlow** couvrant **12 types de logs**, **34 KPI (6 familles)**, **8 règles d'alerte (R1-R8)**, une **API REST sécurisée (RBAC + Rate Limiting Redis)** et une **Interface Web 5 pages**.

## 🏗️ Architecture & Démarrage
1. **Infrastructure Docker :** `docker compose up -d` (Elasticsearch, Logstash, Kibana, MongoDB, Redis)
2. **Génération des 12 types de logs :** `make seed`
3. **Worker d'alerte 8 règles (R1-R8) :** `python3 scripts/alert_worker.py`
4. **API & Interface Web 5 pages :** `uvicorn api.main:app --host 0.0.0.0 --port 8000`
5. **Tests automatisés (E2E) :** `python3 -m pytest -v`
