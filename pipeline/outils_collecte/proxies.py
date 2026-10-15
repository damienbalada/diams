"""Dernières circulaires de procuration (DEF 14A) et 10-K des groupes américains restants."""
import json, os, sys, httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams.connectors import sec
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60, follow_redirects=True)
idx = sec.company_index(c)
out = {}
for slug in sys.argv[1:]:
    t = sec.TICKERS[slug]
    cik, title = idx[t]
    sub = sec.submissions(cik, c)
    p, k = sec.latest_form(sub, "DEF 14A", cik), sec.latest_form(sub, "10-K", cik)
    out[slug] = {"title": title, "proxy": p.__dict__ if p else None, "10k": k.__dict__ if k else None}
    print(slug, title, p.filed if p else None, p.url if p else None, "|", k.filed if k else None)
json.dump(out, open("proxies.json", "w", encoding="utf-8"), indent=1)
