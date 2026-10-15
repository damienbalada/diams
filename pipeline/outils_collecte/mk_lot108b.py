"""Lot 108 : exploitation animale propre à des marques de mode et de luxe, d'après le rapport de leur
groupe (Kering, LVMH, Hermès, Richemont). La phrase nomme la marque ET la matière animale."""
import csv, hashlib, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
S = os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
OUT = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline\curated\groupes_2026-10_lot108b_animal_marques_luxe.csv"
L = [
    ("gucci", "kering", "en 2025, Gucci continue d’adopter des approches et des solutions visant à optimiser la fabrication du cuir", "cuir"),
    ("saint-laurent", "kering", "Saint Laurent intègre 50 % de cuir réutilisé dans certains modèles de sacs de la ligne Sunset", "cuir (sacs)"),
    ("bottega-veneta", "kering", "Bottega Veneta a mis en place plusieurs projets de recyclage et réutilisation de ses chutes de cuir", "cuir"),
    ("balenciaga", "kering", "Balenciaga qui a notamment utilisé un cuir tanné à base de tannage Oleum pour une gamme de chaussures", "cuir (chaussures)"),
    ("boucheron", "kering", "le nouvel écrin à bijoux de Boucheron (depuis 2023), composé de seulement deux matériaux (remplaçant les 15 initiaux) : aluminium (dont 15 % d’aluminium recyclé) et feutre (laine certifiée RWS)", "laine (écrins à bijoux)"),
    ("louis-vuitton", "lvmh", "En Espagne, les ateliers Louis Vuitton, en plus de la fabrication de maroquinerie, concentrent également l’ensemble de l’activité Accessoires Cuir (ceintures, bracelets)", "cuir (ceintures, bracelets)"),
    ("loro-piana", "lvmh", "Loro Piana a développé la Loro Capsule, une collection exclusive de produits réalisés à partir des surplus de cachemire des Maisons du Groupe", "cachemire"),
    ("hermes-maison", "hermes", "les objets Hermès sont essentiellement composés de matières emblématiques telles que le cuir, la soie, le cachemire", "cuir, soie, cachemire"),
    ("montblanc", "richemont", "Montblanc also creates elegant, sophisticated and innovative designs in the fields of fine leather and fine watchmaking", "cuir (maroquinerie)"),
    ("chloe", "richemont", "The relaunch of the Paddington bag reaffirmed Chloé’s heritage and timeless design in leather goods", "cuir (maroquinerie)"),
]
def nom_doc(d):
    return d.get("doc") or f"Document d'enregistrement universel 2025 déposé à l'AMF ({d['numero']})"


rows = []
for slug, grp, q, val in L:
    ok = None
    for k, d in DEP.items():
        if d.get("slug", k.split("#")[0]) != grp:
            continue
        p = os.path.join(S, "cache_rapports", hashlib.sha256(d["report_url"].encode()).hexdigest()[:16] + ".txt")
        if os.path.exists(p) and q in re.sub(r"\s+", " ", open(p, encoding="utf-8").read()):
            ok = (k, d); break
    assert ok, (slug, q[:50])
    k, d = ok
    src = "AMF_BDIF" if "bdif.amf-france.org" in d["report_url"] else d.get("source") or "ANNUAL_REPORT"
    rows.append({"entity_slug": slug, "indicator_code": "ANI_EXPLOITATION", "source_code": src, "nature": "result", "observed_on": "2026-10-15",
                 "value_type": "category", "value_numeric": "", "value_boolean": "", "value_text": val, "normalized_value": "0", "confidence": "0.85",
                 "source_url": d["report_url"], "excerpt": f"{nom_doc(d)} : « {q} » — recours à l'exploitation animale ({val}).", "review_note": ""})
    print(slug, "←", k, src)
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "preuves écrites")
