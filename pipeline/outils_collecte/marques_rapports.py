"""Marques citées dans les rapports annuels déjà lus (lots 100 à 106) : pour chaque marque absente
de la base, cherche dans le texte du rapport un passage qui la nomme avec un mot de portefeuille
(marque, brand, portfolio…). Sortie : candidats à relire à la main (marques_candidats.json)."""
import hashlib, json, os, re, sys, unicodedata
import httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client

S = os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
# clé du document, slug du groupe, secteur par défaut, marques annoncées par la société
CIBLES = [
    ("essity", "essity", "personal_care", ["TENA", "Tork", "Lotus", "Nana", "Demak'Up", "Okay", "Saba", "Libero", "Libresse", "Bodyform", "Leukoplast", "JOBST", "Actimove", "Cutimed", "Zewa", "Plenty", "Edet", "Cushelle", "Tempo", "Regio", "Familia", "Nosotras", "Modibodi", "TOM Organic", "Knix"]),
    ("beiersdorf", "beiersdorf", "personal_care", ["Eucerin", "Aquaphor", "La Prairie", "Hansaplast", "Labello", "Florena", "Coppertone", "Chantecaille", "8x4", "Elastoplast", "Gammon"]),
    ("puig#nfr", "puig", "beauty_fragrance", ["Rabanne", "Carolina Herrera", "Jean Paul Gaultier", "Charlotte Tilbury", "Byredo", "Nina Ricci", "Dries Van Noten", "Uriage", "Apivita", "Penhaligon's", "L'Artisan Parfumeur", "Loewe Perfumes", "Christian Louboutin", "Kama Ayurveda", "Dr. Barbara Sturm", "Antonio Banderas", "Benetton", "Adolfo Dominguez", "Shakira"]),
    ("richemont#nfr", "richemont", "watches_jewelry", ["Cartier", "Van Cleef & Arpels", "Buccellati", "Vhernier", "Jaeger-LeCoultre", "IWC Schaffhausen", "Piaget", "Vacheron Constantin", "A. Lange & Söhne", "Panerai", "Roger Dubuis", "Montblanc", "Peter Millar", "Purdey", "Serapian", "Alaïa", "Gianvito Rossi", "Delvaux"]),
    ("colgate-palmolive#esg", "colgate-palmolive", "personal_care", ["Hill's", "Tom's of Maine", "meridol", "Filorga", "Irish Spring", "Softsoap", "Ajax", "Fabuloso", "Suavitel", "Speed Stick", "Lady Speed Stick", "Protex", "Murphy", "PCA Skin", "EltaMD", "Hello"]),
    ("church-dwight#esg", "church-dwight", "home_care", ["ARM & HAMMER", "OxiClean", "Batiste", "TheraBreath", "Hero", "Waterpik", "Vitafusion", "L'il Critters", "First Response", "Trojan", "Nair", "Orajel", "Zicam", "Xtra", "Kaz", "Spinbrush", "Toppik", "Simply Saline", "Touchland"]),
    ("kenvue#esg", "kenvue", "personal_care", ["Neutrogena", "Aveeno", "Listerine", "Johnson's", "OGX", "Le Petit Marseillais", "Nicorette", "Zyrtec", "Tylenol", "BAND-AID", "Clean & Clear", "Dr.Ci:Labo", "Rogaine", "Benadryl", "Motrin", "Imodium", "Visine", "Sudafed", "Calpol", "Carefree", "o.b.", "Stayfree", "Neostrata", "Biafine", "Nicotinell", "Rhinadvil"]),
    ("ldc", "ldc", "food", ["Loué", "Le Gaulois", "Maître CoQ", "Marie", "Traditions d'Asie", "Régalette", "Ronsard", "Le Marché", "Poulets de Janzé", "Fermiers de l'Ardèche", "Fermiers Landais", "Drosed", "Indykpol", "Hopi"]),
    ("delonghi#en", "delonghi", "household_durables", ["Kenwood", "Braun", "Nutribullet", "Magic Bullet", "Ariete", "La Marzocco", "Eversys"]),
    ("sodiaal", "sodiaal", "food", ["Candia", "Entremont", "Le Rustique", "Régilait", "Grand Lait", "Monts & Terroirs", "Nactalia", "Cœur de Lion", "Les Fromagers Associés"]),
    ("coty#esg", "coty", "beauty_fragrance", ["Rimmel", "Max Factor", "Sally Hansen", "Bourjois", "CoverGirl", "Kylie Cosmetics", "SKKN", "philosophy", "Lancaster", "Nautica", "Bruno Banani", "Adidas", "Davidoff", "Mexx", "Bozzolo"]),
    ("castel-freres", "castel-freres", "wines_spirits", ["Baron de Lestac", "Roche Mazet", "Vieux Papes", "Cambras", "Malesan", "Ferraton", "Patriarche", "Barton & Guestier", "Nicolas"]),
    ("lanson-bcc", "lanson-bcc", "wines_spirits", ["Lanson", "Philipponnat", "Boizel", "De Venoge", "Chanoine Frères", "Tsarine", "Besserat de Bellefon", "Alexandre Bonnet", "Maison Burtin"]),
    ("intersnack-france", "intersnack-france", "food", ["Vico", "Curly", "Bénénuts", "Chipsters", "Pom'Bistro", "Tyrrells", "KP", "Pom-Bär", "Chio", "funny-frisch", "ültje", "McCoy's", "Hula Hoops", "Popchips", "Felix", "Kelly's"]),
    ("schwarz-gruppe", "schwarz-gruppe", "retail_distribution", ["Kaufland", "PreZero", "Schwarz Digits", "MEG", "Solent", "Bonback", "Freshona", "Milbona", "Crivit", "Parkside", "Silvercrest", "Esmara", "Livarno", "Cien", "Formil", "W5", "Bellarom", "Combino", "Favorina", "Deluxe"]),
    ("euralis", "euralis", "food", ["Montfort", "Rougié", "Pierre Guillaumin", "Jean Larnaudie", "Euralis Semences", "Lur Berri"]),
    ("schwarz-gruppe#kz", "schwarz-gruppe", "retail_distribution", []),
]
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
ents = supabase_client.get_all(c, "entities", {"select": "slug,display_name,legal_name,parent_id,is_brand"})
def plain(t):
    return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()).strip()
connus = {plain(e.get("display_name")) for e in ents} | {plain(e.get("legal_name")) for e in ents}
slugs = {e["slug"] for e in ents}
CUE = re.compile(r"\b(brands?|marques?|portfolio|portefeuille|Marken|label|maison|houses?|Maisons)\b", re.I)
out = []
for key, groupe, secteur, marques in CIBLES:
    if not marques or key not in DEP: continue
    p = os.path.join(S, "cache_rapports", hashlib.sha256(DEP[key]["report_url"].encode()).hexdigest()[:16] + ".txt")
    if not os.path.exists(p): print("pas de texte", key); continue
    t = open(p, encoding="utf-8").read()
    for m in marques:
        if plain(m) in connus:
            continue
        pat = r"(?<![\w])" + re.escape(m).replace(r"\ ", r"\s+") + r"(?![\w])"
        best = None
        for x in re.finditer(pat, t):
            ctx = t[max(0, x.start() - 220): x.end() + 220]
            if CUE.search(ctx):
                best = ctx; break
            best = best or ctx
        out.append({"cle": key, "groupe": groupe, "secteur": secteur, "marque": m, "trouvee": best is not None, "passage": best})
json.dump(out, open(os.path.join(S, "marques_candidats.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(sum(1 for o in out if o["trouvee"]), "marques nouvelles citées ;", sum(1 for o in out if not o["trouvee"]), "non citées dans le rapport")
for o in out:
    print(("✓ " if o["trouvee"] else "✗ ") + o["groupe"], "|", o["marque"])
