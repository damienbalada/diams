"""Pages « nos marques » des sites officiels des groupes : relève les noms (textes de liens, alt
d'images, titres) absents de la base, pour tri à la main. Identité déclarée du vérificateur."""
import html, json, os, re, sys, time, unicodedata
import httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client
S = os.path.dirname(os.path.abspath(__file__))
H = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}
PAGES = {
    "lactalis": ["https://www.lactalis.fr/nos-marques/", "https://www.lactalis.fr/marques/"],
    "savencia": ["https://www.savencia.com/fr/nos-marques", "https://www.savencia-fromagedairy.com/fr/marques/"],
    "bel": ["https://www.groupe-bel.com/fr/marques/", "https://www.groupe-bel.com/fr/nos-marques/"],
    "sodiaal": ["https://sodiaal.coop/nos-marques/", "https://sodiaal.coop/marques/"],
    "bonduelle": ["https://www.bonduelle.com/fr/marques.html", "https://www.bonduelle.com/fr/nos-marques.html"],
    "andros": ["https://www.andros.fr/nos-marques", "https://www.groupe-andros.com/marques"],
    "lea-nature": ["https://www.leanature.com/fr_fr/nos-marques.html"],
    "ecotone-france": ["https://www.ecotone.bio/fr/nos-marques", "https://www.ecotone.bio/nos-marques"],
    "avril": ["https://www.avril.com/fr/nos-marques", "https://www.avril.com/marques"],
    "agrial": ["https://www.agrial.com/nos-marques/", "https://www.agrial.com/marques/"],
    "ldc": ["https://www.ldc.fr/marques/", "https://www.ldc.fr/nos-marques/"],
    "eureden": ["https://www.eureden.com/nos-marques/", "https://www.eureden.com/marques/"],
    "terrena": ["https://www.terrena.fr/nos-marques/"],
    "cooperl": ["https://www.cooperl.com/nos-marques", "https://www.cooperl.com/marques"],
    "fleury-michon": ["https://www.fleurymichon.fr/nos-marques"],
    "euralis": ["https://www.euralis.fr/nos-marques/"],
    "nutrimaine": ["https://www.nutrimaine.com/marques"],
    "st-michel": ["https://www.stmichel.fr/nos-marques"],
    "cemoi": ["https://www.cemoi.fr/nos-marques"],
    "materne": ["https://www.materne.fr/nos-marques"],
}
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60, follow_redirects=True, headers=H)
db = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
ents = supabase_client.get_all(db, "entities", {"select": "slug,display_name,legal_name"})
slugs = {e["slug"] for e in ents}
def plain(t):
    return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", (t or "").replace("’", "'")).encode("ascii", "ignore").decode().lower()).strip()
connus = {plain(e.get("display_name")) for e in ents} | {plain(e.get("legal_name")) for e in ents}
out = {}
for g, urls in PAGES.items():
    if g not in slugs:
        print("groupe absent de la base :", g); continue
    for u in urls:
        try:
            r = c.get(u)
        except Exception as x:
            print("erreur", g, u, type(x).__name__); continue
        if r.status_code == 403:
            time.sleep(3); r = c.get(u)
        print(r.status_code, g, u, len(r.text))
        if r.status_code != 200:
            continue
        h = r.text
        noms = set()
        for a in re.findall(r'alt="([^"]{2,40})"', h):
            noms.add(html.unescape(a))
        for a in re.findall(r"<(?:h2|h3|h4)[^>]*>(.*?)</(?:h2|h3|h4)>", h, re.S):
            t = re.sub(r"<[^>]+>", "", html.unescape(a)).strip()
            if 2 <= len(t) <= 40: noms.add(t)
        for a in re.findall(r'href="[^"]*(?:marque|brand)s?/([a-z0-9-]{2,40})/?"', h):
            noms.add(a.replace("-", " "))
        nouveaux = sorted(n for n in noms if plain(n) and plain(n) not in connus and not re.search(r"logo|image|icon|menu|fermer|close", n, re.I))
        out[g] = {"url": str(r.url), "noms": nouveaux}
        break
    time.sleep(1)
json.dump(out, open(os.path.join(S, "pages_marques.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for g, v in out.items():
    print("##", g, v["url"], "|", " · ".join(v["noms"][:50]))
