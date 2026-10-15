"""liens_morts.py <preuves.json> <sortie.json> : état HTTP de chaque adresse de source citée sur les
fiches (identité déclarée du vérificateur, une seule nouvelle tentative après un refus)."""
import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
import httpx
sys.stdout.reconfigure(encoding="utf-8")
P = json.load(open(sys.argv[1], encoding="utf-8"))
urls = sorted({p["url"] for p in P if p.get("url", "").startswith("http")})
H = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}
def etat(u):
    with httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=25, follow_redirects=True, headers=H) as c:
        for essai in range(2):
            try:
                with c.stream("GET", u) as r:
                    code = r.status_code
            except Exception as x:
                code = type(x).__name__
            if code == 200 or essai:
                return u, code
            time.sleep(3)
with ThreadPoolExecutor(6) as ex:
    res = dict(ex.map(etat, urls))
json.dump(res, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=0)
from collections import Counter
print(len(urls), "adresses ;", Counter(str(v) for v in res.values()).most_common())
