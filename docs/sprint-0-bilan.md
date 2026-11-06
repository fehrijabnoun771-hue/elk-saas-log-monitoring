# Bilan Sprint 0

## Ce qui a été fait
- Analyse fonctionnelle, KPI, architecture
- Dépôt GitHub, structure, backlog de 12 issues
- Environnement vérifié (Docker, Docker Compose, Python, GitHub CLI)

## Ce qui a bloqué
- Installation des outils interrompue (^C) : paquets Docker, pip, venv et gh à reprendre
- Elasticsearch, Logstash et Kibana déjà installés en natif, Elasticsearch avec la sécurité désactivée (HTTP sans mot de passe)
- Erreurs dans mon script de vérification des documents (regex des user stories, backticks dans un message), corrigées
- Option gh inconnue dans la version installée : passage du dépôt en public sans cette option

## Ajustements pour le Sprint 1
- Arrêter Elasticsearch et Kibana natifs (inactifs) : les services tournent dans Docker
- Limiter la mémoire des conteneurs (VM : 8,6 Go de RAM, 2 coeurs)

## Sprint 1 : tâches choisies
3. Lancer la stack ELK (Docker) · 4. Générer des logs de test · 5. Pipelines Logstash (5 types)
