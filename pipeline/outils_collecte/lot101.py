"""Lot 101 : sanctions de l'Autorité de la concurrence (décisions de moins de cinq ans), relevées
dans le jeu de données officiel des décisions (data.gouv.fr, mis à jour le 11/10/2026), citées
d'après la page officielle de chaque décision ; montant attribué à la société nommée."""
import csv
import sys

sys.stdout.reconfigure(encoding="utf-8")
OUT = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline\curated\groupes_2026-10_lot101_sanctions_autorite_concurrence.csv"
COLS = ["entity_slug", "indicator_code", "source_code", "nature", "observed_on", "value_type", "value_numeric", "value_boolean",
        "value_text", "normalized_value", "confidence", "source_url", "excerpt", "review_note"]
U = "https://www.autoritedelaconcurrence.fr/fr/decision/"
rows = []


def sev(m):  # montant en euros
    return 0.9 if m >= 1e9 else 0.7 if m >= 1e8 else 0.5


def S(slug, num, date, url, montant, texte_m, motif, quotes):
    d = "/".join(reversed(date.split("-")))
    q = " ; ".join(f"« {x} »" for x in quotes)
    rows.append({**{c: "" for c in COLS}, "entity_slug": slug, "indicator_code": "GOV_SANCTIONS", "source_code": "FR_COMPETITION",
                 "nature": "controversy", "observed_on": date, "value_type": "category", "value_text": f"amende de {texte_m} ({motif})",
                 "normalized_value": sev(montant), "confidence": 0.95, "source_url": U + url,
                 "excerpt": f"Autorité de la concurrence, décision n° {num} du {d} : {q} — {motif} ; amende de {texte_m} (sévérité {str(sev(montant)).replace('.', ',')})."})


S("tereos", "21-D-25", "2021-11-02", "relative-des-pratiques-mises-en-oeuvre-dans-le-secteur-de-lapprovisionnement-en-melasse-la",
  750000, "0,75 M€", "abus de position dominante de sa filiale Tereos Océan Indien sur la mélasse de La Réunion",
  ["L’Autorité a en conséquence imposé à TOI, solidairement avec ses deux filiales, Sucrière de La Réunion et Sucrerie de Bois Rouge, une amende de 750 000 euros",
   "sanctionne Tereos Océan Indien (ci-après « TOI »), une filiale du groupe Tereos"])
S("champagne-canard-duchene", "23-D-02", "2023-03-08", "relative-des-pratiques-mises-en-oeuvre-dans-le-secteur-de-la-commercialisation-du-1",
  59000, "0,059 M€", "exclusivités d'importation du champagne Canard-Duchêne en Guyane et en Guadeloupe ; autres sanctions de 29 000, 10 000 et 19 000 euros",
  ["En conséquence, sont infligées les sanctions pécuniaires suivantes", "59 000 euros à TCD, Champagne Canard-Duchêne, C&C Export et Arvitis, en tant qu’auteures"])
S("engie", "23-D-08", "2023-09-07", "relative-des-pratiques-mises-en-oeuvre-dans-le-secteur-des-prestations-de-services",
  10800000, "10,8 M€", "entente sur des marchés de services pour des sites nucléaires, via sa filiale Endel ; s'y ajoutent 256 000 euros",
  ["L’Autorité a en revanche imposé aux autres entreprises les sanctions pécuniaires suivantes, ainsi qu’une injonction de publication : Grief n° 1 (euros) / Griefs n° 2 à 10 (euros)",
   "ENDEL (solidairement à ENGIE) 10 800 000 / 256 000"])
S("sony", "23-D-14", "2023-12-20", "relative-des-pratiques-mises-en-oeuvre-dans-les-secteurs-des-consoles-statiques-de-jeux",
  13527000, "13,527 M€", "abus de position dominante sur les manettes de la PlayStation 4",
  ["sanctionne quatre sociétés du groupe Sony pour avoir abusé de leur position dominante sur le marché de la fourniture de manettes de jeux vidéo pour consoles PlayStation 4",
   "Ces sociétés se voient infliger une sanction pécuniaire de 13 527 000 euros au titre de la présente décision"])
BPA = "relative-des-pratiques-dans-le-secteur-de-la-fabrication-et-la-vente-de-denrees"
for slug, nom, m, t in [("bonduelle", "Bonduelle", 2884000, "2,884 M€"), ("cofigeo", "Cofigeo", 566000, "0,566 M€"),
                        ("conserves-france", "Conserves France", 130000, "0,13 M€"), ("general-mills", "General Mills", 298000, "0,298 M€"),
                        ("andros", "Andros", 1000, "0,001 M€"), ("unilever", "Unilever", 1381000, "1,381 M€")]:
    S(slug, "23-D-15", "2023-12-29", BPA, m, t, "entente pour taire la présence de bisphénol A dans les emballages alimentaires",
      [f"l’Autorité a infligé les sanctions pécuniaires suivantes", f"{nom} : {m:,} euros".replace(",", " ")])
for slug in ("savencia", "de-neuville"):
    S(slug, "24-D-02", "2024-02-06", "relative-des-pratiques-mises-en-oeuvre-dans-le-secteur-de-la-distribution-de-chocolats",
      2312000, "2,312 M€", "restrictions imposées aux franchisés De Neuville ; s'y ajoutent 1 756 000 euros pour un second grief",
      ["l’Autorité a infligé conjointement et solidairement une sanction de 2 312 000 euros au titre du premier grief, et une sanction de 1 756 000 euros au titre du second grief, à la société De Neuville ainsi qu’à sa société mère, Savencia Holding"])
S("google", "24-D-03", "2024-03-15", "relative-au-respect-des-engagements-figurant-dans-la-decision-de-lautorite-de-la-0",
  250000000, "250 M€", "non-respect de ses engagements sur la rémunération des éditeurs de presse (droits voisins)",
  ["a estimé qu’il y avait lieu de prononcer une sanction à l’encontre de Google d’un montant compris dans la fourchette figurant dans le procès-verbal de transaction, de 250 millions d’euros"])
ELM = "relative-des-pratiques-mises-en-oeuvre-dans-le-secteur-de-la-fabrication-et-de-la-1"
S("seb", "24-D-11", "2024-12-19", ELM, 189500000, "189,5 M€", "ententes sur les prix de revente dans l'électroménager",
  ["l’Autorité a prononcé au titre de ces douze griefs des sanctions pécuniaires d’un montant total de 611 000 000 d’euros", "SEB : 189 500 000 euros"])
S("electrolux", "24-D-11", "2024-12-19", ELM, 44500000, "44,5 M€", "ententes sur les prix de revente dans l'électroménager",
  ["l’Autorité a prononcé au titre de ces douze griefs des sanctions pécuniaires d’un montant total de 611 000 000 d’euros", "Electrolux : 44 500 000 euros"])
BIO = "relative-des-pratiques-mises-en-oeuvre-dans-le-secteur-de-la-distribution-des-produits-7"
S("carrefour", "26-D-05", "2026-04-16", BIO, 1850000, "1,85 M€", "entente de répartition des marques de produits bio, via sa filiale Greenweez",
  ["Elle a ainsi sanctionné le Synadis Bio et les entreprises suivantes à hauteur de", "−1,85 million d’euros pour Greenweez (solidairement avec sa société mère Carrefour SA)"])
S("mousquetaires", "26-D-05", "2026-04-16", BIO, 740000, "0,74 M€", "entente de répartition des marques de produits bio, via ITM Entreprises",
  ["Elle a ainsi sanctionné le Synadis Bio et les entreprises suivantes à hauteur de", "−740 000 euros pour ITM Entreprises (solidairement avec sa société mère Les Mousquetaires)"])

with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(rows)
print(len(rows), "sanctions")
