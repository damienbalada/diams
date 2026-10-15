"""Lot 102 : exploitation animale et offre végétale relevées sur les sites officiels des marques
(sites prouvés par le SIREN ou la raison sociale du propriétaire dans les mentions légales,
trouve_sites2.py), tri à la main des passages relevés par ani_scan8.py : recettes, arômes,
accords mets-vins, cosmétiques (« peau », « lait corps ») et laits infantiles écartés."""
import csv
import json
import os
import re
import sys
from urllib.parse import urlparse

import httpx

sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client  # noqa: E402

S = os.path.dirname(os.path.abspath(__file__))
OUT = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline\curated\groupes_2026-10_lot102_animal_sites_marques.csv"
SITES_OUT = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline\curated\sites_officiels_marques_2026-10-15.csv"
COLS = ["entity_slug", "indicator_code", "source_code", "nature", "observed_on", "value_type", "value_numeric", "value_boolean",
        "value_text", "normalized_value", "confidence", "source_url", "excerpt", "review_note"]

# (slug, fragment exact du passage, mot-clé affiché)
EXPLOIT = [
    ("le-grand-lejon-marque", "Rillettes de poisson", "poisson"), ("feyel", "Maison de Foie Gras Alsacienne depuis 1811", "foie gras"),
    ("kaviari-marque", "Tous nos caviars", "caviar"), ("menguys", "Cracky's soufflé de maïs Fromage", "fromage"),
    ("chocmod-marque", "Oursons Guimauves enrobés de chocolat au Lait", "lait"), ("herta-marque", "Jambons blancs", "jambon"),
    ("coraya", "finement préparés avec du poisson sauvage issu de la pêche responsable", "poisson"), ("tropic-apero-marque", "Délice d'anchois", "anchois"),
    ("baileys", "Irish dairy cream", "crème laitière"), ("president", "Fondue aux 3 fromages", "fromage"),
    ("voie-verte-marque", "Viande de bœuf, porc et veau garantie origine France", "viande"),
    ("origine-truffe-marque", "Beurre à la truffe blanche", "beurre"), ("i-grec-marque", "ce n’est pas juste des spécialités laitières", "lait"),
    ("mix-buffet-marque", "Poulet Pané Caesar", "poulet"), ("gerlinea", "Barres Crousti - Chocolat au lait", "lait"),
    ("labeyrie-marque", "Foie gras & filière canard", "foie gras"), ("emile-noel", "Vinaigre de Kombucha Ail Noir et Miel", "miel"),
    ("lanquetot", "En moyenne 65 vaches laitières par cheptel", "lait"), ("brets", "Saveur Caramel au beurre salé", "beurre"),
    ("tramier", "Barres Énergétiques Miel & Mix Croquant Tramier", "miel"), ("matines", "Nos Oeufs", "oeufs"),
    ("mathez", "Truffes caramel beurre salé - Mathez", "beurre"), ("ninkasi", "Bœuf VBF – Poulet mariné – Poulet frit", "viande"),
    ("royco", "Bouillon Volaille & Vermicelles", "volaille"), ("valfleuri", "Aux 7 oeufs frais plein air par kilo", "oeufs"),
    ("banania", "Lait gourmand saveur Vanille", "lait"), ("nuxe", "Rêve de Miel : devenez addict au Miel", "miel"),
    ("bridelice", "Crème fraiche et produits à base de crème légère Bridélice", "crème"),
    ("galzin-marque", "FRIAND A LA VIANDE", "viande"), ("daucy", "Plats cuisinés à base de poisson", "poisson"),
    ("kaoka-marque", "Chocolat au lait fin et fondant 32% cacao", "lait"), ("vrai", "Skyr nature au lait de brebis", "lait"),
    ("cassegrain", "Lentilles cuisinées et graisse de canard", "canard"), ("baiko", "Yaourts de Savoie et de caractère depuis 1956", "yaourt"),
    ("brioche-pasquier", "Pains au Lait Bio", "lait"), ("paysan-breton", "PAYSAN BRETON : beurre, crepe, lait ribot, fromage fouetté", "beurre"),
    ("thiriet", "Viandes, volailles", "viande"), ("starwax", "Spray détachant au fiel de boeuf", "fiel de bœuf"),
    ("maison-briau-marque", "Morue et autres espèces de poissons", "poisson"), ("olvac-marque", "Mogette de Vendée au jambon", "jambon"),
    ("c-est-qui-le-patron", "Le nouvel emballage de notre lait", "lait"), ("mercurochrome", "LA GAMME AU MIEL D'ACACIA", "miel"),
    ("grainpop", "pop-corn fromage de chèvre", "fromage"), ("gayelord-hauser", "Galette Froment Chocolat au Lait", "lait"),
    ("roquefort-societe", "Notre lait de brebis est collecté auprès de fermes locales", "lait"),
    ("biosoleil", "Petits donuts nappés au chocolat au lait équitable", "lait"),
    ("le-mochi-glace", "Lait et produits à base de lait, fruits à coque et soja", "lait"), ("francois-doucet", "Perles de miel - Terroir IGP", "miel"),
    ("chaussee-aux-moines", "Nos fromages", "fromage"), ("naturactive", "Huile de poissons", "poisson"),
    ("la-boulangere", "Pains au lait frais Bio", "lait"), ("valbreso", "100% Pure Sheep Milk Cheese", "lait de brebis"),
    ("apifruit", "POIRE WILLIAMS AU MIEL EN CUBE", "miel"), ("vrai-et-bon", "Terrine Pur Porc", "porc"),
    ("garbit", "Poulet & Merguez", "poulet"), ("thaas-chips-marque", "Au chocolat au lait", "lait"),
    ("pure-via", "Pure Via ® Chocolat au Lait", "lait"),
]
VEGE = [
    ("baileys", "Nutty vegan Baileys Almande"), ("gerard-bertrand", "Vin Vegan"), ("st-hubert-marque", "Plaisir 100% Végétal"),
    ("le-mochi-glace", "Vegan – Plein fruit"), ("naturactive", "VEGAN INFO Naturactive : sans ingrédient d’origine animale."),
    ("panzani-marque", "Sauce Bolognaise 100% Végétale"), ("primevere", "Une large gamme 100% végétale"),
    ("tossolia-marque", "Découvrez toutes nos gammes 100% végétales"),
]
LIBRE = [("tossolia-marque", "Découvrez toutes nos gammes 100% végétales", "Pour une cuisine 100% végétale")]

scan = {r["slug"]: r for r in json.load(open(os.path.join(S, "ani_scan8.json"), encoding="utf-8"))}
sites = {r["slug"]: r for r in json.load(open(os.path.join(S, "sites_marques.json"), encoding="utf-8")) if r.get("site")}
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
ents = supabase_client.get_all(c, "entities", {"select": "id,slug,display_name,siren,parent_id"})
by_id = {e["id"]: e for e in ents}
by_slug = {e["slug"]: e for e in ents}


def chaine(e):
    out, cur = [], e
    for _ in range(20):
        if not cur.get("parent_id") or cur["parent_id"] not in by_id:
            break
        cur = by_id[cur["parent_id"]]
        out.append(cur)
    return out


def garantie(slug):
    s = sites[slug]
    hote = urlparse(s["site"]).netloc
    if s["type"] == "siren":
        for x in chaine(by_slug[slug]):
            n = x.get("siren")
            if n and re.search(r"(?<!\d)" + r"[\s\u00a0.]?".join([n[0:3], n[3:6], n[6:9]]) + r"(?!\d)", s["extrait"]):
                return f"Site officiel ({hote}, édité par la société propriétaire, SIREN {n} dans ses mentions légales)"
        raise SystemExit("SIREN introuvable " + slug)
    return f"Site officiel ({hote}, sa page de mentions légales nomme la société propriétaire de la marque)"


def trouve(slug, frag):
    r = scan[slug]
    for x in r["ani"] + r["veg"]:
        if frag in x["q"]:
            return x["url"]
    raise SystemExit(f"fragment introuvable {slug} : {frag}")


rows = []
base = {c_: "" for c_ in COLS}
for slug, frag, kw in EXPLOIT:
    nom = sites[slug]["nom"]
    rows.append({**base, "entity_slug": slug, "indicator_code": "ANI_EXPLOITATION", "source_code": "COMPANY_REPORT", "nature": "result",
                 "observed_on": "2026-10-15", "value_type": "category", "value_text": kw, "normalized_value": 0, "confidence": 0.85,
                 "source_url": trouve(slug, frag),
                 "excerpt": f"{garantie(slug)}, produits de la marque {nom} : « {frag} » — recours à l'exploitation animale ({kw})."})
for slug, frag in VEGE:
    nom = sites[slug]["nom"]
    rows.append({**base, "entity_slug": slug, "indicator_code": "ANI_OFFRE_VEGETALE", "source_code": "COMPANY_REPORT", "nature": "result",
                 "observed_on": "2026-10-15", "value_type": "boolean", "value_boolean": "true", "normalized_value": 1, "confidence": 0.85,
                 "source_url": trouve(slug, frag),
                 "excerpt": f"{garantie(slug)}, produits de la marque {nom} : « {frag} » — au moins un produit 100 % végétal"
                            + ("." if slug in {x[0] for x in LIBRE} else " (la marque n'est pas pour autant entièrement végétale).")})
for slug, frag, frag2 in LIBRE:
    nom = sites[slug]["nom"]
    rows.append({**base, "entity_slug": slug, "indicator_code": "ANI_ANIMAL_FREE", "source_code": "COMPANY_REPORT", "nature": "result",
                 "observed_on": "2026-10-15", "value_type": "boolean", "value_boolean": "true", "normalized_value": 1, "confidence": 0.85,
                 "source_url": trouve(slug, frag),
                 "excerpt": f"{garantie(slug)}, à propos de toute la marque {nom} : « {frag} » — marque entièrement végétale."})
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(rows)
# liste des sites officiels prouvés (traçabilité)
EXCLUS = set(open(os.path.join(S, "ani_scan8.py"), encoding="utf-8").read().split('EXCLUS = set("')[1].split('"')[0].split())
with open(SITES_OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["marque", "groupe", "site", "page_de_preuve", "preuve", "extrait"])
    for s in sites.values():
        if s["slug"] not in EXCLUS:
            w.writerow([s["slug"], s["groupe"], s["site"], s["preuve"], s["type"], s["extrait"]])
print(len(rows), "lignes ;", len(sites) - len(EXCLUS & set(sites)), "sites consignés")
