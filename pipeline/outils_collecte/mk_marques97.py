"""Lot de marques 97 : phrases de portefeuille relevées dans les rapports des lots 100 à 106
(listes_marques.py), triées à la main. Écartés : licences (Coty, Interparfums, Hasbro : Marvel,
Spider-Man…), marques de tiers citées (Pepsi, Mirinda, Sting chez Carlsberg ; Crest, Cadbury chez
Kenvue), marques dont le propriétaire change selon le pays (Canada Dry, 7UP, Scrabble), variantes
de produit (Tuborg Green, modèles Stellantis), sociétés d'un autre groupe (DMK chez Arla)."""
import csv, hashlib, json, os, re, sys, unicodedata
import httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client
S = os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
OUT = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline\curated\marques_2026-10_lot97_portefeuilles_rapports_2.csv"
CHOIX = {
    "arla": ["Puck"],
    "danone": ["Real Food Blends", "Functional Formularies", "Kate Farms", "Nutriday", "Ultramel", "FanMilk", "Jamila", "Salim", "Trèfle",
               "Bebelac", "Nursei", "SGM", "Dumex", "International Delight", "Silk"],
    "haleon": ["Panadol", "Excedrin", "Fenbid", "Grand-Pa", "Otrivin", "Theraflu", "Flonase", "Robitussin"],
    "heineken": ["Stëlz", "SERVED", "G Spot", "Bavaria", "Tropical", "Ducal", "Kern’s"],
    "henkel": ["Weißer Riese", "Spee"],
    "keurig-dr-pepper": ["Dr Pepper", "Mott’s", "A&W", "Peñafiel", "GHOST", "Snapple", "Clamato", "Core Hydration"],
    "lotus-bakeries": ["Suzy", "Dinosaurus", "Annas", "Peijnenburg", "Snelle Jelle"],
    "magnum-ice-cream-company": ["Breyers", "Popsicle"],
    "mars": ["Cheez-It", "RXBAR", "Pop-Tarts", "Rice Krispies Treats"],
    "remy-cointreau": ["Ponche Kuba", "Westland", "Belle de Brillet"],
    "seb": [("Supor", "Supor ou Imusa"), ("Imusa", "Supor ou Imusa"), ("Arno", "Arno au Brésil"), ("Samurai", "Samurai en Colombie")],
    "hasbro": ["PJ MASKS", "POWER RANGERS", "THE GAME OF LIFE"],
    "stellantis": ["Lancia"],
}
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
ents = supabase_client.get_all(c, "entities", {"select": "slug,display_name,legal_name,sector_id"})
sect = {s["id"]: s["code"] for s in supabase_client.get_all(c, "sectors", {"select": "id,code"})}
by_slug = {e["slug"]: e for e in ents}
slugs = set(by_slug)
def plain(t):
    return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", (t or "").replace("’", "'")).encode("ascii", "ignore").decode().lower()).strip()
connus = {plain(e.get("display_name")) for e in ents} | {plain(e.get("legal_name")) for e in ents}
def slugify(n):
    s = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", n.replace("’", "")).encode("ascii", "ignore").decode().lower()).strip("-")
    while s in slugs:
        s += "-marque"
    slugs.add(s)
    return s
listes = json.load(open(os.path.join(S, "listes_marques.json"), encoding="utf-8"))
rows, deja = [], []
TXT = {}
for k, d in DEP.items():
    p_ = os.path.join(S, "cache_rapports", hashlib.sha256(d["report_url"].encode()).hexdigest()[:16] + ".txt")
    if os.path.exists(p_):
        TXT[k] = re.sub(r"\s+", " ", open(p_, encoding="utf-8").read())
for groupe, noms in CHOIX.items():
    for n in noms:
        nom, cle = (n, n) if isinstance(n, str) else n
        if plain(nom) in connus:
            deja.append(nom); continue
        q = listes.get(groupe, {}).get(cle)
        if not q:
            print("pas de phrase pour", groupe, nom); continue
        q = q.strip()
        q = q[: q.rfind(" ")] if len(q) >= 250 else q  # pas de mot coupé en fin de citation
        key = next((k for k, d in DEP.items() if d.get("slug", k) == groupe and k in TXT and q in TXT[k]), None)
        assert key, (groupe, nom)
        rows.append({"brand_slug": slugify(nom), "brand_name": nom, "group_slug": groupe, "sector_code": sect.get(by_slug[groupe]["sector_id"], "fmcg_group"),
                     "source_kind": "legal" if DEP[key].get("source", "ESEF") in ("ANNUAL_REPORT", "ESEF", "AMF_BDIF", "SEC_FILING") else "website",
                     "source_url": DEP[key]["report_url"], "doc": DEP[key].get("doc") or "Rapport financier annuel 2025 (ESEF)", "quote": q,
                     "observed_on": "2026-10-15", "animal_free": "", "display_name": nom})
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "marques ; déjà en base :", ", ".join(deja) or "aucune")
