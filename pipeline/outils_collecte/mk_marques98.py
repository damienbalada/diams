"""Lot de marques 98 : pages de marques des sites officiels des groupes (Savencia, Cémoi, Euralis,
LDC). Pour chaque page, la citation est la première phrase qui nomme la marque ; la page est sur le
domaine du groupe, ce qui atteste le lien de propriété."""
import csv, json, os, re, sys, unicodedata, html
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
import httpx
from diams import supabase_client
from diams.esrs_candidates import fetch_text
S = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(S, "cache_rapports")
OUT = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline\curated\marques_2026-10_lot98_pages_marques_groupes.csv"
SAV = "https://savencia.com/marque/"
LISTE = [  # groupe, secteur, nom affiché, url, motif du nom dans le texte
    ("savencia", "food", "Alouette", SAV + "alouette/", r"Alouette"), ("savencia", "food", "Balade", SAV + "balade/", r"Balade"),
    ("savencia", "food", "Bresso", SAV + "bresso/", r"Bresso"), ("savencia", "food", "Brunch", SAV + "brunch/", r"Brunch"),
    ("savencia", "food", "Burgo de Arias", SAV + "burgo-de-arias/", r"Burgo de Arias"), ("savencia", "food", "Corman", SAV + "corman/", r"Corman"),
    ("savencia", "food", "Delaco", SAV + "delaco/", r"Delaco"), ("savencia", "food", "Elle & Vire", SAV + "elle-et-vire/", r"Elle\s?(?:&|et)\s?Vire"),
    ("savencia", "food", "Géramont", SAV + "geramont/", r"G[ée]ramont"), ("savencia", "food", "Île de France", SAV + "ile-de-france/", r"[ÎI]le de France"),
    ("savencia", "food", "Král Sýrů", SAV + "kral-syru/", r"Kr[áa]l S[ýy]r[ůu]"), ("savencia", "food", "Lucina", SAV + "lucina/", r"Lucina"),
    ("savencia", "food", "Medve", SAV + "medve/", r"Medve"), ("savencia", "food", "Milkana", SAV + "milkana/", r"Milkana"),
    ("savencia", "food", "Milkaut", SAV + "milkaut/", r"Milkaut"), ("savencia", "food", "Polenghi", SAV + "polenghi-2/", r"Polenghi"),
    ("savencia", "food", "Rogue Creamery", SAV + "rogue-creamery/", r"Rogue Creamery"), ("savencia", "food", "Santa Rosa", SAV + "santa-rosa/", r"Santa Rosa"),
    ("cemoi", "food", "Quadro", "https://www.cemoi.fr/nos-marques/", r"Quadro"),
    ("euralis", "food", "Qualité Traiteur", "https://www.euralis.fr/wp-content/uploads/2026/01/Euralis-rapport-DPEF-2024-2025-FR.pdf", r"Qualit[ée] Traiteur"),
]
db = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
ents = supabase_client.get_all(db, "entities", {"select": "slug,display_name,legal_name"})
slugs = {e["slug"] for e in ents}
def plain(t):
    return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", (t or "").replace("’", "'")).encode("ascii", "ignore").decode().lower()).strip()
connus = {plain(e.get("display_name")) for e in ents} | {plain(e.get("legal_name")) for e in ents}
def slugify(n):
    s = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode().lower()).strip("-")
    while s in slugs: s += "-marque"
    slugs.add(s); return s
rows = []
for g, sec, nom, url, pat in LISTE:
    if plain(nom) in connus: print("déjà :", nom); continue
    try:
        t = re.sub(r"\s+", " ", fetch_text(url, CACHE))
    except Exception as x:
        print("illisible :", nom, type(x).__name__); continue
    # première phrase (≥ 40 caractères) qui nomme la marque, hors menus
    best = None
    for m in re.finditer(pat, t):
        a = max(t.rfind(". ", 0, m.start()), t.rfind("! ", 0, m.start()), m.start() - 200) + 2
        b = t.find(". ", m.end()); b = len(t) if b < 0 else b
        phr = t[a:b].strip()
        if 40 <= len(phr) <= 260 and not re.search(r"Accueil|Menu|Cookies|Nous rejoindre", phr):
            best = phr; break
    if not best: print("pas de phrase :", nom); continue
    rows.append({"brand_slug": slugify(nom), "brand_name": nom, "group_slug": g, "sector_code": sec, "source_kind": "website",
                 "source_url": url, "doc": "Site officiel du groupe (page de la marque)" if "savencia" in url or "cemoi" in url else "Déclaration de performance extra-financière 2024-2025 d'Euralis",
                 "quote": best, "observed_on": "2026-10-15", "animal_free": "", "display_name": nom})
    print("✓", nom, "|", best[:160])
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "marques")
