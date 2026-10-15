"""Matrice des manques : groupes avec rapport réglementé × indicateurs lus dans les rapports."""
import os, sys, json
import httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client
S = os.path.dirname(os.path.abspath(__file__))
RAPPORT = ["GOV_BOARD_GENDER", "GOV_BOARD_INDEP", "LAB_CEO_PAY_RATIO", "LAB_GENDER_PAYGAP", "ENV_GHG_TREND",
           "ENV_GHG_INTENSITY", "ENV_SCOPE3_DISCLOSED", "TAX_EFFECTIVE_RATE", "SUP_VIGILANCE_PLAN",
           "ENV_TAXONOMY_CAPEX", "PLA_REDUCTION", "PLA_RECYCLED", "WAT_INTENSITY", "LAB_LIVING_WAGE", "SUP_SUPPLIER_LIST"]
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
g = supabase_client.get_all
ents = {e["slug"]: e for e in g(c, "entities", {"select": "id,slug,country"})}
ind = {i["code"]: i["id"] for i in g(c, "indicators", {"select": "id,code"})}
ev = {(e["entity_id"], e["indicator_id"]) for e in g(c, "evidence_active", {"select": "entity_id,indicator_id"})}
rv = {(r["entity_id"], r["indicator_id"]) for r in g(c, "indicator_reviews", {"select": "entity_id,indicator_id,outcome,reviewer", "or": "(outcome.in.(absence_confirmee,autre_forme),reviewer.eq.lecture-rapport)"})}
dep = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
out = {}
for slug in sorted(dep):
    e = ents[slug]
    m = [k for k in RAPPORT if (e["id"], ind[k]) not in ev and (e["id"], ind[k]) not in rv
         and not (k == "SUP_VIGILANCE_PLAN" and e.get("country") != "FR")]
    out[slug] = m
    print(f"{slug:26} {len(m):2}  {' '.join(x.split('_',1)[1] for x in m)}")
json.dump(out, open(os.path.join(S, "manques_esef.json"), "w", encoding="utf-8"), indent=1)
print(sum(len(v) for v in out.values()), "manques au total")
