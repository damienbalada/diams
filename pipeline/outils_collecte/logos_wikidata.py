"""Base de logos des fiches : un logo par groupe et par marque, quand on peut le trouver sans
risque de confusion.

Ordre de recherche :
  1. logos déjà enregistrés dans apps/web/public/logos (icônes officielles des sites) ;
  2. Wikidata, propriété « logo » (P154, fichier de Wikimedia Commons), pour l'élément
     retrouvé par identifiant officiel : LEI (P1278) ou SIREN (P1616) pour les groupes ; pour
     une marque, l'élément dont le nom correspond exactement et qui appartient au groupe
     retrouvé (P127 propriétaire, P176 fabricant, P749 organisation mère, P1830 possède,
     P1716 marque) ;
  3. icône du site officiel (P856 de Wikidata, ou liste des sites officiels vérifiés par les
     mentions légales), par le service d'icônes de Google, seulement si elle fait au moins
     64 pixels.

Puis lancer logos_filtre.py (icônes de site partagées par des marques de noms différents).
Un logo identifie l'entreprise : ce n'est pas une preuve, et Wikidata ne sert ici qu'à trouver
une image. Écrit apps/web/lib/logos.json : { slug: { src, origine } }.
"""
import csv, json, os, re, sys, time, unicodedata
from urllib.parse import quote, urlparse
import httpx

sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client

RACINE = r"C:\Users\damie\Downloads\claude\awareness-score"
SORTIE = os.path.join(RACINE, "apps", "web", "lib", "logos.json")
H = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}
web = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=90, follow_redirects=True, headers=H)
db = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)


def plain(t):
    t = unicodedata.normalize("NFKD", (t or "").replace("’", "'")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def sparql(q):
    for essai in range(3):
        r = web.post("https://query.wikidata.org/sparql", data={"query": q, "format": "json"}, headers={**H, "Accept": "application/sparql-results+json"})
        if r.status_code == 200:
            return r.json()["results"]["bindings"]
        time.sleep(5 * (essai + 1))
    print("SPARQL refusé :", r.status_code, r.text[:200])
    return []


def val(b, k):
    return b[k]["value"] if k in b else None


def commons(url):
    # http://commons.wikimedia.org/wiki/Special:FilePath/Nom.svg → vignette PNG de 160 px
    nom = url.rsplit("/", 1)[-1]
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{nom}?width=160"


ents = supabase_client.get_all(db, "entities", {"select": "id,slug,display_name,legal_name,is_brand,lei,siren,parent_id"})
par_id = {e["id"]: e for e in ents}
logos = {}

# 1. logos locaux
for f in os.listdir(os.path.join(RACINE, "apps", "web", "public", "logos")):
    logos[os.path.splitext(f)[0]] = {"src": f"/logos/{f}", "origine": "site officiel"}

# Choix manuels : l'icône du site n'est pas le logo (Coca-Cola : pictogramme noir de l'application).
logos["coca-cola"] = {"src": "https://commons.wikimedia.org/wiki/Special:FilePath/Coca-Cola%20logo.svg?width=160", "origine": "Wikimedia Commons"}

# 2a. groupes par LEI et SIREN
qid_de = {}  # slug -> QID
site_de = {}  # slug -> domaine officiel
groupes = [e for e in ents if not e["is_brand"] or e.get("lei") or e.get("siren")]
for prop, cle in (("P1278", "lei"), ("P1616", "siren")):
    vals = [e for e in groupes if e.get(cle)]
    for i in range(0, len(vals), 150):
        lot = vals[i:i + 150]
        q = ("SELECT ?id ?item ?logo ?site WHERE { VALUES ?id { " + " ".join(f'"{e[cle]}"' for e in lot) + " } "
             f"?item wdt:{prop} ?id . OPTIONAL {{ ?item wdt:P154 ?logo }} OPTIONAL {{ ?item wdt:P856 ?site }} }}")
        for b in sparql(q):
            for e in lot:
                if e[cle] == val(b, "id"):
                    qid_de.setdefault(e["slug"], val(b, "item").rsplit("/", 1)[-1])
                    if val(b, "logo") and e["slug"] not in logos:
                        logos[e["slug"]] = {"src": commons(val(b, "logo")), "origine": "Wikimedia Commons"}
                    if val(b, "site"):
                        site_de.setdefault(e["slug"], val(b, "site"))
        time.sleep(1)
print("groupes retrouvés sur Wikidata :", len(qid_de))

# 2b. marques : éléments rattachés au groupe retrouvé, au nom identique
marques_de = {}  # QID du groupe -> [marques de la base]
for e in ents:
    if not e["is_brand"]:
        continue
    g, vus = par_id.get(e["parent_id"]), 0
    while g and vus < 4:  # le groupe direct, puis ses propriétaires
        if g["slug"] in qid_de:
            marques_de.setdefault(qid_de[g["slug"]], []).append(e)
        g, vus = par_id.get(g["parent_id"]), vus + 1
qids = list(marques_de)
for i in range(0, len(qids), 40):
    lot = qids[i:i + 40]
    q = ("SELECT ?g ?item ?lab ?logo ?site WHERE { VALUES ?g { " + " ".join(f"wd:{x}" for x in lot) + " } "
         "{ ?item wdt:P127|wdt:P176|wdt:P749 ?g } UNION { ?g wdt:P1830|wdt:P1716 ?item } "
         "?item rdfs:label ?lab . FILTER(LANG(?lab) IN ('fr','en')) "
         "OPTIONAL { ?item wdt:P154 ?logo } OPTIONAL { ?item wdt:P856 ?site } }")
    res = sparql(q)
    for b in res:
        g = val(b, "g").rsplit("/", 1)[-1]
        lab = plain(val(b, "lab"))
        for e in marques_de.get(g, []):
            noms = {plain(e.get("display_name")), plain(e.get("legal_name"))}
            if lab and lab in noms:
                if val(b, "logo") and e["slug"] not in logos:
                    logos[e["slug"]] = {"src": commons(val(b, "logo")), "origine": "Wikimedia Commons"}
                if val(b, "site"):
                    site_de.setdefault(e["slug"], val(b, "site"))
    time.sleep(1)
print("logos après Wikidata :", len(logos))

# 3. icône du site officiel
for f, col_slug, col_site in (("sites_officiels_2026-10-15.csv", "brand_slug", "site"), ("sites_officiels_marques_2026-10-15.csv", "marque", "site"),
                              ("sites_officiels_logos_2026-10-16.csv", "slug", "site")):
    if not os.path.exists(os.path.join(RACINE, "pipeline", "curated", f)):
        continue
    with open(os.path.join(RACINE, "pipeline", "curated", f), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r.get(col_site):
                site_de[r[col_slug]] = r[col_site]


def taille_png(b):
    return int.from_bytes(b[16:20], "big") if b[:8] == b"\x89PNG\r\n\x1a\n" else 0


manque = [s for s in site_de if s not in logos]
print("icônes de site à essayer :", len(manque))
for n, slug in enumerate(manque):
    dom = urlparse(site_de[slug] if "//" in site_de[slug] else "https://" + site_de[slug]).netloc
    if not dom:
        continue
    url = f"https://www.google.com/s2/favicons?domain={quote(dom)}&sz=128"
    try:
        r = web.get(url)
    except Exception:
        continue
    if r.status_code == 200 and taille_png(r.content) >= 64:
        logos[slug] = {"src": url, "origine": f"icône du site {dom}"}
    if n % 100 == 0:
        print(n, len(logos))
    time.sleep(0.2)

# 4. icône déclarée par le site officiel lui-même (apple-touch-icon, icon), enregistrée dans le
#    projet (apps/web/public/logos/auto), pour les sites dont Google ne connaît qu'une petite icône.
import html as _html
from urllib.parse import urljoin
AUTO = os.path.join(RACINE, "apps", "web", "public", "logos", "auto")
os.makedirs(AUTO, exist_ok=True)


def taille_tag(tag):
    m = re.search(r'sizes="(\d+)x', tag)
    return int(m.group(1)) if m else (180 if "apple-touch" in tag else 32)


reste = [s for s in site_de if s not in logos]
print("icônes déclarées à essayer :", len(reste))
for n, slug in enumerate(reste):
    url = site_de[slug] if "//" in site_de[slug] else "https://" + site_de[slug]
    try:
        r = web.get(url, timeout=15)
    except Exception:
        continue
    if r.status_code != 200:
        continue
    cands = []
    for tag in re.findall(r"<link[^>]+>", r.text, re.I):
        if re.search(r'rel="[^"]*(apple-touch-icon|icon)[^"]*"', tag, re.I):
            h = re.search(r'href="([^"]+)"', tag)
            if h:
                cands.append((taille_tag(tag), urljoin(str(r.url), _html.unescape(h.group(1)))))
    cands.sort(reverse=True)
    cands.append((180, urljoin(str(r.url), "/apple-touch-icon.png")))
    for t_, u in cands:
        if t_ < 64:
            continue
        try:
            i = web.get(u, timeout=15)
        except Exception:
            continue
        ct = i.headers.get("content-type", "")
        svg = "svg" in ct or u.split("?")[0].endswith(".svg")
        if i.status_code != 200 or len(i.content) < 300 or not ("image" in ct or svg):
            continue
        if not svg and "png" in ct and taille_png(i.content) < 64:
            continue
        ext = "svg" if svg else "png" if "png" in ct else "jpg" if ("jpeg" in ct or "jpg" in ct) else "webp" if "webp" in ct else None
        if not ext:
            continue
        open(os.path.join(AUTO, f"{slug}.{ext}"), "wb").write(i.content)
        logos[slug] = {"src": f"/logos/auto/{slug}.{ext}", "origine": f"icône du site {urlparse(str(r.url)).netloc}"}
        break
    if n % 50 == 0:
        print(n, len(logos))

# Une marque ne prend jamais le logo de son groupe (élément Wikidata mal rattaché, icône commune).
par_slug = {e["slug"]: e for e in ents}
for e in ents:
    if not e["is_brand"] or e["slug"] not in logos:
        continue
    g, vus = par_id.get(e["parent_id"]), 0
    while g and vus < 5:
        nm, ng = plain(e.get("display_name") or e["legal_name"]).replace(" ", ""), plain(g.get("display_name") or g["legal_name"]).replace(" ", "")
        if logos.get(g["slug"], {}).get("src") == logos[e["slug"]]["src"] and nm not in ng and ng not in nm:
            print("écarté (logo du groupe) :", e["slug"])
            del logos[e["slug"]]
            break
        g, vus = par_id.get(g["parent_id"]), vus + 1

slugs = {e["slug"] for e in ents}
logos = {k: v for k, v in sorted(logos.items()) if k in slugs}
json.dump(logos, open(SORTIE, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
nb_m = sum(1 for e in ents if e["is_brand"] and e["slug"] in logos)
nb_g = sum(1 for e in ents if not e["is_brand"] and e["slug"] in logos)
print(f"{len(logos)} logos écrits : {nb_g} groupes sur {len(ents) - sum(e['is_brand'] for e in ents)}, {nb_m} marques sur {sum(e['is_brand'] for e in ents)}")
