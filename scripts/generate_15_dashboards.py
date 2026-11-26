import requests, json, copy

BASE = "http://localhost:5601/api"
H = {"kbn-xsrf": "true", "Content-Type": "application/json"}

lens_list = requests.get(f"{BASE}/saved_objects/_find?type=lens", headers=H).json()["saved_objects"]
pie_tmpl = next(x for x in lens_list if x["attributes"]["visualizationType"] == "lnsXY")
pie_tmpl = next(x for x in lens_list if x["attributes"]["visualizationType"] == "lnsPie")

DASH_DEFS = [
    ("01-perf-http", "01. Performance HTTP & Latence (K01-K04)", "service.keyword", "level.keyword", "bar", ""),
    ("02-perf-slow", "02. Requetes Lentes > 3s (K05-K08)", "service.keyword", "tenant_id.keyword", "donut", "response_time_ms > 3000"),
    ("03-errors-5xx", "03. Fiabilite & Erreurs Critiques (K09-K12)", "service.keyword", "log_type.keyword", "donut", 'level.keyword: "ERROR"'),
    ("04-sla-levels", "04. Disponibilite SLA & Gravites (K13-K16)", "level.keyword", "service.keyword", "bar", ""),
    ("05-db-sql", "05. Base de Donnees & Requetes SQL (K17-K20)", "tenant_id.keyword", "user_id.keyword", "donut", 'log_type.keyword: "database"'),
    ("06-biz-tenants", "06. Usage Metier & Clients Tenants (K21-K26)", "tenant_id.keyword", "log_type.keyword", "bar", ""),
    ("07-biz-users", "07. Activite Utilisateurs SaaS (K21-K24)", "user_id.keyword", "tenant_id.keyword", "bar", ""),
    ("08-sec-auth", "08. Securite & Tentatives Auth (K27-K31)", "level.keyword", "service.keyword", "donut", 'log_type.keyword: "auth"'),
    ("09-audit-admin", "09. Audit & Conformite Admin (K29-K30)", "user_id.keyword", "tenant_id.keyword", "bar", 'log_type.keyword: "audit"'),
    ("10-billing-saas", "10. Transactions & Paiements SaaS (K25)", "tenant_id.keyword", "level.keyword", "donut", 'log_type.keyword: "payment"'),
    ("11-infra-cpu", "11. Infrastructure & Charge CPU (K32)", "tenant_id.keyword", "service.keyword", "bar", "cpu_pct > 50"),
    ("12-frontend-ux", "12. Experience Client & Frontend (K06)", "tenant_id.keyword", "user_id.keyword", "donut", 'log_type.keyword: "frontend"'),
    ("13-gateway-rate", "13. API Gateway & Rate Limiting (K31)", "tenant_id.keyword", "level.keyword", "bar", 'log_type.keyword: "gateway"'),
    ("14-jobs-workers", "14. Jobs Asynchrones & Pipeline (K33-K34)", "log_type.keyword", "level.keyword", "bar", ""),
    ("15-exec-34kpi", "15. Vue Executive Complete (34 KPI TaskFlow)", "log_type.keyword", "tenant_id.keyword", "donut", "")
]

def make_vis(vid, title, field, base_obj, is_donut=False):
    obj = copy.deepcopy(base_obj)
    obj["attributes"]["title"] = title
    st = obj["attributes"]["state"]
    layer_id = next(iter(st["datasourceStates"]["formBased"]["layers"]))
    cols = st["datasourceStates"]["formBased"]["layers"][layer_id]["columns"]
    for cid, c in cols.items():
        if c.get("isBucketed"):
            c["sourceField"] = field
            c["label"] = field
    if is_donut:
        st["visualization"]["shape"] = "donut" if is_donut else "pie"
    requests.post(f"{BASE}/saved_objects/lens/{vid}?overwrite=true", headers=H, json={"attributes": obj["attributes"], "references": obj["references"]})

for slug, title, f1, f2, style, kql in DASH_DEFS:
    v1, v2 = f"v1-{slug}", f"v2-{slug}"
    make_vis(v1, f"{title} - Principal", f1, pie_tmpl if style == "donut" else pie_tmpl, style == "donut")
    make_vis(v2, f"{title} - Detail", f2, pie_tmpl if style == "donut" else pie_tmpl, style != "donut")
    panels = [
        {"version": "8.11.0", "gridData": {"x": 0, "y": 0, "w": 24, "h": 15, "i": "1"}, "panelIndex": "1", "embeddableConfig": {"enhancements": {}}, "panelRefName": "p1"},
        {"version": "8.11.0", "gridData": {"x": 24, "y": 0, "w": 24, "h": 15, "i": "2"}, "panelIndex": "2", "embeddableConfig": {"enhancements": {}}, "panelRefName": "p2"}
    ]
    dash_attr = {
        "title": title, "panelsJSON": json.dumps(panels), "optionsJSON": "{\"useMargins\":true,\"syncColors\":true}",
        "timeRestore": True, "timeFrom": "now-15y", "timeTo": "now",
        "kibanaSavedObjectMeta": {"searchSourceJSON": json.dumps({"query": {"query": kql, "language": "kuery"}, "filter": []})}
    }
    refs = [{"name": "p1", "type": "lens", "id": v1}, {"name": "p2", "type": "lens", "id": v2}]
    r = requests.post(f"{BASE}/saved_objects/dashboard/dash-{slug}?overwrite=true", headers=H, json={"attributes": dash_attr, "references": refs})
    print(f"{title} -> HTTP {r.status_code}")
