"""Phrases de portefeuille (« brands such as X, Y and Z », « nos marques … ») dans tous les rapports
en cache ; extrait les noms absents de la base, groupe par groupe, pour relecture à la main."""
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
LISTE = re.compile(r"(?:brands?|marques?|Marken|portfolio|portefeuille)(?:\s+\w+){0,3}?\s+(?:such as|including|include|includes|like|namely|comme|telles? que|notamment|dont|incluant|wie|:)\s+((?:[^.;:]{2,40}?,\s*){2,}[^.;:]{2,40}?(?:\s(?:and|et|und|&)\s[^.;:,]{2,40}))", re.I)
STOP = {"the", "our", "and", "et", "les", "des", "la", "le", "other", "others", "autres", "etc", "brands", "marques", "products", "produits"}
res = {}
for key, d in DEP.items():
    p = os.path.join(S, "cache_rapports", hashlib.sha256(d["report_url"].encode()).hexdigest()[:16] + ".txt")
    if not os.path.exists(p):
        continue
    t = re.sub(r"\s+", " ", open(p, encoding="utf-8").read())
    groupe = d.get("slug", key)
    for m in LISTE.finditer(t):
        bloc = m.group(1)
        noms = re.split(r",\s*|\s(?:and|et|und|&)\s", bloc)
        for n in noms:
            n = re.sub(r"[®™*©]|\(\d+\)|\d+\)$", "", n).strip(" .’'\"«»")
            if not (2 <= len(n) <= 35) or not re.match(r"[A-ZÀ-Ý0-9]", n) or len(n.split()) > 4:
                continue
            if plain(n) in connus or plain(n) in STOP:
                continue
            res.setdefault(groupe, {}).setdefault(n, m.group(0)[:260])
json.dump(res, open(os.path.join(S, "listes_marques.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(sum(len(v) for v in res.values()), "noms nouveaux dans", len(res), "groupes")
for g, v in sorted(res.items()):
    print(f"## {g} ({len(v)}) :", " | ".join(list(v)[:60]))
