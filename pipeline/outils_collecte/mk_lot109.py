"""Lot 109 : exploitation animale propre à des marques alimentaires et d'animalerie, d'après le
rapport de leur groupe. La phrase nomme la marque ET le produit animal ; relue à la main."""
import csv, hashlib, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
S = os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
OUT = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline\curated\groupes_2026-10_lot109_animal_marques_alimentaires.csv"
VIANDES_CRF = "Les viandes vendues en France sous les marques Filière Qualité Carrefour, Reflets de France et Carrefour Bio sont issues d’animaux abattus après un étourdissement systématique"
BEURRE = "Réduction du poids des barquettes de beurre des marques Elle & Vire, Balade et Arias"
LDC1 = "Ses marques — Loué, Le Gaulois et Maître CoQ en volaille"
BB = "Blue Buffalo’s new Nudges Salmon Grillers feature salmon as the #1 ingredient"
L = [
    ("pillsbury", "general-mills", "Pillsbury Strawberry Cream Cheese Mini Bagels", "fromage frais (mini bagels)"),
    ("progresso", "general-mills", "Progresso Rich & Hearty Chicken & Homestyle Noodles, Traditional Chicken Noodle", "poulet (soupes)"),
    ("nudges", "general-mills", BB, "saumon"),
    ("blue-buffalo", "general-mills", BB, "saumon"),
    ("edgard-cooper", "general-mills", "Edgard & Cooper creates nutritious food using only the best ingredients, including fresh meat", "viande"),
    ("reflets-de-france", "carrefour", VIANDES_CRF, "viande"),
    ("carrefour-bio", "carrefour", VIANDES_CRF, "viande"),
    ("filiere-qualite-carrefour", "carrefour", VIANDES_CRF, "viande"),
    ("carrefour-halal", "carrefour", "Pour la marque Carrefour Halal en France, un étourdissement réversible ou un soulagement des souffrances est pratiqué pour le poulet, le lapin, la dinde et le bœuf", "viande (poulet, lapin, dinde, bœuf)"),
    ("elle-et-vire", "savencia", BEURRE, "beurre"),
    ("balade", "savencia", BEURRE, "beurre"),
    ("le-gaulois", "ldc", LDC1, "volaille"),
    ("maitre-coq", "ldc", LDC1, "volaille"),
    ("loue", "ldc", "Les œufs bio de Loué sont notés A", "œufs"),
    ("reghalal", "ldc", "Reghalal et Indykpol), pour 100% de viandes d’origine locale", "viande"),
    ("indykpol", "ldc", "Reghalal et Indykpol), pour 100% de viandes d’origine locale", "viande"),
    ("kfc", "yum-brands", "KFC restaurants across the world offer fried and non-fried chicken products", "poulet"),
    ("popeyes", "rbi", "chicken under the Popeyes ® brand", "poulet"),
    ("oikos", "danone", "Oikos s’est imposé comme la référence des produits laitiers riches en protéines", "produits laitiers"),
    ("auga", "auga-group", "AUGA eggs are also supplied to consumers from the Group's organic farms", "œufs"),
    ("castello", "arla", "Our specialty cheese brand Castello ® delivered a revenue increase of 1.2%", "fromage"),
    ("lotus-biscuits", "lotus-bakeries", "We only use cage- free eggs in our Lotus ® Local Heroes", "œufs"),
    ("glofish", "spectrum-brands", "the distribution and/or sale of GloFish brand fish", "poissons vivants (animaux de compagnie)"),
]


def nom_doc(d):
    if d.get("doc"):
        return d["doc"]
    if d.get("numero"):
        return f"Document d'enregistrement universel 2025 déposé à l'AMF ({d['numero']})"
    return f"Rapport financier annuel {d['period_end'][:4]} (format ESEF)"


rows, manque = [], []
for slug, grp, q, val in L:
    ok = None
    for k, d in DEP.items():
        if d.get("slug", k.split("#")[0]) != grp:
            continue
        p = os.path.join(S, "cache_rapports", hashlib.sha256(d["report_url"].encode()).hexdigest()[:16] + ".txt")
        if os.path.exists(p) and q in re.sub(r"\s+", " ", open(p, encoding="utf-8").read()):
            ok = (k, d); break
    if not ok:
        manque.append(slug); continue
    k, d = ok
    src = d.get("source") or ("AMF_BDIF" if "bdif.amf-france.org" in d["report_url"] else "ESEF" if "filings.xbrl.org" in d["report_url"] else "ANNUAL_REPORT")
    rows.append({"entity_slug": slug, "indicator_code": "ANI_EXPLOITATION", "source_code": src, "nature": "result", "observed_on": "2026-10-15",
                 "value_type": "category", "value_numeric": "", "value_boolean": "", "value_text": val, "normalized_value": "0", "confidence": "0.85",
                 "source_url": d["report_url"], "excerpt": f"{nom_doc(d)} : « {q} » — recours à l'exploitation animale ({val}).", "review_note": ""})
    print(slug, "←", k, src)
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "preuves écrites ; introuvables :", manque)
