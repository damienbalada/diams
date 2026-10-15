"""Lot de marques 101 : marques déposées citées par leur propriétaire dans ses 10-K (McCormick,
Energizer, Edgewell, WD-40, Kontoor, Monster Beverage, Starbucks, Yum! Brands, Restaurant Brands
International). Citation : la phrase du 10-K qui nomme la marque. Écartées : Varta (propriétaire
différent en Europe), Playtex (activité cédée), Chic, variantes de produits (WD-40 Specialist,
Monster Ultra…), enseignes et produits génériques."""
import csv, hashlib, json, os, re, sys, unicodedata
import httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client
S = os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
OUT = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline\curated\marques_2026-10_lot101_marques_10k_2.csv"
CHOIX = {
    ("mccormick", "food"): ["Gourmet Garden", "French’s", "Frank’s RedHot", "Lawry’s", "Cholula", "Club House", "OLD BAY", "Zatarain’s", "Stubb's",
                            "Thai Kitchen", "Simply Asia", "Schwartz", "Kamis", "La Drogheria", "DaQiao", "Aeroplane"],
    ("energizer", "household_durables"): ["Eveready", "Nu Finish", "LEXOL", "Eagle One", "NEVR-DULL", "California Scents", "Driven", "Carnu", "Kent Car Care"],
    ("edgewell", "personal_care"): ["Skintimate", "Wet Ones", "Schick", "Billie", "Personna", "Jack Black", "Cremo"],
    ("wd-40", "home_care"): ["2000 Flushes", "Spot Shot", "Lava", "GT85", "Solvol", "X-14", "Carpet Fresh", "3-IN-ONE"],
    ("kontoor", "fashion_leather"): ["Rustler", "Riders", "Musto"],
    ("monster-beverage", "beverages"): ["Reign Total Body Fuel", "Bang Energy", "NOS", "Full Throttle", "Predator", "Mother", "Nalu", "BPM", "Hansen’s",
                                        "Oskar Blues Brewery", "Cigar City", "Perrin Brewing Company", "Deep Ellum Brewing Co", "Squatters", "Wasatch"],
    ("starbucks", "restaurant"): ["Teavana"],
    ("yum-brands", "restaurant"): ["Taco Bell", "Pizza Hut", "Habit"],
    ("rbi", "restaurant"): ["Tim Hortons", "Popeyes", "Firehouse Subs", "Burger King"],
}
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
ents = supabase_client.get_all(c, "entities", {"select": "slug,display_name,legal_name"})
slugs = {e["slug"] for e in ents}
def plain(t):
    return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", (t or "").replace("’", "'")).encode("ascii", "ignore").decode().lower()).strip()
connus = {plain(e.get("display_name")) for e in ents} | {plain(e.get("legal_name")) for e in ents}
def slugify(n):
    s = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", n.replace("’", "")).encode("ascii", "ignore").decode().lower()).strip("-")
    while s in slugs: s += "-marque"
    slugs.add(s); return s
rows, deja, rien = [], [], []
for (g, sec), noms in CHOIX.items():
    key = g + "#10k"
    t = re.sub(r"\s+", " ", open(os.path.join(S, "cache_rapports", hashlib.sha256(DEP[key]["report_url"].encode()).hexdigest()[:16] + ".txt"), encoding="utf-8").read())
    for nom in noms:
        if plain(nom) in connus or plain(nom.replace(" Total Body Fuel", "").replace(" Brewery", "").replace(" Brewing Co", "")) in connus:
            deja.append(nom); continue
        best = None
        for m in re.finditer(r"(?<![\w])" + re.escape(nom) + r"\s?[®™]", t):
            a = max(t.rfind(". ", 0, m.start()) + 2, m.start() - 220)
            b = t.find(". ", m.end()); b = min(len(t) if b < 0 else b, m.end() + 220)
            phr = t[a:b].strip()
            # coupe aux mots entiers
            if a == m.start() - 220: phr = phr[phr.find(" ") + 1:]
            if b == m.end() + 220: phr = phr[: phr.rfind(" ")]
            if re.search(r"brand|trademark|portfolio|products?|include|such as|owns?|sell", phr, re.I):
                best = phr; break
            best = best or phr
        if not best: rien.append(nom); continue
        nom_aff = nom.replace(" Total Body Fuel", "").replace(" Brewery", "").replace(" Brewing Co", " Brewing")
        rows.append({"brand_slug": slugify(nom_aff), "brand_name": nom, "group_slug": g, "sector_code": sec, "source_kind": "legal",
                     "source_url": DEP[key]["report_url"], "doc": DEP[key]["doc"], "quote": best, "observed_on": "2026-10-16", "animal_free": "",
                     "display_name": nom_aff})
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "marques ; déjà :", ", ".join(deja), "; sans phrase :", ", ".join(rien))
for r in rows: print(r["group_slug"], "|", r["display_name"], "|", r["quote"][:200])
