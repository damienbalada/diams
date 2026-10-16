"""Inventaire : pour chaque groupe racine qui a encore des indicateurs de rapport sans preuve ni trace,
y a-t-il un rapport annuel déposé au format ESEF (filings.xbrl.org) sous son LEI ? Résultat :
esef_inventaire.json {slug: {lei, depots: [(fin d'exercice, url)]}}."""
import json, os, sys, time
import httpx
sys.path.insert(0, r"C:/Users/damie/Downloads/claude/awareness-score/pipeline")
from diams import supabase_client

ICI = os.path.dirname(__file__)
OUT = os.path.join(ICI, "esef_inventaire.json")
RAPPORT = ["ENV_GHG_INTENSITY", "ENV_GHG_TREND", "ENV_SCOPE3_DISCLOSED", "LAB_GENDER_PAYGAP", "LAB_CEO_PAY_RATIO",
           "GOV_BOARD_GENDER", "GOV_BOARD_INDEP", "TAX_EFFECTIVE_RATE", "PLA_REDUCTION", "PLA_RECYCLED", "WAT_INTENSITY",
           "SUP_VIGILANCE_PLAN", "LAB_LIVING_WAGE", "SUP_SUPPLIER_LIST"]
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
g = supabase_client.get_all
ents = g(c, "entities", {"select": "id,slug,lei,siren,country,is_brand,parent_id"})
ind = {i["code"]: i["id"] for i in g(c, "indicators", {"select": "id,code"})}
have = {(r["entity_id"], r["indicator_id"]) for r in g(c, "evidence", {"select": "entity_id,indicator_id", "review_status": "eq.approved"})}
have |= {(r["entity_id"], r["indicator_id"]) for r in g(c, "indicator_reviews", {"select": "entity_id,indicator_id"})}
roots = [e for e in ents if not e["is_brand"] and not e["parent_id"]]
cibles = [e for e in roots if any((e["id"], ind[k]) not in have for k in RAPPORT)]
res = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
print(len(cibles), "groupes avec trous ;", sum(1 for e in cibles if e.get("lei")), "avec LEI")
for e in cibles:
    if e["slug"] in res or not e.get("lei"):
        res.setdefault(e["slug"], {"lei": None, "pays": e.get("country"), "depots": []}) if not e.get("lei") else None
        continue
    r = c.get("https://filings.xbrl.org/api/filings", params={"filter[entity.identifier]": e["lei"], "sort": "-period_end",
                                                              "page[size]": 5}, headers={"Accept": "application/vnd.api+json"})
    deps = []
    if r.status_code == 200:
        for f in r.json().get("data", []):
            a = f["attributes"]
            deps.append((a.get("period_end"), "https://filings.xbrl.org" + (a.get("report_url") or "")))
    res[e["slug"]] = {"lei": e["lei"], "pays": e.get("country"), "depots": deps}
    time.sleep(0.3)
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
avec2025 = [s for s, v in res.items() if any((d[0] or "").startswith("2025") for d in v["depots"])]
anciens = [s for s, v in res.items() if v["depots"] and s not in avec2025]
print("rapport ESEF 2025 :", len(avec2025), "·", "dépôts plus anciens seulement :", len(anciens),
      "· aucun dépôt :", sum(1 for v in res.values() if v["lei"] and not v["depots"]), "· sans LEI :", sum(1 for v in res.values() if not v["lei"]))
print("ESEF 2025 :", ", ".join(avec2025))
