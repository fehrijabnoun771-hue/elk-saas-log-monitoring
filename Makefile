seed:
	python3 scripts/generate_logs.py
reset:
	curl -s -X DELETE "http://localhost:9200/saas-logs-*" && python3 scripts/generate_logs.py
