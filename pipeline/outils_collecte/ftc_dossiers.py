"""Sanctions de la FTC (Federal Trade Commission, États-Unis ; domaine public fédéral) : amendes
civiles (« civil penalty ») prononcées depuis cinq ans contre un groupe de l'Index.

Pour chaque groupe racine : recherche dans la bibliothèque des dossiers de la FTC
(/legal-library/browse/cases-proceedings?search=), dossiers dont le titre contient le nom du groupe
(mot entier) ; lecture de la page du dossier (date de mise à jour) et des communiqués liés, dont on
garde les phrases mentionnant une amende civile. Les candidats sont relus à la main avant tout lot.
Délai de 5 secondes entre deux requêtes (robots.txt du site).

Usage : ftc_dossiers.py <dossier>   (cache ftc_cache.json ; sortie ftc_candidats.json ; reprise)
"""
import datetime as dt, html, json, os, re, sys, time
import httpx
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from diams import supabase_client

OUT = sys.argv[1]
CACHE = os.path.join(OUT, "ftc_cache.json")
BASE = "https://www.ftc.gov"
UA = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}
w = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60, headers=UA, follow_redirects=True)
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60)
cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {"recherches": {}, "pages": {}}
DEPUIS = dt.date.today() - dt.timedelta(days=5 * 365)


def get(url):
    if url in cache["pages"]:
        return cache["pages"][url]
    time.sleep(5)
    try:
        r = w.get(url)
    except httpx.HTTPError:
        return None
    t = r.text if r.status_code == 200 else None
    cache["pages"][url] = t
    return t


def texte(p):
    m = re.search(r"<main.*?</main>", p or "", re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", m.group(0) if m else "", flags=re.S)))


ents = supabase_client.get_all(c, "entities", {"select": "slug,display_name,is_brand,parent_id"})
roots = [e for e in ents if not e["is_brand"] and not e["parent_id"] and len(e["display_name"]) >= 3]
print(len(roots), "groupes")
cand = []
for n, e in enumerate(roots, 1):
    nom = e["display_name"]
    if nom not in cache["recherches"]:
        time.sleep(5)
        try:
            p = w.get(BASE + "/legal-library/browse/cases-proceedings", params={"search": nom, "items_per_page": 100}).text
        except httpx.HTTPError:
            continue
        liens = re.findall(r'<a href="(/legal-library/browse/cases-proceedings/\d[^"]+)"[^>]*>(.*?)</a>', p, re.S)
        cache["recherches"][nom] = [[u, re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", t))).strip()] for u, t in liens]
    mot = re.compile(r"(?<![\w-])" + re.escape(nom) + r"(?![\w-])", re.I)
    for u, titre in cache["recherches"][nom]:
        if not mot.search(titre):
            continue
        page = get(BASE + u)
        t = texte(page)
        m = re.search(r"Last Updated (\w+ \d{1,2}, \d{4})", t)
        maj = dt.datetime.strptime(m.group(1), "%B %d, %Y").date() if m else None
        if not maj or maj < DEPUIS:
            continue
        for pr in dict.fromkeys(re.findall(r'href="(/news-events/news/press-releases/[^"#?]+)"', page or "")):
            tp = texte(get(BASE + pr))
            phrases = [s.strip() for s in re.split(r"(?<=[.!?])\s+", tp) if re.search(r"civil penalt", s, re.I)]
            if phrases:
                cand.append({"slug": e["slug"], "nom": nom, "dossier": BASE + u, "titre": titre, "maj": maj.isoformat(),
                             "communique": BASE + pr, "phrases": phrases[:6]})
    if n % 25 == 0:
        json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False); print(n, "groupes")
json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
json.dump(cand, open(os.path.join(OUT, "ftc_candidats.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("fini :", len(cand), "communiqués candidats ;", len({x["slug"] for x in cand}), "groupes")
