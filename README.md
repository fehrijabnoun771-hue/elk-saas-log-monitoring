# 🚀 Plateforme SaaS de Monitoring & d'Analyse de Logs (ELK + FastAPI + Redis + MongoDB)

Plateforme de supervision DevOps permettant de collecter 5 types de logs applicatifs (`access`, `auth`, `app`, `payment`, `system`), de les analyser en temps réel via la stack **ELK**, d'exposer les KPIs via une **API REST sécurisée** (accélérée par **Redis** et archivée dans **MongoDB**) et de déclencher des **alertes critiques (> 3 s)**.

## 🏗️ Architecture Technique
- **Collecte & Analyse :** Logstash (TCP `5044`), Elasticsearch (`9200`), Kibana (`5601`)
- **Backend & Stockage :** FastAPI (`8000`, clé `X-API-Key`), Cache Redis (`6379`), MongoDB (`27017`)
- **Alerting & Frontend :** Worker Python (`scripts/alert_worker.py`), Interface Web DevOps (`webapp/index.html`)

## ⚡ Guide de Démarrage Rapide (Démo)
1. **Démarrer l'infrastructure Docker :** `docker compose up -d`
2. **Générer les 5 types de logs :** `python3 scripts/generate_logs.py`
3. **Lancer le scan d'alertes (> 3s) :** `python3 scripts/alert_worker.py`
4. **Démarrer l'API & Webapp :** `uvicorn api.main:app --host 0.0.0.0 --port 8000`
5. **Exécuter les tests :** `python3 -m pytest -v`
