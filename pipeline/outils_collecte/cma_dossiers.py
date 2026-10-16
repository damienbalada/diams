"""Sanctions de la CMA (Competition and Markets Authority, Royaume-Uni ; Open Government Licence) :
dossiers clos depuis cinq ans dont l'issue est une infraction au Competition Act 1998 (chapitres I ou
II), une décision de justice ou des engagements en droit de la consommation. Pour chaque dossier, le
texte de la page (API de contenu de gov.uk) est cherché pour les noms des groupes racines de l'Index
(nom entier, mot pour mot) ; les candidats sont relus à la main avant tout lot de preuves.

Usage : cma_dossiers.py <dossier>   (cache cma_cache.json ; sortie cma_candidats.json)
"""
import datetime as dt, html, json, os, re, sys, time
import httpx
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from diams import supabase_client

OUT = sys.argv[1]
CACHE = os.path.join(OUT, "cma_cache.json")
UA = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}
w = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60, headers=UA, follow_redirects=True)
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60)
cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
DEPUIS = (dt.date.today() - dt.timedelta(days=5 * 365)).isoformat()
ISSUES = {"ca98-infringement-chapter-i", "ca98-infringement-chapter-ii", "consumer-enforcement-court-order",
          "consumer-enforcement-undertakings", "consumer-enforcement-changes-to-business-practices-agreed"}
dossiers = []
for t in ("ca98-and-civil-cartels", "consumer-enforcement"):
    d = w.get("https://www.gov.uk/api/search.json", params={"filter_format": "cma_case", "filter_case_type": t,
              "count": 1000, "fields": "title,link,closed_date,outcome_type,case_state"}).json()
    dossiers += [r for r in d["results"] if r.get("outcome_type") in ISSUES and (r.get("closed_date") or "9") >= DEPUIS]
print(len(dossiers), "dossiers retenus")
for r in dossiers:
    if r["link"] in cache:
        continue
    time.sleep(0.5)
    j = w.get("https://www.gov.uk/api/content" + r["link"]).json()
    corps = j.get("details", {}).get("body") or ""
    texte = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", corps)))
    cache[r["link"]] = {"titre": r["title"], "clos": r.get("closed_date"), "issue": r.get("outcome_type"), "texte": texte}
json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)

ents = supabase_client.get_all(c, "entities", {"select": "slug,display_name,legal_name,is_brand,parent_id"})
roots = [e for e in ents if not e["is_brand"] and not e["parent_id"]]
cand = []
for e in roots:
    noms = {n for n in (e["display_name"], e.get("legal_name")) if n and len(n) >= 4}
    for lien, v in cache.items():
        hay = v["titre"] + " " + v["texte"]
        for n in noms:
            m = re.search(r"(?<![\w-])" + re.escape(n) + r"(?![\w-])", hay)
            if m:
                cand.append({"slug": e["slug"], "nom": n, "lien": "https://www.gov.uk" + lien, "titre": v["titre"],
                             "clos": v["clos"], "issue": v["issue"],
                             "extrait": hay[max(0, m.start() - 200):m.end() + 200]})
                break
json.dump(cand, open(os.path.join(OUT, "cma_candidats.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(cand), "candidats ;", len({x["slug"] for x in cand}), "groupes")
