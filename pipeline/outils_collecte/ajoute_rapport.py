"""ajoute_rapport.py <slug> <url> <source> "<intitulé du document>" [période=2025-12-31]
Déclare le rapport d'un groupe dans la chaîne de lecture et calcule ses indicateurs manquants."""
import json, sys
slug, url, src, doc = sys.argv[1:5]
pe = sys.argv[5] if len(sys.argv) > 5 else "2025-12-31"
e = json.load(open("esef_depots.json", encoding="utf-8"))
e[slug] = {"period_end": pe, "date_added": "2026-10-15", "report_url": url, "source": src, "doc": doc}
json.dump(e, open("esef_depots.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
m = json.load(open("manques_esef.json"))
m[slug] = ["GOV_BOARD_GENDER","GOV_BOARD_INDEP","LAB_CEO_PAY_RATIO","LAB_GENDER_PAYGAP","ENV_GHG_TREND","ENV_GHG_INTENSITY",
           "ENV_SCOPE3_DISCLOSED","TAX_EFFECTIVE_RATE","SUP_VIGILANCE_PLAN","ENV_TAXONOMY_CAPEX","PLA_REDUCTION","PLA_RECYCLED",
           "WAT_INTENSITY","LAB_LIVING_WAGE"]
json.dump(m, open("manques_esef.json", "w"), indent=1)
print("ok", slug)
