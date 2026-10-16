"""Relève, dans l'annuaire officiel des entreprises (recherche-entreprises.api.gouv.fr, données Insee),
la catégorie d'entreprise (PME, ETI, GE), la tranche d'effectif et quelques indicateurs publics de
chaque groupe racine français doté d'un SIREN. Résultat gardé en cache (taille_sirene.json)."""
import json, os, sys, time
import httpx
sys.path.insert(0, r"C:/Users/damie/Downloads/claude/awareness-score/pipeline")
from diams import supabase_client

ICI = os.path.dirname(__file__)
CACHE = os.path.join(ICI, "taille_sirene.json")
cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60)
ents = supabase_client.get_all(c, "entities", {"select": "id,slug,siren,is_brand,parent_id,country"})
roots = [e for e in ents if not e["is_brand"] and not e["parent_id"] and e.get("siren")]
print(len(roots), "groupes racines avec SIREN")
w = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60,
                 headers={"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)"})
n = 0
for e in roots:
    s = str(e["siren"])
    if s in cache:
        continue
    for essai in range(3):
        r = w.get("https://recherche-entreprises.api.gouv.fr/search", params={"q": s, "per_page": 3})
        if r.status_code == 429:
            time.sleep(5); continue
        break
    if r.status_code != 200:
        print("échec", e["slug"], r.status_code); continue
    hit = next((x for x in r.json().get("results", []) if x.get("siren") == s), None)
    cache[s] = {"slug": e["slug"]} | ({k: hit.get(k) for k in ["nom_complet", "categorie_entreprise", "annee_categorie_entreprise",
             "tranche_effectif_salarie", "annee_tranche_effectif_salarie", "etat_administratif"]}
             | {k: (hit.get("complements") or {}).get(k) for k in ["bilan_ges_renseigne", "egapro_renseignee", "est_societe_mission", "est_ess"]}
             if hit else {"absent": True})
    n += 1
    if n % 50 == 0:
        json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False); print(n)
    time.sleep(0.2)
json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
from collections import Counter
print(Counter(v.get("categorie_entreprise") for v in cache.values()))
