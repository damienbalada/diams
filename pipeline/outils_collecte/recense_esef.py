import os, sys, json
from concurrent.futures import ThreadPoolExecutor
import httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client
from diams.connectors import esef
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60, follow_redirects=True)
ents = supabase_client.get_all(c, "entities", {"select": "id,slug,lei,country,parent_id,is_brand,display_name,legal_name"})
racines = [e for e in ents if e.get("lei") and not e["is_brand"]]
def f(e):
    try:
        with httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60, follow_redirects=True) as cc:
            fi = esef.latest_filing(e["lei"], cc, prefer_country=e.get("country"))
        return e["slug"], (fi.__dict__ if fi else None), e.get("parent_id") is None
    except Exception as x:
        return e["slug"], {"erreur": str(x)[:80]}, e.get("parent_id") is None
with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(f, racines))
ok = {s: d for s, d, r in res if d and "erreur" not in d}
json.dump(ok, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "esef_depots.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(racines), "entités avec LEI ;", len(ok), "avec un rapport ESEF ;", sum(1 for s, d, r in res if d and "erreur" in d), "erreurs")
print(sorted(ok))
