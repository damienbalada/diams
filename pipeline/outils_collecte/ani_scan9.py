"""ani_scan9 (16/10/2026) : comme ani_scan8, sur les sites officiels prouvés par trouve_sites_logos.py
(pipeline/curated/sites_officiels_logos_2026-10-16.csv), pour les seules marques dont l'exploitation
animale n'est que présumée. Identité déclarée du vérificateur.
Balaye les sites officiels confirmés par SIREN : accueil + pages produits ; relève
les phrases contenant un mot-clé d'exploitation animale (hors « sans … ») ou une
mention vegan, pour relecture à la main."""
import json, re, os, sys, html
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
import httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
from diams.verify_curated import ESEF_KEYWORDS
sys.stdout.reconfigure(encoding="utf-8")
ANI = re.compile(ESEF_KEYWORDS["ANI_EXPLOITATION"][0], re.I)
VEG = re.compile(r"\bvegan\b|v[ée]g[ée]talien|100 ?% v[ée]g[ée]tal|sans ingr[ée]dient d.origine animale", re.I)
NEG = re.compile(r"\b(sans|aucun|z[ée]ro|ni|free|alternative|substitut|remplace|v[ée]g[ée]tal)\b", re.I)
PROD = re.compile(r"produit|gamme|recette|nos-|boutique|shop|collection|catalogue|categorie|category|product|fromage|biscuit|saveur", re.I)
EXCLUS = set("valade toupargel-marque landreau-marque happy-hours-en-biovallee-marque french-desserts-marque fiona-marque mutti instant-healthy-marque veri-good-marque cibele-marque centrum natessance karelea jonzac aultmore pernod-anise boehli-marque jean-herve-marque andros-marque daregal-marque palmolive le-petit-camarguais-marque markal-marque".split())
import csv
from diams import supabase_client
c0 = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
g = supabase_client.get_all
ind = {i["code"]: i["id"] for i in g(c0, "indicators", {"select": "id,code"})}
ents = {e["slug"]: e for e in g(c0, "entities", {"select": "id,slug,display_name,is_brand,animal_free"})}
doc = {x["entity_id"] for x in g(c0, "evidence_active", {"select": "entity_id,indicator_id"})
       if x["indicator_id"] in (ind["ANI_EXPLOITATION"], ind["ANI_ANIMAL_FREE"])}
SITES = "C:/Users/damie/Downloads/claude/awareness-score/pipeline/curated/sites_officiels_logos_2026-10-16.csv"
d = []
for r in csv.DictReader(open(SITES, encoding="utf-8")):
    e = ents.get(r["slug"])
    if e and e["is_brand"] and e["id"] not in doc and not e.get("animal_free") and r["slug"] not in EXCLUS:
        d.append({"slug": r["slug"], "nom": e.get("display_name"), "site": r["site"].rstrip("/")})
print(len(d), "marques présumées avec un site prouvé", flush=True)
def texte(h):
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>|</(p|li|h\d|div|td|tr|title)>", "\n", h)
    return html.unescape(re.sub(r"<[^>]+>", " ", h))
def phrases(t):
    for l in t.split("\n"):
        l = re.sub(r"\s+", " ", l).strip()
        if 6 <= len(l) <= 220:
            yield l
def scan(r):
    out = {"slug": r["slug"], "nom": r["nom"], "site": r["site"], "ani": [], "veg": []}
    vus = set()
    with httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=10, follow_redirects=True,
                      headers={"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}) as c:
        try:
            a = c.get(r["site"] + "/")
        except Exception:
            return out
        hote = urlparse(str(a.url)).netloc
        liens = []
        for l in re.findall(r'href="([^"#?]+)"', a.text):
            u = urljoin(str(a.url), l)
            if urlparse(u).netloc == hote and PROD.search(u) and u not in liens and not re.search(r"\.(jpg|png|pdf|css|js)$", u):
                liens.append(u)
        for u, h in [(str(a.url), a.text)] + [(u, None) for u in liens[:8]]:
            if h is None:
                try:
                    p = c.get(u)
                    if p.status_code >= 400: continue
                    h = p.text
                except Exception:
                    continue
            for ph in phrases(texte(h)):
                if ph in vus: continue
                vus.add(ph)
                if VEG.search(ph): out["veg"].append({"url": u, "q": ph})
                m = ANI.search(ph)
                if m and not NEG.search(ph[max(0, m.start() - 25):m.start()]):
                    out["ani"].append({"url": u, "q": ph, "kw": m.group(0).lower()})
    return out
with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(scan, d))
json.dump(res, open("ani_scan9.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(sum(1 for r in res if r["ani"]), "marques avec un passage animal ;", sum(1 for r in res if r["veg"]), "avec une mention vegan ;", sum(1 for r in res if not r["ani"] and not r["veg"]), "rien")
