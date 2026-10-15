"""ajoute_rapport.py <slug> <url> <source> "<intitulé du document>" [période=2025-12-31]
Déclare le rapport d'un groupe dans la chaîne de lecture et retient ses VRAIS manques : les
indicateurs sans preuve approuvée et sans lecture déjà consignée (absence confirmée, autre forme,
lecture de rapport). Évite les doublons (leçon du 15/10/2026)."""
import json
import os
import sys

import httpx

sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client  # noqa: E402

TOUS = ["GOV_BOARD_GENDER", "GOV_BOARD_INDEP", "LAB_CEO_PAY_RATIO", "LAB_GENDER_PAYGAP", "ENV_GHG_TREND", "ENV_GHG_INTENSITY",
        "ENV_SCOPE3_DISCLOSED", "TAX_EFFECTIVE_RATE", "SUP_VIGILANCE_PLAN", "ENV_TAXONOMY_CAPEX", "PLA_REDUCTION", "PLA_RECYCLED",
        "WAT_INTENSITY", "LAB_LIVING_WAGE"]

slug, url, src, doc = sys.argv[1:5]
pe = sys.argv[5] if len(sys.argv) > 5 else "2025-12-31"
e = json.load(open("esef_depots.json", encoding="utf-8"))
e[slug] = {"period_end": pe, "date_added": "2026-10-15", "report_url": url, "source": src, "doc": doc}
json.dump(e, open("esef_depots.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60)
g = supabase_client.get_all
ent = g(c, "entities", {"select": "id,country", "slug": f"eq.{slug}"})[0]
ind = {i["id"]: i["code"] for i in g(c, "indicators", {"select": "id,code"})}
pris = {ind[x["indicator_id"]] for x in g(c, "evidence_active", {"select": "indicator_id", "entity_id": f"eq.{ent['id']}"})}
pris |= {ind[x["indicator_id"]] for x in g(c, "indicator_reviews", {"select": "indicator_id", "entity_id": f"eq.{ent['id']}",
         "or": "(outcome.in.(absence_confirmee,autre_forme),reviewer.eq.lecture-rapport)"})}
m = json.load(open("manques_esef.json", encoding="utf-8"))
m[slug] = [k for k in TOUS if k not in pris and not (k == "SUP_VIGILANCE_PLAN" and ent.get("country") != "FR")]
json.dump(m, open("manques_esef.json", "w", encoding="utf-8"), indent=1)
print("manques réels", slug, ":", " ".join(m[slug]) or "aucun")
