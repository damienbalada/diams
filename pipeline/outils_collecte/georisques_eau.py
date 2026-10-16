"""Controverses sur l'eau : arrêtés préfectoraux de mise en demeure des installations classées
(Géorisques, Licence Ouverte) dont le texte porte sur l'eau (rejets, effluents, station d'épuration,
prélèvements, pollution d'un cours d'eau).

Pour chaque société française de l'Index (SIREN et raison sociale de l'annuaire officiel) : recherche
des installations classées par raison sociale, en ne gardant que les établissements dont le SIRET
commence par le SIREN ; lecture des arrêtés « AP mise en demeure » des cinq dernières années ; un
arrêté est retenu si son texte contient un passage sur l'eau, cité mot pour mot.

Usage : georisques_eau.py <dossier> <taille_sirene.json>   (cache georisques_cache.json ; reprise)
"""
import datetime as dt, io, json, logging, os, re, sys, time
import httpx

OUT, TAILLE = sys.argv[1], sys.argv[2]
CACHE = os.path.join(OUT, "georisques_cache.json")
UA = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}
w = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120, headers=UA, follow_redirects=True)
cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
societes = json.load(open(TAILLE, encoding="utf-8"))
DEPUIS = (dt.date.today() - dt.timedelta(days=5 * 365)).isoformat()
EAU = re.compile(r"[^.;:]{0,200}\b(rejets? (?:aqueux|d.eaux|dans le milieu|au milieu)|eaux (?:usées|résiduaires|pluviales)|effluents?|station d.épuration|"
                 r"prélèvements? d.eau|cours d.eau|milieu aquatique|pollution (?:des eaux|de la rivière|du ruisseau))\b[^.;]{0,200}", re.I)
logging.getLogger("pypdf").setLevel(logging.ERROR)


def texte_pdf(url):
    import pypdf
    r = w.get(url)
    if r.status_code != 200 or b"%PDF" not in r.content[:1024]:
        return None
    try:
        return re.sub(r"\s+", " ", " ".join((p.extract_text() or "") for p in pypdf.PdfReader(io.BytesIO(r.content)).pages))
    except Exception:
        return None


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
            t = texte_pdf(doc["urlFichier"]) if doc.get("urlFichier") else None
            time.sleep(0.3)
            m = EAU.search(t or "")
            arretes.append({"siret": s["siret"], "commune": s.get("commune"), "date": date, "nom": doc.get("nomFichier"),
                            "url": doc.get("urlFichier"), "lisible": t is not None,
                            "eau": m.group(0).strip() if m else None})
    cache[v["slug"]] = {"siren": siren, "nom": nom, "sites": len(sites), "arretes": arretes}
    if n % 20 == 0:
        json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False); print(n, "sociétés")
json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
print("fini :", len(cache), "sociétés ;", sum(1 for v in cache.values() if any(a["eau"] for a in v["arretes"])), "avec un arrêté sur l'eau")
