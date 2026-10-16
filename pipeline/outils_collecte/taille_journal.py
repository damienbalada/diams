"""Journal : pour chaque groupe racine de catégorie PME (répertoire Sirene, annuaire officiel des
entreprises), une note par indicateur tiré d'un rapport de durabilité ou de gestion, quand le groupe
n'a ni preuve ni note sur cet indicateur. Usage : taille_journal.py [--apply]"""
import json, os, sys
import httpx
sys.path.insert(0, r"C:/Users/damie/Downloads/claude/awareness-score/pipeline")
from diams import supabase_client
from diams.relecture import write_reviews

ICI = os.path.dirname(__file__)
TRANCHES = {"00": "0 salarié", "01": "1 ou 2 salariés", "02": "3 à 5 salariés", "03": "6 à 9 salariés",
            "11": "10 à 19 salariés", "12": "20 à 49 salariés", "21": "50 à 99 salariés", "22": "100 à 199 salariés",
            "31": "200 à 249 salariés", "32": "250 à 499 salariés", "41": "500 à 999 salariés"}
# Indicateurs dont la seule source est un rapport (état de durabilité, rapport de gestion, plan de
# vigilance, déclaration pays par pays) que la loi n'impose pas à une PME.
RAPPORT = ["ENV_GHG_INTENSITY", "ENV_GHG_TREND", "ENV_SCOPE3_DISCLOSED", "ENV_TAXONOMY_CAPEX", "LAB_GENDER_PAYGAP",
           "LAB_CEO_PAY_RATIO", "LAB_LIVING_WAGE", "GOV_BOARD_GENDER", "GOV_BOARD_INDEP", "TAX_EFFECTIVE_RATE",
           "TAX_CBCR_PUBLISHED", "PLA_REDUCTION", "PLA_RECYCLED", "WAT_INTENSITY", "SUP_VIGILANCE_PLAN", "SUP_SUPPLIER_LIST"]

cache = json.load(open(os.path.join(ICI, "taille_sirene.json"), encoding="utf-8"))
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
g = supabase_client.get_all
ents = {e["slug"]: e for e in g(c, "entities", {"select": "id,slug,siren"})}
ind = {i["code"]: i["id"] for i in g(c, "indicators", {"select": "id,code"})}
deja = {(r["entity_id"], r["indicator_id"]) for r in g(c, "evidence", {"select": "entity_id,indicator_id", "review_status": "eq.approved"})}
deja |= {(r["entity_id"], r["indicator_id"]) for r in g(c, "indicator_reviews", {"select": "entity_id,indicator_id"})
         if True}
rows = []
for siren, v in cache.items():
    if v.get("categorie_entreprise") != "PME" or v.get("etat_administratif") != "A":
        continue
    e = ents.get(v["slug"])
    if not e:
        continue
    eff = TRANCHES.get(v.get("tranche_effectif_salarie") or "", None)
    detail = (f"Catégorie d'entreprise : PME selon le répertoire Sirene de l'Insee ({v.get('annee_categorie_entreprise')}"
              + (f", {eff} en {v.get('annee_tranche_effectif_salarie')}" if eff else "")
              + ") : la loi n'impose pas à une PME de publier un rapport de durabilité, où figure cette donnée.")
    url = f"https://annuaire-entreprises.data.gouv.fr/entreprise/{siren}"
    for code in RAPPORT:
        if (e["id"], ind[code]) in deja:
            continue
        rows.append({"entity_id": e["id"], "indicator_id": ind[code], "evidence_id": None, "outcome": "non_trouvee",
                     "detail": detail, "source_url": url, "reviewer": "relecture:taille-sirene", "wave": None})
print(len(rows), "notes à écrire pour", len({r['entity_id'] for r in rows}), "PME")
if rows:
    print("exemple :", rows[0]["detail"])
if "--apply" in sys.argv and rows:
    print("écrites :", write_reviews(c, rows))
