"""Lot de marques 99 : marques déposées (®) listées par Spectrum Brands (10-K), Church & Dwight,
Kenvue (rapports de durabilité) et Keurig Dr Pepper (circulaire). Écartées : licences (Black+Decker,
George Foreman, Emeril), marques cédées (Vitafusion, L'il Critters, vendues le 31/12/2025),
Ball (sous licence)."""
import csv, hashlib, json, os, re, sys, unicodedata
import httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client
S = os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
OUT = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline\curated\marques_2026-10_lot99_marques_deposees_us.csv"
SP1 = "Companion Animal: Good ’ n ’ Fun®, DreamBone®, Good Boy®, Nature's Miracle®, SmartBones®, FURminator®, Wild Harvest TM , Dingo®, 8IN1® (8-in-1), Better Belly®, and Meowee!®"
SP2 = "Aquatics: Tetra®, Marineland®, GloFish®, Instant Ocean®, and OmegaSea®"
SP3 = "Household: Hot Shot®, Black Flag®. Controls: Spectracide®, Liquid Fence®, Garden Safe®, and EcoLogic®. Repellents: Cutter® and Repel®. Cleaning: Rejuvenate®"
CH = ("Our well-recognized brands include ARM & HAMMER® baking soda, cat litter, laundry detergent, carpet deodorizer, and other baking soda-based products; "
      "OXICLEAN® stain removers, cleaning solutions, laundry detergents, and bleach alternatives; BATISTE® dry shampoo; WATERPIK® water flossers; "
      "THERABREATH® oral care products; HERO® acne treatment products; TOUCHLAND® hand sanitizers; TROJAN® condoms, lubricants, and vibrators; "
      "FIRST RESPONSE® home pregnancy and ovulation test kits; NAIR® depilatories; ORAJEL® oral analgesic; XTRA® laundry detergent; and ZICAM® cold shortening and relief products")
CHG = "We qualified PET neckbands to replace PVC neckbands on the packaging for our Gravol™ and Ovol™ brand products"
KV = "Major brands in the segment include BAND-AID® Brand, Carefree®, Desitin®, Johnson’s®, Listerine®, o.b.® tampons, and Stayfree®"
L = [
    ("spectrum-brands#10k", "spectrum-brands", "pet_care", n, SP1) for n in ["Good ’n’ Fun", "DreamBone", "Good Boy", "Nature's Miracle", "SmartBones", "FURminator", "Wild Harvest", "Dingo", "8IN1", "Better Belly", "Meowee!"]
] + [
    ("spectrum-brands#10k", "spectrum-brands", "pet_care", n, SP2) for n in ["Tetra", "Marineland", "GloFish", "Instant Ocean", "OmegaSea"]
] + [
    ("spectrum-brands#10k", "spectrum-brands", "home_care", n, SP3) for n in ["Hot Shot", "Black Flag", "Spectracide", "Liquid Fence", "Garden Safe", "EcoLogic", "Cutter", "Repel", "Rejuvenate"]
] + [
    ("church-dwight#esg", "church-dwight", s, n, CH) for n, s in [("OxiClean", "home_care"), ("Batiste", "personal_care"), ("Waterpik", "personal_care"), ("TheraBreath", "personal_care"),
                                                                  ("Hero", "personal_care"), ("Trojan", "personal_care"), ("First Response", "personal_care"), ("Nair", "personal_care"),
                                                                  ("Orajel", "personal_care"), ("Xtra", "home_care"), ("Zicam", "personal_care")]
] + [
    ("church-dwight#esg", "church-dwight", "personal_care", n, CHG) for n in ["Gravol", "Ovol"]
] + [
    ("kenvue#esg", "kenvue", "personal_care", n, KV) for n in ["Carefree", "Desitin", "o.b."]
] + [
    ("kenvue#esg", "kenvue", "personal_care", "Codral", "In 2025, Codral® continued its partnership with Australian pharmacy chain Chemist Warehouse"),
    ("kenvue#esg", "kenvue", "personal_care", "Siempre Libre", "We combined Siempre Libre® product distribution with an educational board game"),
    ("keurig-dr-pepper#proxy", "keurig-dr-pepper", "household_durables", "Keurig", "includes the leading Keurig ® single-serve brewing system in the U.S. and Canada"),
]
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
TXT = {}
rows, deja = [], []
for key, g, sec, nom, q in L:
    if plain(nom) in connus: deja.append(nom); continue
    if key not in TXT:
        TXT[key] = re.sub(r"\s+", " ", open(os.path.join(S, "cache_rapports", hashlib.sha256(DEP[key]["report_url"].encode()).hexdigest()[:16] + ".txt"), encoding="utf-8").read())
    assert q in TXT[key], (nom, q[:60])
    rows.append({"brand_slug": slugify(nom), "brand_name": nom, "group_slug": g, "sector_code": sec,
                 "source_kind": "legal" if DEP[key].get("source") == "SEC_FILING" else "website", "source_url": DEP[key]["report_url"],
                 "doc": DEP[key]["doc"], "quote": q, "observed_on": "2026-10-16", "animal_free": "", "display_name": nom})
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "marques ; déjà :", ", ".join(deja))
