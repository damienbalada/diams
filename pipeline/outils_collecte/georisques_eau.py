"""Controverses sur l'eau : arrêtés préfectoraux de mise en demeure des installations classées
(Géorisques, Licence Ouverte) dont le texte porte sur l'eau (rejets, effluents, station d'épuration,
prélèvements, pollution d'un cours d'eau).

Pour chaque société française de l'Index (SIREN et raison sociale de l'annuaire officiel) : recherche
des installations classées par raison sociale, en ne gardant que les établissements dont le SIRET
commence par le SIREN ; lecture des arrêtés « AP mise en demeure » des cinq dernières années ; un
arrêté est retenu si son texte contient un passage sur l'eau, cité mot pour mot.

Usage : georisques_eau.py <dossier> <taille_sirene.json>   (cache georisques_cache.json ; reprise)
"""
import datetime as dt, json, os, re, sys, time
import httpx

OUT, TAILLE = sys.argv[1], sys.argv[2]
CACHE = os.path.join(OUT, "georisques_cache.json")
UA = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}
w = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120, headers=UA, follow_redirects=True)
cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
societes = json.load(open(TAILLE, encoding="utf-8"))
DEPUIS = (dt.date.today() - dt.timedelta(days=5 * 365)).isoformat()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from diams.ocr import pdf_text_or_ocr, loose_pattern
# Thèmes de l'eau, cherchés sans tenir compte des accents ni des espaces perdus par l'OCR.
THEMES = ["rejets aqueux", "rejet aqueux", "eaux usées", "eaux résiduaires", "eaux pluviales", "effluents", "effluent",
          "station d'épuration", "prélèvement d'eau", "prélèvements d'eau", "cours d'eau", "milieu aquatique",
          "pollution des eaux", "rejets dans le milieu", "rejet dans le milieu naturel"]
EAU = re.compile("|".join(loose_pattern(t).replace("'", "[’'\s]?") for t in THEMES), re.I)
def texte_pdf(url):
    r = w.get(url)
    if r.status_code != 200 or b"%PDF" not in r.content[:1024]:
        return None, False
    try:
        return pdf_text_or_ocr(r.content)
    except Exception:
        return None, False


def phrase(t, m):
    """Phrase entière autour du thème trouvé, telle que reconnue (bornée aux signes de ponctuation)."""
    i = max(t.rfind(".", 0, m.start()), t.rfind(";", 0, m.start()), t.rfind(":", 0, m.start()), m.start() - 300)
    j_candidats = [k for k in (t.find(".", m.end()), t.find(";", m.end())) if k != -1]
    j = min(j_candidats + [m.end() + 300])
    return t[i + 1:j].strip()


for n, (siren, v) in enumerate(societes.items(), 1):
    if v.get("slug") in cache or not v.get("nom_complet") or v.get("etat_administratif") != "A":
        continue
    nom = re.sub(r"\s*\(.*?\)\s*", " ", v["nom_complet"]).strip()
    nom = nom.split(" - ")[0].strip()
    sites, page = [], 1
    while page <= 10:
        try:
            d = w.get("https://georisques.gouv.fr/api/v1/installations_classees",
                      params={"raisonSociale": nom, "page": page, "page_size": 100}).json()
        except Exception:
            break
        sites += [s for s in d.get("data", []) if (s.get("siret") or "").startswith(siren)]
        if page >= d.get("total_pages", 1):
            break
        page += 1
        time.sleep(0.3)
    arretes = []
    for s in sites:
        for doc in s.get("documentsHorsInspection") or []:
            if "demeure" not in (doc.get("typeFichier") or "").lower():
                continue
            date = doc.get("dateFichier") or ""
            if date and date < DEPUIS:
                continue
            t, ocr = texte_pdf(doc["urlFichier"]) if doc.get("urlFichier") else (None, False)
            time.sleep(0.3)
            m = EAU.search(t or "")
            arretes.append({"siret": s["siret"], "commune": s.get("commune"), "date": date, "nom": doc.get("nomFichier"),
                            "url": doc.get("urlFichier"), "lisible": bool(t), "ocr": ocr,
                            "eau": phrase(t, m) if m else None, "theme": m.group(0) if m else None})
    cache[v["slug"]] = {"siren": siren, "nom": nom, "sites": len(sites), "arretes": arretes}
    if n % 20 == 0:
        json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False); print(n, "sociétés")
json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
print("fini :", len(cache), "sociétés ;", sum(1 for v in cache.values() if any(a["eau"] for a in v["arretes"])), "avec un arrêté sur l'eau")
