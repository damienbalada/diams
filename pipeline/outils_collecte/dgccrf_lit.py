"""Lit les pages de sanctions publiées par la DGCCRF (plan du site), relève SIRET, montant, date,
motif ; rapproche le SIREN des entités DIAMS (chaîne de propriété)."""
import html, json, os, re, sys, time
import httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client
S = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}
urls = [u.strip() for u in open(os.path.join(S, "telechargements", "dgccrf", "urls.txt")) if "requisitions" not in u]
cache_p = os.path.join(S, "telechargements", "dgccrf", "pages.json")
cache = json.load(open(cache_p, encoding="utf-8")) if os.path.exists(cache_p) else {}
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60, follow_redirects=True, headers=UA)
def texte(h):
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h)))
for u in urls:
    if u in cache: continue
    r = c.get(u)
    if r.status_code == 403:
        time.sleep(3); r = c.get(u)
    if r.status_code != 200:
        print("échec", r.status_code, u); break
    t = texte(r.text)
    i = t.find("Injonctions et sanctions", t.find("Signaler un problème"))
    cache[u] = t[i:i + 4000] if i > 0 else t[:4000]
    time.sleep(0.5)
json.dump(cache, open(cache_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
g = supabase_client.get_all
db = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
ents = g(db, "entities", {"select": "id,slug,siren,parent_id,is_brand,display_name"})
by_siren = {}
for e in ents:
    if e.get("siren"): by_siren.setdefault(e["siren"], []).append(e)
hits = []
for u, t in cache.items():
    for m in re.finditer(r"SIRE[NT]\s*:?\s*(\d[\d\s]{8,16})", t):
        n = re.sub(r"\D", "", m.group(1))[:9]
        if n in by_siren:
            hits.append({"url": u, "siren": n, "slugs": [e["slug"] for e in by_siren[n]], "extrait": t[:900]})
            break
json.dump(hits, open(os.path.join(S, "dgccrf_hits.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(cache), "pages lues ;", len(hits), "sociétés de la base")
for h in hits: print(h["slugs"], h["siren"], h["url"][-90:])
