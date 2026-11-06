# KPI

| # | KPI | Source de log | Champs Elasticsearch | Visualisation Kibana | Seuil / alerte |
|---|-----|---------------|----------------------|----------------------|----------------|
| 1 | Temps de réponse moyen par endpoint | Performance / Nginx | endpoint, response_time_ms | Line chart | > 3000 ms : alerte DevOps |
| 2 | Taux d'erreur 5xx par service | Nginx / App | service, status_code | Area chart | > 2 % (à valider) |
| 3 | Requêtes SQL les plus lentes | Base de données | query, duration_ms | Top 10 (table) | > 1000 ms |
| 4 | Utilisateurs actifs simultanés | Usage métier | user_id, @timestamp | Metric (dernière heure) | informatif |
| 5 | Features les plus/moins utilisées | Usage métier | feature, action | Bar chart | informatif |

## Définitions
- KPI 1 : moyenne de `response_time_ms` groupée par `endpoint`, fenêtre 5 min.
- KPI 2 : nombre de `status_code` 500-599 / total des requêtes, par `service`, fenêtre 1 h.
- KPI 3 : top 10 des `duration_ms` décroissants, sur 24 h.
- KPI 4 : nombre de `user_id` distincts sur la dernière heure.
- KPI 5 : nombre d'événements par `feature` sur 7 jours.
