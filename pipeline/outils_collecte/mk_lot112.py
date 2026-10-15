"""Lot 112 : exploitation animale propre à des marques, d'après leur site officiel prouvé (mentions
légales ou droits d'auteur nommant le propriétaire, curated/sites_officiels_logos_2026-10-16.csv) ;
phrases relues à la main : produit réellement vendu, pas une recette, un arôme ni une trace."""
import csv, json, os, sys
from urllib.parse import urlparse
sys.stdout.reconfigure(encoding="utf-8")
S = os.path.dirname(os.path.abspath(__file__))
R = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline"
OUT = os.path.join(R, "curated", "groupes_2026-10_lot112_animal_sites_officiels.csv")
SITES = {r["slug"]: r for r in csv.DictReader(open(os.path.join(R, "curated", "sites_officiels_logos_2026-10-16.csv"), encoding="utf-8"))}
SCAN = {r["slug"]: r for r in json.load(open(os.path.join(S, "ani_scan9.json"), encoding="utf-8"))}
CHOIX = {  # marque: (début de la phrase retenue, produit)
    "annies": ("Deluxe Mac & Cheese", "fromage"), "arla-marque": ("A dairy cooperative", "produits laitiers"),
    "biscuiterie-husson-marque": ("Pâte feuilletée pur beurre", "beurre"), "cite-marine-marque": ("Nos poissons cuisinés", "poisson"),
    "clairefontaine": ("Sacs cuir", "cuir"), "crosta-et-mollica-marque": ("Jambon • Pesto", "jambon"),
    "dunkaroos": ("Contains milk", "lait"), "fraiche-pizz-marque": ("JAMBON MOZZA", "jambon et fromage"),
    "gardettos": ("CONTAINS WHEAT AND MILK", "lait"), "haagen-dazs": ("Chaque boule commence", "lait, crème et œufs"),
    "heinz": ("Contient : œufs", "œufs"), "huitres-geay-marque": ("Nos Huîtres", "huîtres"),
    "hisense": ("Fabriquée en cuir véritable", "cuir"), "jim-beam": ("Jim Beam Honey", "miel"),
    "mccain-frites": ("Bun's Jambon 4 Fromages", "jambon et fromage"), "merci-storck": ("Milk Praliné", "lait"),
    "nature-valley": ("Crunchy Avoine & Miel", "miel"), "oreo": ("Allergens CONTAINS", "lait"),
    "perfect-fit": ("PERFECT FIT ADULT 1+ Croquettes Riche en Saumon", "saumon"), "picard-magasins": ("Volailles", "volaille"),
    "robitussin": ("True Source Certified Honey", "miel"), "strepsils": ("Strepsils Miel Citron x24", "miel"),
    "tostitos": ("Tostitos® Chipotle Chicken", "poulet"), "totinos": ("Cheese Pizza Rolls", "fromage"),
    "zolux-marque": ("Crunchy Dog Poulet", "poulet"), "cheerios": ("Honey Nut Cheerios", "miel"),
    "chex": ("Honey Nut Chex", "miel"), "cascadian-farm": ("Oats & Honey Granola", "miel"), "fiber-one": ("Honey Clusters", "miel"),
    "le-cabanon-marque": ("Le Cabanon accorde", "viande"), "skoda": ("Un intérieur élégant en cuir noir", "cuir"),
}
VEG = {"kokiriki-marque": ("Large gamme 100% végétale", None), "nuttree-marque": ("OUI ! ET TOUJOURS BIO, VEGAN", None)}
cols = "entity_slug,indicator_code,source_code,nature,observed_on,value_type,value_numeric,value_boolean,value_text,normalized_value,confidence,source_url,excerpt,review_note".split(",")
rows, manque = [], []
def site_txt(slug):
    s = SITES[slug]; dom = urlparse(s["site"]).netloc
    how = "son SIREN figure dans les mentions légales" if s["preuve"] == "siren" else "ses mentions légales ou droits d'auteur nomment la société propriétaire"
    return dom, how
for slug, (debut, val) in {**CHOIX, **VEG}.items():
    sc = SCAN.get(slug)
    lst = (sc or {}).get("veg" if slug in VEG else "ani", []) + (sc or {}).get("ani", [])
    hit = next((x for x in lst if x["q"].startswith(debut) or debut in x["q"]), None)
    if not hit or slug not in SITES:
        manque.append(slug); continue
    dom, how = site_txt(slug)
    if slug in VEG:
        ex = f"Site officiel ({dom} ; {how}), à propos de toute la marque : « {hit['q']} » — marque entièrement végétale."
        rows.append({c: "" for c in cols} | {"entity_slug": slug, "indicator_code": "ANI_ANIMAL_FREE", "source_code": "COMPANY_REPORT", "nature": "result",
                    "observed_on": "2026-10-16", "value_type": "boolean", "value_boolean": "true", "normalized_value": "1", "confidence": "0.85",
                    "source_url": hit["url"], "excerpt": ex})
    else:
        ex = f"Site officiel ({dom} ; {how}) : « {hit['q']} » — recours à l'exploitation animale ({val})."
        rows.append({c: "" for c in cols} | {"entity_slug": slug, "indicator_code": "ANI_EXPLOITATION", "source_code": "COMPANY_REPORT", "nature": "result",
                    "observed_on": "2026-10-16", "value_type": "category", "value_text": val, "normalized_value": "0", "confidence": "0.85",
                    "source_url": hit["url"], "excerpt": ex})
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
print(len(rows), "preuves ; introuvables :", manque)
