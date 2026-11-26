import requests, json

BASE = "http://localhost:5601/api"
H = {"kbn-xsrf": "true", "Content-Type": "application/json"}

dv_res = requests.get(f"{BASE}/data_views", headers=H).json()
dv_id = dv_res["data_view"][0]["id"]

SPECS = [
    ("01-perf-http", "01. Performance HTTP & Latence (K01-K04)", "response_time_ms", "average", "metric", ""),
    ("02-perf-slow", "02. Requetes Lentes > 3s (K05-K08)", "service.keyword", "count", "bar", "response_time_ms > 3000"),
    ("03-errors-5xx", "03. Fiabilite & Erreurs Critiques (K09-K12)", "service.keyword", "count", "pie", 'level: "ERROR"'),
    ("04-sla-levels", "04. Disponibilite SLA & Gravites (K13-K16)", "level.keyword", "count", "pie", ""),
    ("05-db-sql", "05. Base de Donnees & Requetes SQL (K17-K20)", "duration_ms", "average", "metric", 'log_type: "database"'),
    ("06-biz-tenants", "06. Usage Metier & Clients Tenants (K21-K26)", "tenant_id.keyword", "count", "pie", ""),
    ("07-biz-users", "07. Activite Utilisateurs SaaS (K21-K24)", "user_id.keyword", "count", "bar", ""),
    ("08-sec-auth", "08. Securite & Tentatives Auth (K27-K31)", "status_code", "count", "bar", 'log_type: "auth"'),
    ("09-audit-admin", "09. Audit & Conformite Admin (K29-K30)", "service.keyword", "count", "bar", 'log_type: "audit"'),
    ("10-billing-saas", "10. Transactions & Paiements SaaS (K25)", "level.keyword", "count", "pie", 'log_type: "payment"'),
    ("11-infra-cpu", "11. Infrastructure & Charge CPU (K32)", "cpu_pct", "average", "metric", ""),
    ("12-frontend-ux", "12. Experience Client & Frontend (K06)", "service.keyword", "count", "bar", 'log_type: "frontend"'),
    ("13-gateway-rate", "13. API Gateway & Rate Limiting (K31)", "status_code", "count", "pie", 'log_type: "gateway"'),
    ("14-jobs-workers", "14. Jobs Asynchrones & Pipeline (K33-K34)", "log_type.keyword", "count", "bar", ""),
    ("15-exec-34kpi", "15. Vue Executive Complete (34 KPI TaskFlow)", "tenant_id.keyword", "count", "bar", "")
]

for slug, title, field, op, vtype, kql in SPECS:
    vis_id = f"vis-{slug}"
    is_num = op == "average"
    cols = {
        "c1": {"label": title, "dataType": "number", "operationType": op, "sourceField": field if is_num else "___records___", "isBucketed": False, "scale": "ratio"}
    }
    col_order = ["c1"]
    if not is_num:
        cols["c0"] = {"label": field, "dataType": "string", "operationType": "terms", "sourceField": field, "isBucketed": True, "scale": "ordinal", "params": {"size": 10, "orderBy": {"type": "column", "columnId": "c1"}, "orderDirection": "desc"}}
        col_order = ["c0", "c1"]

    lens_body = {
        "attributes": {
            "title": f"Graph - {title}",
            "visualizationType": "lnsMetric" if vtype == "metric" else ("lnsPie" if vtype == "pie" else "lnsXY"),
            "state": {
                "visualization": {"shape": "donut", "layers": [{"layerId": "l1", "primaryGroups": ["c0"], "metrics": ["c1"]}]} if vtype == "pie" else ({"layerId": "l1", "metricAccessor": "c1"} if vtype == "metric" else {"preferredSeriesType": "bar", "layers": [{"layerId": "l1", "accessors": ["c1"], "xAccessor": "c0"}]}),
                "query": {"query": kql, "language": "kuery"},
                "filters": [],
                "datasourceStates": {"formBased": {"layers": {"l1": {"columns": cols, "columnOrder": col_order, "incompleteColumns": {}}}}}
            }
        },
        "references": [{"id": dv_id, "name": "indexpattern-datasource-layer-l1", "type": "index-pattern"}]
    }
    requests.post(f"{BASE}/saved_objects/lens/{vis_id}?overwrite=true", headers=H, json=lens_body)

    panels = [{"version": "8.11.0", "gridData": {"x": 0, "y": 0, "w": 48, "h": 15, "i": "1"}, "panelIndex": "1", "embeddableConfig": {"enhancements": {}}, "panelRefName": "panel_1"}]
    dash_body = {
        "attributes": {"title": title, "panelsJSON": json.dumps(panels), "optionsJSON": "{\"useMargins\":true}", "timeRestore": True, "timeFrom": "now-24h", "timeTo": "now"},
        "references": [{"name": "panel_1", "type": "lens", "id": vis_id}]
    }
    r = requests.post(f"{BASE}/saved_objects/dashboard/dash-{slug}?overwrite=true", headers=H, json=dash_body)
    print(f"{title} -> HTTP {r.status_code}")
