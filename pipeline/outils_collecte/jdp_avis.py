"""Avis du Jury de déontologie publicitaire (JDP) : relève, pour chaque avis listé dans le plan du
site, l'annonceur, le support, le numéro, l'issue (plainte fondée, partiellement fondée, rejetée…),
la date de publication et la mention des règles « Développement durable » ou « environnement ».

Usage : jdp_avis.py <dossier>   (cache jdp_cache.json dans le dossier ; reprise possible)
"""
import html, json, os, re, sys, time
import httpx

OUT = sys.argv[1]
CACHE = os.path.join(OUT, "jdp_cache.json")
UA = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}
w = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60, headers=UA, follow_redirects=True)
cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
urls = []
for sm in ("avis-sitemap.xml", "avis-sitemap2.xml"):
    urls += re.findall(r"<loc>(https://www\.jdp-pub\.org/avis/[^<]+/)</loc>", w.get(f"https://www.jdp-pub.org/{sm}").text)
print(len(urls), "avis")
MOIS = {m: i for i, m in enumerate("janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split(), 1)}
for n, u in enumerate(urls, 1):
    if u in cache:
        continue
    time.sleep(1)
    try:
        r = w.get(u)
    except httpx.HTTPError as e:
        print("  erreur", u, e); continue
    page = r.content.decode("utf-8", errors="replace")
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", page, flags=re.S)))
    titre = html.unescape((re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S) or [None, ""])[1])
    titre = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", titre)).strip()
    m = re.search(r"Avis publié le (\d{1,2})(?:er)? (\w+) (\d{4})", t)
    date = f"{m.group(3)}-{MOIS.get(m.group(2).lower(), 0):02d}-{int(m.group(1)):02d}" if m else ""
    issue = (re.search(r"\b(Plainte (?:partiellement )?fondée|Plainte rejetée|Plainte non fondée|Réserves?|Irrecevable)", t) or [None, ""])[0] if True else ""
    if isinstance(issue, re.Match):
        issue = issue.group(1)
    num = (re.search(r"\b(\d{2,4}/\d{2})\b", t) or [None, ""])
    num = num.group(1) if isinstance(num, re.Match) else ""
    dd = bool(re.search(r"[Dd]éveloppement [Dd]urable", t))
    env = bool(re.search(r"environnement|écolog|planète|climat|carbone|recycl|biodégrad|durable", t, re.I))
    cache[u] = {"titre": titre, "date": date, "issue": issue, "numero": num, "dd": dd, "env": env, "statut": r.status_code}
    if n % 50 == 0:
        json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False); print(n)
json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
print("fini :", len(cache))
