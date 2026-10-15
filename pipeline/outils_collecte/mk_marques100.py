"""Lot de marques 100 : marques listées par leur propriétaire dans ses documents déposés à la SEC ou
publiés (General Mills : liste des marques déposées du 10-K ; Newell : marques clés par segment du
10-K ; Brown-Forman : portefeuille du rapport annuel ; Hasbro, Stanley Black & Decker, Keurig Dr
Pepper, Mattel). Écartées : Ball (licence), American Girl (citation nommant une personne)."""
import csv, hashlib, json, os, re, sys, unicodedata
import httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client
S = os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
OUT = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline\curated\marques_2026-10_lot100_marques_10k.csv"
GM = ("Some of the more important trademarks used in our global operations (set forth in italics in this report) include Annie ’ s, Betty Crocker, Bisquick, "
      "Blue Buffalo, Bugles, Cascadian Farm, Cheerios, Chex, Cinnamon Toast Crunch, Cocoa Puffs, Cookie Crisp, Dunkaroos, Edgard & Cooper, Fiber One, "
      "Fruit by the Foot, Fruit Gushers, Fruit Roll-Ups, Gardetto ’ s, Gold Medal, Golden Grahams, Häagen-Dazs, Kitano, Kix, Lärabar, Latina, Lucky Charms, "
      "Nature Valley, Nudges, Oatmeal Crisp, Old El Paso, Pillsbury, Progresso, Tastefuls, Tiki Pets, Total, Totino ’ s, Trix, True Solutions, Wanchai Ferry, "
      "Wheaties, Wilderness, and Yoki")
NW1 = ("Home and Commercial Solutions Ball (a) , Calphalon, Chesapeake Bay, Crockpot, FoodSaver, Mapa, Mr. Coffee, Oster, Rubbermaid, "
       "Rubbermaid Commercial Products, Sistema, Spontex, Sunbeam, WoodWick and Yankee Candle")
NW2 = "Learning and Development Dymo, Elmer’s, EXPO, Graco, NUK, Paper Mate, Parker and Sharpie"
NW3 = "Outdoor and Recreation Bubba, Campingaz, Coleman, Contigo and Marmot"
HB1 = ("Through our franchise-first approach, we unlock value from both new and legacy IP, including MAGIC: THE GATHERING, MONOPOLY, HASBRO GAMES, "
       "PLAY-DOH, TRANSFORMERS, DUNGEONS & DRAGONS, NERF, and PEPPA PIG")
SB1 = "Tool Service Net, is the official site for parts and service for DEWALT, CRAFTSMAN, BLACK+DECKER, BOSTITCH, PORTER CABLE and PROTO tools"
SB2 = "Professional Brands such as DEWALT, Proto, Hustler or STANLEY in the industrial space"
KD = "along with powerhouse brands such as Peet’s, L’OR and Jacobs, and other regional coffee leaders"
L = [("general-mills#10k", "general-mills", "pet_care" if n in ("Blue Buffalo", "Edgard & Cooper", "Nudges", "Tastefuls", "Tiki Pets", "Wilderness") else "food", n, GM)
     for n in ["Annie’s", "Betty Crocker", "Bisquick", "Blue Buffalo", "Bugles", "Cascadian Farm", "Cheerios", "Chex", "Cinnamon Toast Crunch", "Cocoa Puffs",
               "Cookie Crisp", "Dunkaroos", "Edgard & Cooper", "Fiber One", "Fruit by the Foot", "Fruit Gushers", "Fruit Roll-Ups", "Gardetto’s", "Gold Medal",
               "Golden Grahams", "Kitano", "Kix", "Lärabar", "Lucky Charms", "Nudges", "Oatmeal Crisp", "Pillsbury", "Progresso", "Tastefuls", "Tiki Pets",
               "Totino’s", "Trix", "Wanchai Ferry", "Wheaties", "Wilderness", "Yoki"]]
L += [("newell-brands#10k", "newell-brands", s, n, NW1) for n, s in [("Calphalon", "household_durables"), ("Chesapeake Bay", "home_care"), ("Crockpot", "household_durables"),
       ("FoodSaver", "household_durables"), ("Mapa", "home_care"), ("Mr. Coffee", "household_durables"), ("Sistema", "household_durables"),
       ("Spontex", "home_care"), ("Sunbeam", "household_durables"), ("WoodWick", "home_care")]]
L += [("newell-brands#10k", "newell-brands", s, n, NW2) for n, s in [("Elmer’s", "household_durables"), ("EXPO", "household_durables"), ("Graco", "personal_care"),
       ("NUK", "personal_care"), ("Parker", "household_durables")]]
L += [("newell-brands#10k", "newell-brands", s, n, NW3) for n, s in [("Bubba", "household_durables"), ("Campingaz", "household_durables"),
       ("Contigo", "household_durables"), ("Marmot", "fashion_leather")]]
L += [("brown-forman#ars", "brown-forman", "wines_spirits", n, q) for n, q in [
    ("Chambord", "Chambord Liqueur"), ("The Glendronach", "The Glendronach Single Malt Scotch Whiskies"), ("Benriach", "Benriach Single Malt Scotch Whiskies"),
    ("Glenglassaugh", "Glenglassaugh Single Malt Scotch Whiskies"), ("Fords Gin", "Fords Gin Jack Daniel’s 12-Year-Old Tennessee Whiskey"),
    ("King of Kentucky", "King of Kentucky Straight Bourbon Whiskey"), ("Slane", "Slane Irish Whiskey"),
    ("Old Forester", "Old Forester Single Barrel Straight Bourbon Whisky"),
    ("Herradura", "Within our tequila portfolio, we strengthened performance and sales of our Herradura Double Barrel Reposado")]]
L += [("hasbro#10k", "hasbro", "toys_games", n, HB1) for n in ["Dungeons & Dragons", "Peppa Pig"]]
L += [("hasbro#10k", "hasbro", "toys_games", "My Little Pony", "a resurgence from MY LITTLE PONY through licensing across merchandising categories")]
L += [("stanley-black-decker#esg", "stanley-black-decker", "household_durables", n, SB1) for n in ["Craftsman", "Bostitch", "Porter Cable", "Proto"]]
L += [("stanley-black-decker#esg", "stanley-black-decker", "household_durables", n, SB2) for n in ["Hustler", "Stanley"]]
L += [("keurig-dr-pepper#proxy", "keurig-dr-pepper", "beverages", n, KD) for n in ["Peet’s", "L’OR", "Jacobs"]]
L += [("mattel#proxy", "mattel", "toys_games", "UNO", "Hot Wheels’ and UNO’s strong momentum continued")]
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
TXT, rows, deja = {}, [], []
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
