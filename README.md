# Plateforme de monitoring et d'analyse de logs SaaS (stack ELK)

Mini-projet ITBS – Scénario D : Application Web SaaS (application monitorée fictive : **TaskFlow**).

## Objectif
Centraliser, indexer, rechercher et visualiser les logs d'une application SaaS, avec alerte DevOps
si le temps de réponse dépasse 3 secondes.

## Stack
Elasticsearch 8.x · Logstash 8.x · Kibana 8.x · MongoDB 7.x · Redis 7.x · Flask 3.x · Docker Compose

## Organisation
Scrum en solo, 6 semaines (Sprints 0 à 4). Backlog : onglet *Issues* de ce dépôt (labels S0 à S4).

## Structure
- `docs/` : analyse, KPI, architecture, bilans de sprint
- `webapp/` : application web (Flask)
- `logstash/pipeline/` : pipelines d'ingestion
- `elasticsearch/` : templates et mappings
- `kibana/exports/` : dashboards exportés
- `scripts/` : vérification des outils, génération de logs de test
- `tests/` : tests

## Démarrage
À compléter au Sprint 1.
