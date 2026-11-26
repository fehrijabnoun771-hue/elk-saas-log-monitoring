# Spécifications Enrichies TaskFlow (S0 - Tâches 13 à 17)
- **Application monitorée :** TaskFlow (SaaS multi-tenant)
- **Périmètre enrichi :** 50 tâches Scrum, 34 KPI (6 familles), 12 types de logs, 8 règles d'alerte (R1-R8), 5 dashboards Kibana, interface web 5 pages.
- **Modèle de données :**
  - Elasticsearch : `saas-logs-{type}-YYYY.MM.dd` + `saas-logs-failed` (DLQ)
  - MongoDB : `kpi_snapshots`, `alerts`, `uploaded_files`, `search_history`, `saved_dashboards`
  - Redis : `kpi:*` (TTL 30s), `ratelimit:*` (TTL 60s)
