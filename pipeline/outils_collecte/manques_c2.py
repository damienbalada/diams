import os, sys, httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client
R = ["GOV_BOARD_GENDER","GOV_BOARD_INDEP","LAB_CEO_PAY_RATIO","LAB_GENDER_PAYGAP","ENV_GHG_TREND","ENV_GHG_INTENSITY","ENV_SCOPE3_DISCLOSED","TAX_EFFECTIVE_RATE","SUP_VIGILANCE_PLAN","ENV_TAXONOMY_CAPEX","PLA_REDUCTION","PLA_RECYCLED","WAT_INTENSITY","LAB_LIVING_WAGE"]
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120); g = supabase_client.get_all
ents = g(c, "entities", {"select": "id,slug,display_name,country,is_brand,parent_id,lei,siren"})
ind = {i["code"]: i["id"] for i in g(c, "indicators", {"select": "id,code"})}
ev = {(e["entity_id"], e["indicator_id"]) for e in g(c, "evidence_active", {"select": "entity_id,indicator_id"})}
rv = {(r["entity_id"], r["indicator_id"]) for r in g(c, "indicator_reviews", {"select": "entity_id,indicator_id", "or": "(outcome.in.(absence_confirmee,autre_forme),reviewer.eq.lecture-rapport)"})}
kids = {}
for e in ents:
    if e["parent_id"]: kids[e["parent_id"]] = kids.get(e["parent_id"], 0) + 1
for e in sorted(ents, key=lambda e: -kids.get(e["id"], 0)):
    if e["parent_id"] or kids.get(e["id"], 0) < 5: continue
    m = [k for k in R if (e["id"], ind[k]) not in ev and (e["id"], ind[k]) not in rv and not (k == "SUP_VIGILANCE_PLAN" and e.get("country") != "FR")]
    if len(m) >= 5:
        print(f"{e['slug']:24} {e.get('country') or '':3} {kids[e['id']]:3}m lei={'o' if e.get('lei') else '-'} {len(m):2} {' '.join(x.split('_',1)[1] for x in m)}")
