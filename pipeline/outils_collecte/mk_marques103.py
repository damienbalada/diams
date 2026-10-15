"""Lot de marques 103 : marques citées par leur propriétaire dans son rapport officiel (AB InBev, Arla,
Mars, Lactalis, VTech, BIC, Essity, Pierre Fabre, Ubisoft). Écartées : marques dont le propriétaire
change selon le pays (Skol, Modelo Especial, Canada Dry, Varta), noms ambigus (Cristal, Victoria),
sous-gammes et technologies."""
import csv, hashlib, json, os, re, sys, unicodedata
import httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client
S = os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
OUT = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline\curated\marques_2026-10_lot103_rapports_groupes.csv"
ABI = "local c hampions such as Aguila®, Antarctica®, Bud Light®, Brahma®, Cass®, Castle®, Castle Lite®, Cristal®"
L = [  # (marque, nom affiché, groupe, secteur, citation)
    ("Aguila", "Aguila", "ab-inbev", "wines_spirits", ABI), ("Antarctica", "Antarctica", "ab-inbev", "wines_spirits", ABI),
    ("Bud Light", "Bud Light", "ab-inbev", "wines_spirits", ABI), ("Brahma", "Brahma", "ab-inbev", "wines_spirits", ABI),
    ("Cass", "Cass", "ab-inbev", "wines_spirits", ABI), ("Castle Lite", "Castle Lite", "ab-inbev", "wines_spirits", ABI),
    ("Harbin", "Harbin", "ab-inbev", "wines_spirits", "Cristal®, Harbin ®"),
    ("Quilmes", "Quilmes", "ab-inbev", "wines_spirits", "Modelo Especial®, Quilmes®, Victoria®"),
    ("Michelob Ultra", "Michelob Ultra", "ab-inbev", "wines_spirits", "Stella Arto is® and Michelob Ultra®"),
    ("Dano", "Dano", "arla", "food", "while our Dano ® brand saw a volume decrease of 41.5%"),
    ("Cheasy", "Cheasy", "arla", "food", "accompanied by solid growth from Cheasy ® at 11.9%"),
    ("GREENIES", "Greenies", "mars", "pet_care", "In 2025, Mars introduced GREENIES™ Canine Dental Check in the US"),
    ("STARBURST", "Starburst", "mars", "food", "in the US for M&M’S®, Skittles®, STARBURST®"),
    ("SEEDS OF CHANGE", "Seeds of Change", "mars", "food", "SEEDS OF CHANGE™ Organic Protein Bowl in Harvest Herb"),
    ("Mountain High", "Mountain High", "lactalis", "food", "l’héritage de marques emblématiques – Yoplait®, Go‑Gurt®, Oui®, Mountain High®"),
    ("LeapFrog", "LeapFrog", "vtech-electronics-europe", "toys_games", "LeapFrog® 6-in-1 Snap & Learn Busy Cube™ made from reclaimed plastics"),
    ("Rocketbook", "Rocketbook", "bic", "household_durables", "Acquisition de Rocketbook ® , marque américaine de carnets réutilisables"),
    ("Inkbox", "Inkbox", "bic", "personal_care", "Acquisition d’Inkbox ® , la première marque de tatouages semi-permanents sur la peau"),
    ("Wite-Out", "Wite-Out", "bic", "household_durables", "BIC ® Wite-Out ® EZ Correct"),
    ("Soleil", "BIC Soleil", "bic", "personal_care", "Gamme Soleil de BIC ® qui inclut : BIC ® Soleil Escape ®"),
    ("TENA", "TENA", "essity", "personal_care", "TENA Stretch™ Plus Briefs was launched"),
    ("Eludril", "Eludril", "pierre-fabre", "personal_care", "Cette innovation ouvre la voie au développement d’Eludril®, devenue une marque de référence en santé bucco-dentaire"),
    ("Assassin’s Creed", "Assassin’s Creed", "ubisoft", "toys_games", "univers de marques fortes : Assassin’s Creed®, Brawlhalla ®, The Crew®, Far Cry®, For Honor®, Just Dance®"),
    ("Far Cry", "Far Cry", "ubisoft", "toys_games", "univers de marques fortes : Assassin’s Creed®, Brawlhalla ®, The Crew®, Far Cry®, For Honor®, Just Dance®"),
    ("Just Dance", "Just Dance", "ubisoft", "toys_games", "univers de marques fortes : Assassin’s Creed®, Brawlhalla ®, The Crew®, Far Cry®, For Honor®, Just Dance®"),
    ("Rayman", "Rayman", "ubisoft", "toys_games", "Lancement en 1995 de Rayman ®, la première franchise majeure d’Ubisoft"),
]
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
ents = supabase_client.get_all(c, "entities", {"select": "slug,display_name,legal_name"})
slugs = {e["slug"] for e in ents}
def slugify(n):
    s = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", n.replace("’", "")).encode("ascii", "ignore").decode().lower()).strip("-")
    while s in slugs: s += "-marque"
    slugs.add(s); return s
def nom_doc(d):
    if d.get("doc"): return d["doc"]
    if d.get("numero"): return f"Document d'enregistrement universel déposé à l'AMF ({d['numero']})"
    return f"Rapport financier annuel {d['period_end'][:4]} (format ESEF)"
rows = []
for nom, aff, g, sec, q in L:
    ok = None
    for k, d in DEP.items():
        if d.get("slug", k.split("#")[0]) != g: continue
        p = os.path.join(S, "cache_rapports", hashlib.sha256(d["report_url"].encode()).hexdigest()[:16] + ".txt")
        if os.path.exists(p) and q in re.sub(r"\s+", " ", open(p, encoding="utf-8").read()):
            ok = d; break
    assert ok, (nom, q[:50])
    legal = ok.get("source") in ("SEC_FILING", "AMF_BDIF") or "filings.xbrl.org" in ok["report_url"] or ok.get("numero")
    rows.append({"brand_slug": slugify(aff), "brand_name": nom, "group_slug": g, "sector_code": sec, "source_kind": "legal" if legal else "website",
                 "source_url": ok["report_url"], "doc": nom_doc(ok), "quote": q, "observed_on": "2026-10-15", "animal_free": "", "display_name": aff})
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "marques")
for r in rows: print(r["brand_slug"], r["group_slug"], r["source_kind"])
