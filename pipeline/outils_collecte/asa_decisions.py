"""Allégations environnementales trompeuses au Royaume-Uni : décisions de l'ASA (Advertising Standards
Authority) retenant une plainte, de moins de cinq ans, pour les groupes et marques de l'Index.

Pour chaque entité : recherche des décisions par nom sur le site de l'ASA ; lecture de chaque décision
trouvée ; on garde celles dont l'annonceur porte nettement le nom de l'entité, dont l'issue est
« Upheld » (en tout ou en partie) et qui invoquent les règles sur les allégations environnementales
(code CAP, chapitre 11 ; code BCAP, chapitre 9). Les candidats sont relus à la main avant tout lot.
Délai de 2 secondes entre deux requêtes.

Usage : asa_decisions.py <dossier>   (cache asa_cache.json ; sortie asa_candidats.json ; reprise)
"""
import datetime as dt
import html
import json
import os
import re
import sys
import time

import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from diams import supabase_client  # noqa: E402
from diams.normalize.names import normalize_name  # noqa: E402

OUT = sys.argv[1]
CACHE = os.path.join(OUT, "asa_cache.json")
UA = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}
w = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60, headers=UA, follow_redirects=True)
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {"recherches": {}, "decisions": {}}
DEPUIS = (dt.date.today() - dt.timedelta(days=5 * 365)).isoformat()
MOIS = {m: i for i, m in enumerate("January February March April May June July August September October "
                                     "November December".split(), 1)}


def texte(p):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", p, flags=re.S)))


def decision(url):
    if url in cache["decisions"]:
        return cache["decisions"][url]
    time.sleep(2)
    try:
        t = texte(w.get(url).text)
    except httpx.HTTPError:
        return None
    m = re.search(r"ASA Ruling on (.+?) (Upheld in part|Upheld|Not upheld)\b.*? (\d{1,2}) (\w+) (\d{4})", t)
    d = None
    if m and m.group(4) in MOIS:
        d = f"{m.group(5)}-{MOIS[m.group(4)]:02d}-{int(m.group(3)):02d}"
    env = bool(re.search(r"CAP Code \(Edition 12\)[^.]{0,80}\b11\.\d|BCAP Code[^.]{0,60}\b9\.[1-5]\b|Environmental claims", t))
    v = {"annonceur": m.group(1) if m else None, "issue": m.group(2) if m else None, "date": d, "env": env}
    cache["decisions"][url] = v
    return v


ents = supabase_client.get_all(c, "entities", {"select": "slug,display_name,legal_name"})
cand = []
for n, e in enumerate(ents, 1):
    nom = (e.get("display_name") or e.get("legal_name") or "").strip()
    if len(nom) < 3:
        continue
    if nom not in cache["recherches"]:
        time.sleep(2)
        try:
            p = w.get("https://www.asa.org.uk/codes-and-rulings/rulings.html", params={"q": nom}).text
        except httpx.HTTPError:
            continue
        cache["recherches"][nom] = sorted(set(re.findall(r'href="(https://www\.asa\.org\.uk/rulings/[^"]+)"', p)))
    for u in cache["recherches"][nom]:
        v = decision(u)
        if not v or not v["annonceur"] or not v["date"] or v["date"] < DEPUIS:
            continue
        if not v["issue"].startswith("Upheld") or not v["env"]:
            continue
        a = normalize_name(re.sub(r"\bt/a\b.*", "", v["annonceur"]))
        if normalize_name(nom) and re.search(r"(?<![a-z0-9])" + re.escape(normalize_name(nom)) + r"(?![a-z0-9])", a):
            cand.append({"slug": e["slug"], "nom": nom, "url": u, **v})
    if n % 50 == 0:
        json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
        print(n, "entités", flush=True)
json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
json.dump(cand, open(os.path.join(OUT, "asa_candidats.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("fini :", len(cand), "décisions candidates ;", len({x["slug"] for x in cand}), "entités", flush=True)
