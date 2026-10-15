"""Noms suivis de ® ou ™ dans les 10-K (et rapports) des groupes américains : candidats de marques
absentes de la base, avec la phrase qui les cite, pour tri à la main."""
import hashlib, json, os, re, sys, unicodedata
import httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client
S = os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
ents = supabase_client.get_all(c, "entities", {"select": "slug,display_name,legal_name"})
def plain(t):
    return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", (t or "").replace("’", "'")).encode("ascii", "ignore").decode().lower()).strip()
connus = {plain(e.get("display_name")) for e in ents} | {plain(e.get("legal_name")) for e in ents}
GROUPES = sys.argv[1].split(",")
NOM = re.compile(r"((?:[A-Z0-9][\w'’&.\-]*\s){0,3}[A-Z0-9][\w'’&.\-]*)\s?[®™]")
res = {}
for k, d in DEP.items():
    g = d.get("slug", k)
    if g not in GROUPES: continue
    p = os.path.join(S, "cache_rapports", hashlib.sha256(d["report_url"].encode()).hexdigest()[:16] + ".txt")
    if not os.path.exists(p): continue
    t = re.sub(r"\s+", " ", open(p, encoding="utf-8").read())
    for m in NOM.finditer(t):
        n = m.group(1).strip()
        n = re.sub(r"^(?:The|Our|and|or|our|including|such as|as|of|the)\s+", "", n)
        if len(n) < 2 or plain(n) in connus or not plain(n):
            continue
        e = res.setdefault(g, {}).setdefault(n, {"n": 0, "cle": k, "phrase": t[max(0, m.start() - 160): m.end() + 120]})
        e["n"] += 1
json.dump(res, open(os.path.join(S, "marques_10k_2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for g, v in res.items():
    top = sorted(v.items(), key=lambda x: -x[1]["n"])
    print(f"## {g} ({len(v)}):", " | ".join(f"{n}×{e['n']}" for n, e in top[:70]))
