"""Lot de marques 96 : portefeuilles cités par les groupes eux-mêmes dans leurs rapports annuels
(lus et vérifiés dans les lots 100 à 106). Une ligne par marque : la citation, exacte, nomme la
marque dans une liste ou une phrase de portefeuille du propriétaire. Écartés : licences
(Puig, Coty), sociétés et usines (Schwarz), marques de filiales étrangères rattachées en base à une
filiale française (Intersnack, VTech), passages sans lien de propriété explicite."""
import csv, hashlib, json, os, re, sys, unicodedata
import httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client

S = os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
OUT = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline\curated\marques_2026-10_lot96_portefeuilles_rapports.csv"
ESSITY_FEM = "Our brands include Libresse, Bodyform, Nana, Saba, Nosotras, Libra, TOM Organic, Knix and Modibodi"
ESSITY_TISSUE = "paper napkins under brands such as Lotus, Tempo, Zewa, Cushelle, Plenty, Regio and Familia"
ESSITY_HEALTH = "well- known brands such as TENA, JOBST, Leukoplast, Actimove, Cutimed and Hydrofera Blue"
ESSITY_BABY = "with leading brands such as Libero, Bodyform, TENA, Lotus, Zewa and Cushelle"
BDF = "With its Hansaplast, Elastoplast and CURITAS brands, Beiersdorf also has a global presence in the field of plasters and wound care"
BDF2 = "La Prairie as well as Chantecaille at the selective cosmetics market"
BDF3 = "Our Derma Eucerin and Aquaphor brands delivered industry-leading organic growth"
BDF4 = "over-the-counter (OTC) sun protection products under the Coppertone and Eucerin Sun brands"
CL = "under brands such as Colgate, Palmolive, Ajax, Axion, Darlie, elmex, EltaMD, Fabuloso, Filorga, hello, Hill’s Prescription Diet, Hill’s Science Diet, Irish Spring, Lady Speed Stick, meridol, PCA SKIN, Prime100, Protex, Sanex, Softsoap, Sorriso, Soupline, Speed Stick, Suavitel and Tom’s of Maine"
KV1 = "Major brands in the segment include Aveeno®, Dr.Ci:Labo®, Le Petit Marseillais®, Lubriderm®, Neutrogena®, OGX®, and Rogaine®"
KV2 = "Major brands in the segment include Benadryl®, Calpol®, Motrin®, Nicorette®, Rhinocort®, Tylenol®, Zarbee’s®, and Zyrtec®"
KV3 = "portfolio of iconic brands—including Aveeno®, BAND-AID® Brand, Johnson’s®, Listerine®, Neutrogena®, Nicorette®, Tylenol®, and Zyrtec®"
KV4 = "Brands such as Stayfree®, Nicorette®, Listerine®, Neutrogena®, and Aveeno® are driving important initiatives"
DL1 = "an American company active in the personal blenders segment with the Nutribullet and Magic Bullet brands"
DL2 = "With the acquisition in 2024 of La Marzocco , the world leader in semi-automatic professional coffee machines"
DL3 = "following the acquisition of Eversys , De’ Longhi entered the professional espresso coffee machine sector"
LISTE = [
    # (clé du rapport, groupe, secteur, marque, citation)
    ("essity", "essity", "personal_care", "Libresse", ESSITY_FEM), ("essity", "essity", "personal_care", "Bodyform", ESSITY_FEM),
    ("essity", "essity", "personal_care", "Saba", ESSITY_FEM), ("essity", "essity", "personal_care", "Nosotras", ESSITY_FEM),
    ("essity", "essity", "personal_care", "Libra", ESSITY_FEM), ("essity", "essity", "personal_care", "TOM Organic", ESSITY_FEM),
    ("essity", "essity", "personal_care", "Knix", ESSITY_FEM), ("essity", "essity", "personal_care", "Modibodi", ESSITY_FEM),
    ("essity", "essity", "personal_care", "Tempo", ESSITY_TISSUE), ("essity", "essity", "personal_care", "Zewa", ESSITY_TISSUE),
    ("essity", "essity", "personal_care", "Cushelle", ESSITY_TISSUE), ("essity", "essity", "personal_care", "Plenty", ESSITY_TISSUE),
    ("essity", "essity", "personal_care", "Regio", ESSITY_TISSUE), ("essity", "essity", "personal_care", "Familia", ESSITY_TISSUE),
    ("essity", "essity", "personal_care", "JOBST", ESSITY_HEALTH), ("essity", "essity", "personal_care", "Leukoplast", ESSITY_HEALTH),
    ("essity", "essity", "personal_care", "Actimove", ESSITY_HEALTH), ("essity", "essity", "personal_care", "Cutimed", ESSITY_HEALTH),
    ("essity", "essity", "personal_care", "Hydrofera Blue", ESSITY_HEALTH), ("essity", "essity", "personal_care", "Libero", ESSITY_BABY),
    ("beiersdorf", "beiersdorf", "personal_care", "Elastoplast", BDF), ("beiersdorf", "beiersdorf", "personal_care", "CURITAS", BDF),
    ("beiersdorf", "beiersdorf", "beauty_fragrance", "Chantecaille", BDF2), ("beiersdorf", "beiersdorf", "personal_care", "Aquaphor", BDF3),
    ("beiersdorf", "beiersdorf", "personal_care", "Coppertone", BDF4),
    ("colgate-palmolive#esg", "colgate-palmolive", "home_care", "Axion", CL), ("colgate-palmolive#esg", "colgate-palmolive", "personal_care", "Darlie", CL),
    ("colgate-palmolive#esg", "colgate-palmolive", "personal_care", "EltaMD", CL), ("colgate-palmolive#esg", "colgate-palmolive", "home_care", "Fabuloso", CL),
    ("colgate-palmolive#esg", "colgate-palmolive", "beauty_fragrance", "Filorga", CL), ("colgate-palmolive#esg", "colgate-palmolive", "personal_care", "hello", CL),
    ("colgate-palmolive#esg", "colgate-palmolive", "pet_care", "Hill’s Science Diet", CL), ("colgate-palmolive#esg", "colgate-palmolive", "pet_care", "Hill’s Prescription Diet", CL),
    ("colgate-palmolive#esg", "colgate-palmolive", "personal_care", "Irish Spring", CL), ("colgate-palmolive#esg", "colgate-palmolive", "personal_care", "Lady Speed Stick", CL),
    ("colgate-palmolive#esg", "colgate-palmolive", "beauty_fragrance", "PCA SKIN", CL), ("colgate-palmolive#esg", "colgate-palmolive", "pet_care", "Prime100", CL),
    ("colgate-palmolive#esg", "colgate-palmolive", "personal_care", "Protex", CL), ("colgate-palmolive#esg", "colgate-palmolive", "personal_care", "Softsoap", CL),
    ("colgate-palmolive#esg", "colgate-palmolive", "personal_care", "Sorriso", CL), ("colgate-palmolive#esg", "colgate-palmolive", "personal_care", "Speed Stick", CL),
    ("colgate-palmolive#esg", "colgate-palmolive", "home_care", "Suavitel", CL), ("colgate-palmolive#esg", "colgate-palmolive", "personal_care", "Tom’s of Maine", CL),
    ("kenvue#esg", "kenvue", "personal_care", "Dr.Ci:Labo", KV1), ("kenvue#esg", "kenvue", "personal_care", "Lubriderm", KV1),
    ("kenvue#esg", "kenvue", "personal_care", "Rogaine", KV1), ("kenvue#esg", "kenvue", "personal_care", "Benadryl", KV2),
    ("kenvue#esg", "kenvue", "personal_care", "Calpol", KV2), ("kenvue#esg", "kenvue", "personal_care", "Motrin", KV2),
    ("kenvue#esg", "kenvue", "personal_care", "Rhinocort", KV2), ("kenvue#esg", "kenvue", "personal_care", "Tylenol", KV2),
    ("kenvue#esg", "kenvue", "personal_care", "Zarbee’s", KV2), ("kenvue#esg", "kenvue", "personal_care", "Zyrtec", KV2),
    ("kenvue#esg", "kenvue", "personal_care", "BAND-AID", KV3), ("kenvue#esg", "kenvue", "personal_care", "Stayfree", KV4),
    ("delonghi#en", "delonghi", "household_durables", "Magic Bullet", DL1), ("delonghi#en", "delonghi", "household_durables", "La Marzocco", DL2),
    ("delonghi#en", "delonghi", "household_durables", "Eversys", DL3),
    ("church-dwight#esg", "church-dwight", "home_care", "Touchland", "we completed the acquisition of Touchland Holding Corp., the developer of TOUCHLAND® hand sanitizer products"),
    ("coty#esg", "coty", "beauty_fragrance", "philosophy", "Coty Brazil brands Paixão and Cenoura & Bronze joined COVERGIRL, Rimmel, Manhattan, philosophy, Risqué and Monange"),
    ("coty#esg", "coty", "beauty_fragrance", "Manhattan", "Coty Brazil brands Paixão and Cenoura & Bronze joined COVERGIRL, Rimmel, Manhattan, philosophy, Risqué and Monange"),
    ("coty#esg", "coty", "beauty_fragrance", "Risqué", "Coty Brazil brands Paixão and Cenoura & Bronze joined COVERGIRL, Rimmel, Manhattan, philosophy, Risqué and Monange"),
    ("coty#esg", "coty", "beauty_fragrance", "Monange", "Coty Brazil brands Paixão and Cenoura & Bronze joined COVERGIRL, Rimmel, Manhattan, philosophy, Risqué and Monange"),
    ("ldc", "ldc", "food", "Indykpol", "tranchage de charcuterie à la marque Indykpol"),
    ("lanson-bcc", "lanson-bcc", "wines_spirits", "Chanoine Frères", "La Maison CHANOINE se distingue par ses deux marques complémentaires aux styles distincts : Champagne Chanoine Frères et Cham pagne Tsarine"),
    ("lanson-bcc", "lanson-bcc", "wines_spirits", "Heidsieck & C° Monopole", "La marque Heidsieck & C° Monopole sera développée au sein de la Maison Burtin"),
    ("euralis", "euralis", "food", "Maison Montfort", "la grande distribution pour les marques Maison Montfort, Qualité Traiteur et les Marques De Distributeurs (MDD)"),
    ("schwarz-gruppe", "schwarz-gruppe", "retail_distribution", "Kaufland", "setzt sich aus den Handelssparten Lidl und Kaufland, den Kreis- laufwirtschaftsunternehmen PreZero"),
    ("richemont#nfr", "richemont", "watches_jewelry", "Vhernier", "The integration of Vhernier into Richemont’s regional operating model in 2025"),
    ("richemont#nfr", "richemont", "fashion_leather", "Gianvito Rossi", "as well as Maison Gianvito Rossi and Manufacture Miles acquired in FY24"),
]
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
ents = supabase_client.get_all(c, "entities", {"select": "slug,display_name,legal_name"})
def plain(t):
    return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", (t or "").replace("’", "'")).encode("ascii", "ignore").decode().lower()).strip()
connus = {plain(e.get("display_name")) for e in ents} | {plain(e.get("legal_name")) for e in ents}
slugs = {e["slug"] for e in ents}
def slugify(n):
    s = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", n.replace("’", "")).encode("ascii", "ignore").decode().lower()).strip("-")
    return s if s not in slugs else s + "-marque"
rows, deja, absentes = [], [], []
for key, groupe, secteur, marque, q in LISTE:
    if plain(marque) in connus:
        deja.append(marque); continue
    t = open(os.path.join(S, "cache_rapports", hashlib.sha256(DEP[key]["report_url"].encode()).hexdigest()[:16] + ".txt"), encoding="utf-8").read()
    if re.sub(r"\s+", " ", q) not in re.sub(r"\s+", " ", t):
        absentes.append(marque); continue
    rows.append({"brand_slug": slugify(marque), "brand_name": marque, "group_slug": groupe, "sector_code": secteur,
                 "source_kind": "legal" if DEP[key].get("source") in ("ANNUAL_REPORT", "ESEF", "AMF_BDIF", "SEC_FILING") else "website",
                 "source_url": DEP[key]["report_url"], "doc": DEP[key]["doc"], "quote": q, "observed_on": "2026-10-15",
                 "animal_free": "", "display_name": marque})
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
print(len(rows), "marques ;", "déjà en base :", ", ".join(deja) or "aucune", "; citation introuvable :", ", ".join(absentes) or "aucune")
