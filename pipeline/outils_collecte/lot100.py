"""Lot 100 : rapports réglementés (ESEF) des groupes cotés — tous les piliers.
Chaque preuve : citation(s) exacte(s) du rapport, cadre, calcul écrit en toutes lettres.
Les absences lues (« non matériel », publié autrement) vont au journal de relecture."""
import csv, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
S = os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
OUT = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline\curated\groupes_2026-10_lot100_rapports_esef.csv"
JOURNAL = os.path.join(S, "lot100_journal.json")
COLS = ["entity_slug", "indicator_code", "source_code", "nature", "observed_on", "value_type", "value_numeric", "value_boolean",
        "value_text", "normalized_value", "confidence", "source_url", "excerpt", "review_note"]
FX = {"USD": 1.13, "GBP": 0.8568, "DKK": 7.4634, "SEK": 11.0663, "CHF": 0.937, "PLN": 4.2397}
rows, journal = [], []


def fr(x: float, d: int = 2) -> str:
    s = f"{abs(x):.{d}f}".replace(".", ",")
    return ("−" if x < 0 else "+" if x > 0 else "") + s


def num(x: float) -> str:
    return str(int(x)) if float(x) == int(x) else str(x).replace(".", ",")


def cadre_doc(slug: str) -> str:
    if DEP[slug].get("doc"):
        return DEP[slug]["doc"]
    if DEP[slug].get("source") == "AMF_BDIF":
        return f"Document d'enregistrement universel {DEP[slug]['period_end'][:4]} déposé à l'AMF ({DEP[slug]['numero']})"
    return "Rapport financier annuel 2025 (ESEF)" if DEP[slug]["period_end"].startswith("2025-12") else \
        f"Rapport annuel de l'exercice clos le {'/'.join(reversed(DEP[slug]['period_end'].split('-')))} (ESEF)"


def P(slug, code, quotes, cadre, value=None, vtype="numeric", text="", boolean="", norm="", calc=""):
    if (slug, code) in DEJA:
        return
    q = " ; ".join(f"« {x} »" for x in quotes)
    rows.append({**{c: "" for c in COLS}, "entity_slug": slug, "indicator_code": code, "source_code": DEP[slug].get("source", "ESEF"), "nature": "result",
                 "observed_on": DEP[slug]["date_added"][:10], "value_type": vtype,
                 "value_numeric": "" if value is None else value, "value_boolean": boolean, "value_text": text,
                 "normalized_value": norm, "confidence": 0.9, "source_url": DEP[slug]["report_url"],
                 "excerpt": f"{cadre_doc(slug)}, {cadre} : {q}" + (f" ; {calc}" if calc else "")})


def trend(slug, code, quotes, cadre, y0, y1, last, base, ghg=True):
    n = y1 - y0
    r = ((last / base) ** (1 / n) - 1) * 100
    r = round(r, 2)
    norm = round(max(0.0, min(1.0, -r / 4.2)), 4) if ghg else ""
    calc = f"rythme annuel moyen ({y0} → {y1}, {n} an{'s' if n > 1 else ''}) : ({num(last)} / {num(base)})^(1/{n}) − 1 = {fr(r).lstrip('+')} %"
    P(slug, code, quotes, cadre, value=r, norm=norm, calc=calc)


def trend_pct(slug, code, quotes, cadre, y0, y1, pct, ghg=False, dec=None):
    """Variation publiée depuis l'année de référence (pct < 0 = baisse) ; dec : décimales publiées."""
    n = y1 - y0
    r = round(((1 + pct / 100) ** (1 / n) - 1) * 100, 2)
    sign = "−" if pct < 0 else "+"
    d = dec if dec is not None else (0 if pct == int(pct) else 1)
    calc = f"rythme annuel moyen ({y0} → {y1}, {n} an{'s' if n > 1 else ''}) : (1 {sign} {fr(abs(pct), d).lstrip('+')} %)^(1/{n}) − 1 = {fr(r).lstrip('+')} %"
    P(slug, code, quotes, cadre, value=r, norm=(round(max(0.0, min(1.0, -r / 4.2)), 4) if ghg else ""), calc=calc)


def fx(slug, code, quotes, cadre, a, cur, unit_out, year="2025", d=1):
    rate = FX[cur]
    c = round(a * rate, d)
    calc = f"taux de change annuel moyen {year} de la BCE (1 € = {str(rate).replace('.', ',')} {cur}) : {str(a).replace('.', ',')} × {str(rate).replace('.', ',')} = {str(c).replace('.', ',')}"
    P(slug, code, quotes, f"{cadre} (converti en {unit_out})", value=c, calc=calc)


# (slug, code) déjà documentés en base avant ce lot : non régénérés (doublons écartés le 15/10/2026)
DEJA = set([('henkel', 'ENV_GHG_TREND'), ('lactalis', 'SUP_VIGILANCE_PLAN'), ('mars', 'ENV_GHG_TREND'), ('nestle', 'ENV_GHG_TREND'), ('nestle', 'PLA_REDUCTION'), ('savencia', 'ENV_GHG_INTENSITY'), ('savencia', 'ENV_GHG_TREND'), ('savencia', 'GOV_BOARD_INDEP'), ('mondelez', 'ENV_GHG_TREND'), ('mondelez', 'PLA_REDUCTION')])


def J(slug, code, outcome, detail):
    journal.append({"slug": slug, "code": code, "outcome": outcome, "detail": detail, "source_url": DEP[slug]["report_url"]})


VIG = "plan de vigilance (C. com. L225-102-4) : analyse des risques, mesures, alerte et suivi"

# ---------------------------------------------------------------- Michelin
s = "michelin"
P(s, "GOV_BOARD_GENDER", ["Pourcentage de femmes membres au sein du Conseil de Surveillance (1) 45,5 % 45,5 %"],
  "état de durabilité, ESRS 2 GOV-1 (diversité du conseil de surveillance ; colonnes 2025, 2024)", value=45.5)
P(s, "GOV_BOARD_INDEP", ["Stabilité du taux d’indépendance à 89 % (hors membres représentant les salariés)"],
  "gouvernement d'entreprise (indépendance du conseil de surveillance)", value=89, norm=0.89)
trend(s, "ENV_GHG_TREND", ["Année de référence 2019 (tCO 2 e) 2023 (tCO 2 e) 2024 (tCO 2 e) 2025 (tCO 2 e)",
                           "Total des émissions de GES basé sur le marché (scopes 1 + 2+ 3 essentiel (1) ) (E1‑6‑52b) 18 468 387 15 939 151 14 750 899 13 782 821",
                           "Émissions de GES brutes du scope 3 usage (2) 131 000 000 125 000 000"],
      "état de durabilité, ESRS E1-6, émissions totales de GES publiées, scopes 1, 2 et 3 « essentiel » (fondées sur le marché, tCO2e ; "
      "colonnes 2019 (référence), 2023, 2024, 2025) ; ce total exclut le scope 3 « usage » (émissions liées à l'utilisation des pneus vendus), "
      "publié à part pour 2024 et 2025 seulement (131 puis 125 millions de tCO2e, environ neuf fois le total publié)",
      2019, 2025, 13782821, 18468387)
P(s, "ENV_GHG_INTENSITY", ["Intensité des GES basée sur le chiffre d’affaires 2023 2024 2025",
                           "Intensité des GES (basée sur le marché) (E1‑6‑53) 562 tCO 2 e/M€ 542 tCO 2 e/M€ 530 tCO 2 e/M€"],
  "état de durabilité, ESRS E1-6 (intensité de GES par chiffre d'affaires, fondée sur le marché ; colonnes 2023, 2024, 2025)", value=530)
P(s, "ENV_SCOPE3_DISCLOSED", ["Émissions de GES brutes du scope 3 essentiel (1) 15 029 349 13 617 627 12 724 408 12 096 228"],
  "état de durabilité, ESRS E1-6 (émissions de scope 3 ; colonnes 2019, 2023, 2024, 2025)", vtype="boolean", boolean="true", norm=1)
P(s, "SUP_VIGILANCE_PLAN", ["Comme chaque année depuis 2017, Michelin répond aux exigences de la loi n o 2017‑399 du 27 mars 2017 sur le devoir de vigilance par la rédaction d’un Plan de vigilance",
                            "Il identifie les risques du Groupe et de sa chaîne de valeur et détaille les mesures mises en place pour prévenir et atténuer les atteintes graves à l’environnement, à la santé/sécurité et aux droits humains",
                            "Plan de Vigilance et compte rendu de sa mise en œuvre effective Article L. 225‑102‑4 du Code de commerce"],
  VIG, vtype="category", text="complet", norm=1)
P(s, "WAT_INTENSITY", ["Consommation d’eau 2024 (1) 2025 (2)",
                       "(c) Intensité hydrique basé sur le chiffre d’affaires (E3‑4‑29) 350 m 3 /M€ 320 m 3 /M€"],
  "état de durabilité, ESRS E3-4 (intensité hydrique réglementaire : consommation d'eau rapportée au chiffre d'affaires ; colonnes 2024, 2025)", value=320)
P(s, "LAB_LIVING_WAGE", ["Conformément à l’indicateur tel que défini dans S1‑10‑69 des ESRS, 100 % des salariés du Groupe perçoivent un salaire décent",
                         "Depuis 2023, le Groupe engage un travail plus ambitieux en obtenant la certification Fair Wage Network"],
  "état de durabilité, ESRS S1-10 (salaire décent ; certification par un organisme tiers)", vtype="category", text="verified", norm=1)
J(s, "ENV_TAXONOMY_CAPEX", "non_trouvee", "Rapport financier annuel 2025 lu (ESEF) : aucun CapEx aligné sur la taxonomie — tableau réglementaire, ligne « CapEx des activités durables sur le plan environnemental (alignées sur la taxonomie) (A.1) - - - » ; CapEx éligibles : 61 %.")
for code, nom in (("LAB_GENDER_PAYGAP", "Écart de rémunération entre hommes et femmes non corrigé"),
                  ("LAB_CEO_PAY_RATIO", "Ratio de rémunération excessif du Directeur Général")):
    J(s, code, "absence_confirmee", f"Rapport financier annuel 2025 lu (ESEF) : la table des points de données ESRS indique « ESRS S1‑16 {nom} » … « Non matériel » ; la donnée n'est pas publiée.")

# ---------------------------------------------------------------- Carlsberg
s = "carlsberg"
trend(s, "ENV_GHG_TREND", ["GHG emissions (kt CO 2 e) E1-6 2025 2024 Δ",
                           "Total GHG emissions (market-based) 9,041 8,278 ⁱ 8 %"],
      "sustainability statement, ESRS E1-6, émissions totales de GES, scopes 1, 2 et 3 (fondées sur le marché, kt CO2e ; colonnes 2025, 2024 retraitée) ; "
      "une seule année publiée en comparaison", 2024, 2025, 9041, 8278)
trend_pct(s, "PLA_REDUCTION", ["88 kt of virgin fossil-based plastic in our primary packaging materials. Excluding acquisitions, this figure was 56 kt, representing a 4% decline in the use of virgin plastic since 2024 and a 7% decline since our baseline of 2019"],
          "sustainability statement, ESRS E5 (plastique fossile vierge des emballages primaires, hors acquisitions ; y compris acquisitions : 88 kt en 2025)",
          2019, 2025, -7)
P(s, "PLA_RECYCLED", ["Rate of recyclable, reusable or renewable packaging 2025 2025* 2024* 2024* Δ* PET 84 73 68 68 5 %p Aluminium 100 100 100 100 0 %p Glass 100 100 100 100 0 %p Total 95 95 94 94 1 %p"],
  "sustainability statement, ESRS E5 (part d'emballages recyclables, réutilisables ou renouvelables ; première colonne : 2025)", value=95)
fx(s, "WAT_INTENSITY", ["E3-4 Unit 2025 2024 Total water consumption million m³ 14 12",
                        "Water intensity ratio m³ per DKK million 152 162"],
   "sustainability statement, ESRS E3-4 (intensité hydrique réglementaire : consommation d'eau rapportée au chiffre d'affaires, 152 m³ par million de couronnes danoises en 2025)",
   152, "DKK", "m³/M€")
J(s, "LAB_LIVING_WAGE", "autre_forme", "Rapport annuel 2025 lu (ESEF) : « we are paying all employees at or above the minimum wage or living wage, depending on the aforementioned data availability » — le salaire minimum national sert de référence là où il existe ; ce n'est pas un engagement de salaire décent.")
J(s, "LAB_CEO_PAY_RATIO", "autre_forme", "Rapport annuel 2025 lu (ESEF) : « CEO pay ratio (disclosed in the Remuneration Report) » — publié dans le rapport de rémunération, document distinct.")

# ---------------------------------------------------------------- Campari
s = "campari"
trend(s, "ENV_GHG_TREND", ["Total GHG emissions UoM Retrospective 2025 2024 (1) Base Year (2019) % change 2025 vs. 2024",
                           "Total market-based GHG emissions tCO2eq 1,005,470 988,782 957,944 1.7 %"],
      "sustainability statement, ESRS E1-6, émissions totales de GES, scopes 1, 2 et 3 (fondées sur le marché, tCO2eq ; colonnes 2025, 2024, 2019 (référence))",
      2019, 2025, 1005470, 957944)
P(s, "ENV_TAXONOMY_CAPEX", ["CapEx of environmentally sustainable activities (Taxonomy-aligned) (A.1) 22.05 6.93%"],
  "taxonomie verte de l'UE (règlement 2020/852, art. 8), tableau réglementaire des CapEx (montant aligné en M€, part alignée)", value=6.93, text="6,93 %", norm=0.0693)
J(s, "GOV_BOARD_GENDER", "autre_forme", "Rapport annuel 2025 lu (ESEF) : part de femmes publiée par catégorie seulement — « Executive Directors … 0% » et « Non-Executive Directors … 36.4% » — sans pourcentage pour le conseil entier.")

# ---------------------------------------------------------------- Arla
s = "arla"
P(s, "LAB_CEO_PAY_RATIO", ["Total remuneration ratio 69"],
  "sustainability statement, ESRS S1-16 (ratio de rémunération annuelle totale : la personne la mieux payée rapportée à la médiane des salariés)", value=69)

# ---------------------------------------------------------------- BIC
s = "bic"
P(s, "ENV_TAXONOMY_CAPEX", ["l’analyse des critères DNSH ( Do Not Significantly Harm ) et garanties minimales a conduit à un CapEx aligné de 2,1 millions d'euros, soit 1,8 % du total des dépenses d’investissement, contre 2,5 % du CapEx total en 2024",
                            "Proportion du chiffre d’affaires, CapEx, OpEx des produits ou services associés aux activités économiques éligibles à la taxonomie ou alignées sur la"],
  "taxonomie verte de l'UE (règlement 2020/852, art. 8), CapEx alignés", value=1.8, text="1,8 %", norm=0.018)
P(s, "SUP_VIGILANCE_PLAN", ["3.2. Plan de Vigilance 3.2.1 Introduction 3.2.2 Gouvernance 3.2.3 Méthodologie 3.2.4 Cartographies des risques liées aux thématiques du devoir de vigilance 3.2.5 Atténuation et remédiation 3.2.6 Suivi du Plan de Vigilance"],
  VIG, vtype="category", text="complet", norm=1)
P(s, "LAB_LIVING_WAGE", ["BIC met tout en œuvre pour que tous ses salariés perçoivent un salaire décent, au moins égal aux seuils locaux de minimum vital (S1-5)"],
  "état de durabilité, ESRS S1-10 (salaire décent : engagement, sans vérification par un tiers)", vtype="category", text="policy", norm=0.5)


# ---------------------------------------------------------------- AB InBev
s = "ab-inbev"
P(s, "PLA_RECYCLED", ["In 2025, 89.7% of the company’s products were in returnable packaging or made from majority recycled content (more than 50%)"],
  "sustainability statements, ESRS E5 (part des produits en emballage consigné ou majoritairement recyclé)", value=89.7)
P(s, "ENV_TAXONOMY_CAPEX", ["Taxonomy-aligned Capex and Opex ratios are by year-end 2025 approximately 0.4%"],
  "taxonomie verte de l'UE (règlement 2020/852, art. 8), CapEx alignés", value=0.4, text="0,4 %", norm=0.004)
J(s, "ENV_GHG_TREND", "non_trouvee", "Rapport annuel 2025 lu (ESEF) : une seule année de comparaison publiée — « Total GHG emissions (market-based) (in million metric tonnes of CO2 eq) 22.14 23.62 -6.3% » (2025, 2024) ; une baisse sur un an ne dit pas une trajectoire, aucun rythme n'est calculé.")
J(s, "WAT_INTENSITY", "autre_forme", "Rapport annuel 2025 lu (ESEF) : intensité publiée en dollars — « Water intensity across all operations (thousand m3/million USD) 1.15 1.15 » (2025, 2024), soit 1 150 m³ par million de dollars de chiffre d'affaires.")
J(s, "LAB_LIVING_WAGE", "autre_forme", "Rapport annuel 2025 lu (ESEF) : « the company conducted an adequate wage review and concluded that all employees were being paid adequate wages, as defined by country benchmarks » ; note 33 : « For countries with no established adequate/living wages, the company used minimum wages as benchmarks » — le salaire minimum sert de référence là où il n'existe pas de référence de salaire décent.")
J(s, "LAB_CEO_PAY_RATIO", "autre_forme", "Rapport annuel 2025 lu (ESEF) : « For 2025, the ratio between the remuneration of the highest paid member of the ExCom and the lowest paid employee of the company (Anheuser-Busch InBev SA/NV) was 1,790.6 to one » — rapport au salarié le moins payé de la société belge, et non à la rémunération médiane du groupe (ESRS S1-16).")

# ---------------------------------------------------------------- Auga group
s = "auga-group"
P(s, "GOV_BOARD_GENDER", ["the share of women on the Board has decreased to 0%"],
  "rapport de gestion consolidé (composition du conseil après la restructuration)", value=0, norm=0)
P(s, "ENV_SCOPE3_DISCLOSED", ["Scope 3 emissions are higher, totaling 2,878 t CO 2e, or 189% higher compared to 2024"],
  "sustainability statement, ESRS E1-6 (émissions de scope 3)", vtype="boolean", boolean="true", norm=1)
J(s, "LAB_GENDER_PAYGAP", "autre_forme", "Rapport annuel 2025 lu (ESEF) : écart publié sur les salaires médians, non sur les rémunérations moyennes (ESRS S1-16) — « Ratio of men‘s and women‘s median salaries 2025 2024 2023 Total: 1.18 1.13 1.09 » (salaire médian des hommes 1,18 fois celui des femmes).")
J(s, "ENV_GHG_TREND", "non_trouvee", "Rapport annuel 2025 lu (ESEF) : évolution publiée sur un an seulement — « In 2025, the Group’s total operational carbon footprint decreased by 99,978 t CO2e, or 54% compared to 2024 » (empreinte « opérationnelle »).")

# ---------------------------------------------------------------- AXA
s = "axa"
P(s, "LAB_LIVING_WAGE", ["AXA vise à rémunérer ses employés à un niveau égal ou supérieur au salaire décent"],
  "état de durabilité, ESRS S1-10 (salaire décent : engagement, sans vérification par un tiers)", vtype="category", text="policy", norm=0.5)

# ---------------------------------------------------------------- BNP Paribas
s = "bnp-paribas"
P(s, "LAB_LIVING_WAGE", ["Conformément au nouvel engagement pris dans l’Accord Monde de novembre 2024, 100 % des salariés du Groupe perçoivent un salaire dit décent"],
  "état de durabilité, ESRS S1-10 (salaire décent, données de référence Fair Wage Network ; sans certification par un tiers)", vtype="category", text="policy", norm=0.5)
J(s, "ENV_GHG_TREND", "non_trouvee", "Rapport financier annuel 2025 lu (ESEF) : une seule année de comparaison pour le total — « Émissions totales de GES ( market-based ) (tCO 2 e) 94 588 364 104 347 619 (9,4) % » (2025, 2024) ; une baisse sur un an ne dit pas une trajectoire.")

# ---------------------------------------------------------------- BPCE
s = "bpce"
J(s, "LAB_LIVING_WAGE", "autre_forme", "Rapport financier annuel 2025 lu (ESEF) : « Tous les collaborateurs du groupe perçoivent un salaire décent conformément aux indices de référence applicables. Le salaire décent se réfère aux salaires minimums sociaux fixés par la législation ou par les négociations collectives » — la référence est le salaire minimum, pas un salaire décent calculé.")
J(s, "ENV_GHG_TREND", "non_trouvee", "Rapport financier annuel 2025 lu (ESEF) : deux tableaux d'émissions totales aux périmètres différents (« 138 244 392 148 315 966 7% » puis « 83 427 446 91 194 711 9% », en hausse), colonnes non datées dans la ligne ; aucun rythme n'est calculé.")

# ---------------------------------------------------------------- Banques et assureurs : taxonomie
for s in ("axa", "bnp-paribas", "bpce", "credit-agricole", "credit-mutuel-arkea", "la-banque-postale", "societe-generale"):
    J(s, "ENV_TAXONOMY_CAPEX", "autre_forme", "Rapport financier annuel 2025 lu (ESEF) : établissement financier — l'alignement sur la taxonomie verte se publie par le ratio d'actifs verts (GAR) et les indicateurs d'investissement ou de souscription, non par la part des CapEx.")

# ---------------------------------------------------------------- Crédit Agricole
s = "credit-agricole"
J(s, "LAB_LIVING_WAGE", "autre_forme", "Rapport financier annuel 2025 lu (ESEF) : « Le Groupe applique les préconisations de la norme pour calculer le salaire décent en s’appuyant sur les salaires minimums des pays quand ils existent et sur les benchmarks proposés par Fair Wage Network » — le salaire minimum sert de référence là où il existe.")
J(s, "ENV_GHG_TREND", "non_trouvee", "Rapport financier annuel 2025 lu (ESEF) : émissions totales publiées sur deux années seulement (« Émissions totales de GES (fondées sur le marché) (teqCO 2 ) 164 180 320 165 638 612 ») ; aucun rythme pluriannuel n'est calculable.")

# ---------------------------------------------------------------- Crédit Mutuel Arkéa
s = "credit-mutuel-arkea"
J(s, "ENV_GHG_TREND", "non_trouvee", "Rapport financier annuel 2025 lu (ESEF) : total publié hors investissements (poste 15) — « Émissions totales de GES – basées sur le marché hors investissements (poste 15) 35 072 44 641 38 047 » — sans les émissions financées ; aucun rythme n'est calculé.")

# ---------------------------------------------------------------- Diageo (exercice clos le 30/06/2026)
s = "diageo"
P(s, "PLA_RECYCLED", ["Continue our work to increase recycled content in our total packaging (increasing the percentage of recycled content in our packaging to 50%) 50% 2026 cumulative progress 47% 2025 cumulative progress 46%"],
  "strategic report (contenu recyclé dans l'ensemble des emballages, exercice 2026)", value=47)
P(s, "LAB_CEO_PAY_RATIO", ["Year Method 25 th percentile pay ratio Median pay ratio 75 th percentile pay ratio 2026 (1) Option A (4) 59:1 43:1 35:1"],
  "directors' remuneration report (ratio de rémunération du directeur général à la rémunération médiane des salariés du Royaume-Uni, méthode réglementaire britannique « Option A » ; périmètre : Royaume-Uni)", value=43)
P(s, "ENV_SCOPE3_DISCLOSED", ["Reduce our value chain (Scope 3) greenhouse gas emissions by 26% (26)% 2026 cumulative progress (18.8) %"],
  "strategic report (émissions de la chaîne de valeur, scope 3 : évolution publiée depuis l'exercice 2022)", vtype="boolean", boolean="true", norm=1)
P(s, "LAB_LIVING_WAGE", ["Conducting global pay equity and living wage analyses for Diageo employees and taking action to close gaps if identified"],
  "strategic report (salaire décent : analyse et engagement, sans vérification par un tiers)", vtype="category", text="policy", norm=0.5)
J(s, "ENV_GHG_TREND", "autre_forme", "Rapport annuel 2026 lu (ESEF) : évolutions publiées séparément pour les opérations directes (scopes 1 et 2) et la chaîne de valeur (scope 3, « 2026 cumulative progress (18.8) % » depuis l'exercice 2022), sans total des scopes 1, 2 et 3.")


def unite(slug, code, quotes, cadre, a, c):
    """Intensité publiée en milliers de m³ par M€ : conversion écrite en toutes lettres."""
    P(slug, code, quotes, cadre, value=c,
      calc=f"conversion : {str(a).replace('.', ',')} milliers de m³/M€ × 1 000 = " + f"{c:,.0f}".replace(",", " ") + " m³/M€")


# ---------------------------------------------------------------- ENGIE
s = "engie"
P(s, "WAT_INTENSITY", ["Résultats 2024 Résultats 2025 Unité Consommation d’eau totale 59 832 379 45 890 955 m 3",
                       "Ratio intensité eau - chiffre d’affaires 810,6 637,9 m 3 /millions €"],
  "état de durabilité, ESRS E3-4 (intensité hydrique réglementaire : consommation d'eau rapportée au chiffre d'affaires ; colonnes 2024, 2025)", value=637.9)
J(s, "LAB_LIVING_WAGE", "autre_forme", "Rapport financier annuel 2025 lu (ESEF) : « Les salariés d’ENGIE perçoivent un salaire décent dans les pays disposant d’indices de référence. ENGIE se réfère aux données de salaires minimums légaux ou salaires minimums locaux établis par les accords » — la référence est le salaire minimum, pas un salaire décent calculé.")

# ---------------------------------------------------------------- Haleon
s = "haleon"
P(s, "LAB_CEO_PAY_RATIO", ["Year Method 4 25th percentile pay ratio Median pay ratio 75th percentile pay ratio 2025 Option B 131:1 76:1 52:1"],
  "directors' remuneration report (ratio de rémunération du directeur général à la rémunération médiane des salariés du Royaume-Uni, méthode réglementaire britannique « Option B » ; périmètre : Royaume-Uni)", value=76)
P(s, "ENV_SCOPE3_DISCLOSED", ["Total Scope 3 carbon emissions (thousands of tonnes CO 2 e) 2,463 2,533"],
  "rapport annuel (émissions de scope 3, en milliers de tCO2e)", vtype="boolean", boolean="true", norm=1)
trend_pct(s, "PLA_REDUCTION", ["We aim to reduce our use of virgin petroleum-based plastic by 10% by 2025, and a third by 2030 vs a 2022 baseline 2,5 . (9)% * (1)%"],
          "rapport annuel (plastique vierge d'origine pétrolière, période de mesure close fin juin 2025, par rapport à 2022 ; colonnes 2025, 2024)",
          2022, 2025, -9)

# ---------------------------------------------------------------- Heineken
s = "heineken"
P(s, "PLA_RECYCLED", ["In 2025, we reached 48% (2024: 44% ) recycled content in our bottles and cans"],
  "sustainability statement, ESRS E5 (contenu recyclé des bouteilles et canettes)", value=48)
P(s, "ENV_GHG_INTENSITY", ["GHG intensity as a factor of net revenue", "2025 2024 Scope 1 GHG emissions from regulated ETS (%) 19% 22% Total GHG emissions per net revenue (tCO 2 eq/mEUR) 1 Market-based 519 533"],
  "sustainability statement, ESRS E1-6 (intensité de GES par chiffre d'affaires net, fondée sur le marché ; colonnes 2025, 2024)", value=519)
unite(s, "WAT_INTENSITY", ["In 2025, water intensity as a factor of revenue (total water consumption per net revenue) was 1.12 thousand m3 / mEUR"],
      "sustainability statement, ESRS E3-4 (intensité hydrique réglementaire : consommation d'eau rapportée au chiffre d'affaires)", 1.12, 1120)

# ---------------------------------------------------------------- Interparfums
s = "interparfums"
P(s, "WAT_INTENSITY", ["2023 2024 2025 Consommation totale d'eau en m 3 1 301 1 014 2 830 Intensité hydrique en m 3 /M€ de CA 1,629 1,152 3,147"],
  "état de durabilité, ESRS E3-4 (intensité hydrique : consommation d'eau rapportée au chiffre d'affaires ; colonnes 2023, 2024, 2025)", value=3.147)
P(s, "LAB_LIVING_WAGE", ["Part des collaborateurs rémunérés au dessus du salaire décent 100 % 100 % 100 %"],
  "état de durabilité, ESRS S1-10 (part des salariés payés au-dessus du salaire décent, mesure interne sans vérification par un tiers)", vtype="category", text="policy", norm=0.5)
J(s, "GOV_BOARD_GENDER", "autre_forme", "Rapport financier annuel 2025 lu (ESEF) : deux valeurs discordantes — tableau des indicateurs « Part des femmes au conseil d'administration 50 % 55 % 50 % » et texte « en 2024, la proportion de femmes était de 42% de femmes contre 46% en 2025 » ; aucune n'est retenue.")

# ---------------------------------------------------------------- La Banque Postale
s = "la-banque-postale"
J(s, "ENV_GHG_TREND", "non_trouvee", "Rapport financier annuel 2025 lu (ESEF) : une seule année de comparaison (2024 publiée, 2024 retraitée, 2025) — « Total des émissions de GES – basé sur le marché 62 964 867 146 387 815 179 776 821 » ; la hausse vient des émissions financées du périmètre assurantiel, retraitées ; aucun rythme n'est calculé.")
J(s, "LAB_LIVING_WAGE", "autre_forme", "Rapport financier annuel 2025 lu (ESEF) : « Tous les salariés perçoivent un salaire décent (105) , conformément aux normes en vigueur, qu’il s’agisse de la législation, des conventions collectives ou des accords d’entreprise applicables » — la référence est le salaire légal ou conventionnel, pas un salaire décent calculé.")

# ---------------------------------------------------------------- Laurent-Perrier (exercice clos le 31/03/2026)
s = "laurent-perrier"
P(s, "LAB_CEO_PAY_RATIO", ["F’22 F’23 F’24 F’25 F’26",
                           "Président du Directoire Evolution de la rémunération vs N-1 0% 9,58% 9,41% 6,64% 0,40% Ratio avec rémunération* moyenne 9,82 10,36 11,09 11,40 11,35 Evolution N vs N-1 -5,39% 5,50% 7,05% 2,80% -0,44% Ratio avec rémunération* médiane 13,20 13,67 14,31 14,60 14,48"],
  "rapport sur le gouvernement d'entreprise, ratios d'équité (C. com. L.22-10-9) : rémunération du président du directoire rapportée à la rémunération médiane des salariés (dernière colonne : exercice 2025-2026)", value=14.48)

# ---------------------------------------------------------------- L'Oréal
s = "loreal"
P(s, "WAT_INTENSITY", ["En m 3 /millions d'euros 2024 2025 Intensité hydrique : consommation totale d’eau pour des activités propres par revenu net (1) 22 22"],
  "état de durabilité, ESRS E3-4 (intensité hydrique réglementaire : consommation d'eau rapportée au chiffre d'affaires ; colonnes 2024, 2025)", value=22)
P(s, "LAB_LIVING_WAGE", ["Pour l’année 2025 et pour la troisième année consécutive, L’Oréal est certifié Living Wage Employer au niveau mondial par l’ONG Fair Wage Network"],
  "état de durabilité, ESRS S1-10 (salaire décent ; certification par un organisme tiers)", vtype="category", text="verified", norm=1)

# ---------------------------------------------------------------- The Magnum Ice Cream Company
s = "magnum-ice-cream-company"
P(s, "WAT_INTENSITY", ["Water intensity ratio: water consumption per turnover (m 3 /€ million) 384"],
  "sustainability statements, ESRS E3-4 (intensité hydrique réglementaire : consommation d'eau rapportée au chiffre d'affaires, 2025)", value=384)
P(s, "LAB_LIVING_WAGE", ["we aim to provide at least a living wage in every market where we operate, supporting a good standard of living for all our people and their families"],
  "rapport de gestion (salaire décent : engagement, sans vérification par un tiers)", vtype="category", text="policy", norm=0.5)
for code, nom in (("LAB_GENDER_PAYGAP", "Unadjusted gender pay gap"), ("LAB_CEO_PAY_RATIO", "Excessive CEO pay ratio")):
    J(s, code, "absence_confirmee", f"Rapport annuel 2025 lu (ESEF) : la table des points de données ESRS indique « ESRS S1-16 … {nom} Not material » ; la donnée n'est pas publiée.")
J(s, "ENV_GHG_TREND", "non_trouvee", "Rapport annuel 2025 lu (ESEF) : premier exercice de la société séparée d'Unilever ; émissions publiées pour 2025 seulement, aucune évolution calculable.")

# ---------------------------------------------------------------- Marie Brizard Wine & Spirits
s = "marie-brizard"
J(s, "ENV_GHG_TREND", "non_trouvee", "Rapport financier annuel 2025 lu (ESEF) : une seule année de comparaison — « Émissions totales de GES (fondées sur le marché) (teqCO2) 152 675 175 648 -16% » (2025, 2024) ; une baisse sur un an ne dit pas une trajectoire.")
J(s, "LAB_LIVING_WAGE", "non_trouvee", "Rapport financier annuel 2025 lu (ESEF) : « Salaires décents [S1-10] Conformément à l’application des dispositions d’entrée en vigueur progressive, le reporting sur les enjeux du pilier S1 est reporté à l’année prochaine » — publication reportée, comme la loi l'autorise.")

# ---------------------------------------------------------------- Pernod Ricard (exercice clos le 30/06/2025)
s = "pernod-ricard"
P(s, "ENV_TAXONOMY_CAPEX", ["les OpEx au titre de la Taxonomie sont considérées comme non significatives, l’évaluation de l’alignement portait uniquement sur les CapEx éligibles",
                            "Pour l’exercice 2024/25, les CapEx alignées représentent 4,1 % (soit 32,6 millions d’euros) du total des CapEx"],
  "taxonomie verte de l'UE (règlement 2020/852, art. 8), CapEx alignés", value=4.1, text="4,1 %", norm=0.041)
trend_pct(s, "PLA_REDUCTION", ["le poids de plastique vierge utilisé a été réduit de 32 % par rapport à l’exercice 2020/21"],
          "état de durabilité (plastique vierge, périmètre de l'engagement mondial de la Fondation Ellen MacArthur ; exercices 2020/21 → 2024/25)",
          2020, 2024, -32)
P(s, "PLA_RECYCLED", ["S’assurer que tous les emballages soient recyclables, réutilisables ou compostables (10) 2025 100 % 99 % 99 %"],
  "état de durabilité (part d'emballages recyclables, réutilisables ou compostables ; colonnes : objectif 2025, 2023/24, 2024/25)", value=99)
J(s, "LAB_LIVING_WAGE", "autre_forme", "Document d'enregistrement universel 2024-2025 lu (ESEF) : « nous avons veillé à ce que la rémunération de tous les salariés respecte ou dépasse les exigences légales et réglementaires minimales applicables » — la référence est le minimum légal, pas un salaire décent calculé.")

# ---------------------------------------------------------------- Philips
s = "philips"
P(s, "LAB_CEO_PAY_RATIO", ["the ratio between the CEO and median annual total remuneration for all employees (excluding the highest-paid individual) was 83:1"],
  "remuneration report (ratio de rémunération du directeur général à la rémunération médiane de tous les salariés)", value=83)
P(s, "LAB_LIVING_WAGE", ["We pay at least a living wage and aim for employee engagement above the high-performance norm"],
  "rapport annuel (salaire décent : engagement, sans vérification par un tiers)", vtype="category", text="policy", norm=0.5)
J(s, "ENV_GHG_TREND", "non_trouvee", "Rapport annuel 2025 lu (ESEF) : une seule année de comparaison — « Total GHG emissions (Market-based) 4,122,628 4,348,133 » (2025, 2024) ; une baisse sur un an ne dit pas une trajectoire.")

# ---------------------------------------------------------------- Reckitt
s = "reckitt"
J(s, "LAB_GENDER_PAYGAP", "autre_forme", "Rapport annuel 2025 lu (ESEF) : écart publié par pays, pour les dix plus grands marchés, dans un document distinct — « Reckitt voluntarily discloses the gender pay gap for our 10 largest markets by workforce size … All data is published in our ESG Databook on our website ».")

# ---------------------------------------------------------------- Rémy Cointreau (exercice clos le 31/03/2026)
s = "remy-cointreau"
P(s, "LAB_CEO_PAY_RATIO", ["Ratio d’équité salariale entre la rémunération du dirigeant et la médiane des salariés 31 30",
                           "Pour le périmètre France, salaire médian des salariés présents au 31 mars 2026 sur la rémunération totale du PDG au cours de la même période"],
  "état de durabilité (ratio d'équité du PDG à la rémunération médiane, périmètre France ; colonnes 2024-2025, 2025-2026)", value=30)
P(s, "LAB_GENDER_PAYGAP", ["Écart de rémunération moyen entre les femmes et les hommes (%) +4,8% +0,79%"],
  "état de durabilité, ESRS S1-16 (écart de rémunération moyen femmes-hommes ; colonnes 2024-2025, 2025-2026)", value=0.79)
P(s, "WAT_INTENSITY", ["Indicateurs 2024-2025 2025-2026 Volume Volume Iso reporting financier Prélèvements d’eau (m 3 ) 308 427 278 130",
                       "Iso reporting financier Intensité de la consommation d’eau (m 3 /M€) 66 65"],
  "état de durabilité, ESRS E3-4 (intensité hydrique : consommation d'eau rapportée au chiffre d'affaires ; colonnes 2024-2025, 2025-2026)", value=65)
J(s, "SUP_VIGILANCE_PLAN", "autre_forme", "Rapport annuel 2025-2026 lu (ESEF) : « le Groupe n’est pas soumis à la loi n o 2017-399 du 27 mars 2017 relative au devoir de vigilance et ne publie donc pas son plan de vigilance … Toutefois, le Groupe a mis en place en interne un plan de vigilance dont les éléments sont intégrés dans le présent chapitre ».")
J(s, "ENV_GHG_TREND", "non_trouvee", "Rapport annuel 2025-2026 lu (ESEF) : une seule année de comparaison — « Émissions totales de GES (market-based) 155 171 148 660 » (2024-2025, 2025-2026) ; une baisse sur un an ne dit pas une trajectoire.")

# ---------------------------------------------------------------- Renault
s = "renault"
P(s, "TAX_EFFECTIVE_RATE", ["Produit (charge) d’impôts courants et différés (522) (647) Taux Effectif d’Impôts 42 % 18 %",
                            "Le taux effectif d’imposition est de 42 %"],
  "comptes consolidés, note sur l'impôt (taux effectif ; colonnes 2025, 2024 ; 2025 affecté par la non-reconnaissance d'impôts différés)", value=42)
P(s, "WAT_INTENSITY", ["le ratio d’intensité hydrique est calculé comme le rapport de la consommation d’eau de ses opérations propres par le chiffre d’affaires total",
                       "Renault Group attire l’attention sur la difficulté à interpréter ce ratio, égal à 38 m 3 /MEUR en 2025"],
  "état de durabilité, ESRS E3-4 (intensité hydrique réglementaire : consommation d'eau rapportée au chiffre d'affaires)", value=38)
J(s, "LAB_LIVING_WAGE", "autre_forme", "Rapport financier annuel 2025 lu (ESEF) : « Dans des régions où le Groupe est présent de façon significative, Renault Group a choisi comme base de référence les salaires minimaux nationaux » — le salaire minimum sert de référence de salaire décent.")

# ---------------------------------------------------------------- SEB
s = "seb"
P(s, "LAB_GENDER_PAYGAP", ["l'écart de rémunération moyen entre les hommes et les femmes au niveau consolidé - sur les données de salaire de base - est de 1,5% en faveur des hommes"],
  "état de durabilité, ESRS S1-16 (écart de rémunération moyen femmes-hommes, calculé sur le salaire de base)", value=1.5)
P(s, "WAT_INTENSITY", ["Water Intensity Ratio ( m 3 /M€) 89 115 131 - 23 %"],
  "état de durabilité, ESRS E3-4 (intensité hydrique ; colonnes 2025, 2024, 2023 puis variation 2025/2024)", value=89)
P(s, "SUP_VIGILANCE_PLAN", ["4.6 Plan de vigilance 4.6.1 Gestion des risques d’atteintes graves aux personnes et à l’environnement 4.6.2 Prévenir et gérer les risques sociaux et sociétaux liés à la santé, sécurité et sûreté des personnes 4.6.3 Prévenir et gérer les risques liés à l’environnement 4.6.4 Mécanisme d’alerte et de recueil des signalements 4.6.5 Pilotage, gouvernance et suivi du déploiement du plan"],
  VIG, vtype="category", text="complet", norm=1)
J(s, "ENV_TAXONOMY_CAPEX", "non_trouvee", "Rapport financier annuel 2025 lu (ESEF) : aucun CapEx aligné — « En 2025, le montant total de CapEx alignées à la Taxonomie est nul, comparativement à 7,5 millions d’euros, soit 2,3 % des CapEx consolidées en 2024 ».")

# ---------------------------------------------------------------- Shell
s = "shell"
P(s, "ENV_TAXONOMY_CAPEX", ["Our aligned capex was $ 1,370 million or 4.6% (2024: $ 1,849 million or 6.0% ). Our taxonomy-aligned capex is associated with activities including elements of our hydrogen, wind, solar, battery storage, biogas, and electric vehicle charging businesses"],
  "taxonomie verte de l'UE (publication volontaire), CapEx alignés", value=4.6, text="4,6 %", norm=0.046)
P(s, "LAB_LIVING_WAGE", ["Shell's pay is designed to be market competitive. We expect that our employees can meet their basic needs through the pay and benefits that we provide"],
  "sustainability statements, ESRS S1-10 (salaire adéquat : déclaration, sans vérification par un tiers)", vtype="category", text="policy", norm=0.5)
J(s, "ENV_GHG_TREND", "non_trouvee", "Rapport annuel 2025 lu (ESEF) : une seule année de comparaison — « Total GHG emissions (market-based) million tonnes CO 2 e 1,142 1,166 » (2025, 2024) ; une baisse sur un an ne dit pas une trajectoire.")
J(s, "ENV_GHG_INTENSITY", "autre_forme", "Rapport annuel 2025 lu (ESEF) : intensité publiée par dollar — « Total GHG emissions per net revenue (market-based) tonnes CO 2 e / $ 0.004 0.004 » (2025, 2024), soit environ 4 000 t CO2e par million de dollars.")

# ---------------------------------------------------------------- Société Générale
s = "societe-generale"
J(s, "ENV_GHG_TREND", "non_trouvee", "Rapport financier annuel 2025 lu (ESEF) : une seule année de comparaison — « Émissions totales de GES (fondées sur le marché) 77 220 422 79 391 731 -3% » (2025, 2024) ; une baisse sur un an ne dit pas une trajectoire.")

# ---------------------------------------------------------------- Stellantis
s = "stellantis"
P(s, "WAT_INTENSITY", ["Water intensity ratio 2025 2024 Total water consumed (m 3 ) 6,932,589 7,705,671 Net revenues (€ million) 153,508 156,878 Water intensity ratio (m 3 /€ million) 45.16 49.12"],
  "sustainability statement, ESRS E3-4 (intensité hydrique réglementaire : consommation d'eau rapportée au chiffre d'affaires ; colonnes 2025, 2024)", value=45.16)
P(s, "TAX_EFFECTIVE_RATE", ["Total Tax expense/(benefit) (4,273) (1,488) 3,793 Effective tax rate 16.1 % -36.9 % 16.9 %",
                            "The effective tax rate for the year ended December 31, 2025 is 16.1 percent"],
  "consolidated financial statements, note sur l'impôt (taux effectif 2025 ; produit d'impôt sur une perte avant impôt)", value=16.1)
P(s, "LAB_LIVING_WAGE", ["We work towards providing competitive and living wages"],
  "rapport annuel (salaire décent : engagement, sans vérification par un tiers)", vtype="category", text="policy", norm=0.5)

# ---------------------------------------------------------------- TotalEnergies
s = "totalenergies"
P(s, "LAB_LIVING_WAGE", ["100% des collaborateurs bénéficient d’une rémunération directe au moins égale au salaire décent du pays ( reporting mondial en place depuis 2022)"],
  "état de durabilité (salaire décent : mesure interne mondiale, sans vérification par un tiers)", vtype="category", text="policy", norm=0.5)
J(s, "ENV_GHG_TREND", "non_trouvee", "Rapport financier annuel 2025 lu (ESEF) : une seule année de comparaison au périmètre ESRS — « Émissions totales de GES (fondées sur le marché) 387 000 000 379 000 000 -2% » (2024, 2025 ; scopes 1, 2 et 3 catégorie 11) ; une baisse sur un an ne dit pas une trajectoire.")
J(s, "WAT_INTENSITY", "non_trouvee", "Rapport financier annuel 2025 lu (ESEF) : « en l’absence des informations des sites non opérés, le calcul de l’intensité hydrique au périmètre ESRS ne peut pas être effectué ».")

# ---------------------------------------------------------------- Ubisoft (exercice clos le 31/03/2026)
s = "ubisoft"
P(s, "GOV_BOARD_INDEP", ["14 ADMINISTRATEURS/RICES 54,55 % ADMINISTRATEUR/RICES INDÉPENDANT(E)S (1) 45,45 % DE PARITÉ FEMMES/HOMMES (2)"],
  "gouvernement d'entreprise, présentation synthétique du conseil au 20 mai 2026 (indépendance)", value=54.55, norm=0.5455)
P(s, "GOV_BOARD_GENDER", ["14 ADMINISTRATEURS/RICES 54,55 % ADMINISTRATEUR/RICES INDÉPENDANT(E)S (1) 45,45 % DE PARITÉ FEMMES/HOMMES (2)",
                           "Le Conseil estime que le pourcentage de 40 % d’administratrices, requis par les textes légaux, correspond à une représentation équilibrée"],
  "gouvernement d'entreprise, présentation synthétique du conseil au 20 mai 2026 (part de femmes)", value=45.45)
P(s, "LAB_GENDER_PAYGAP", ["l’écart de rémunération non ajusté entre les femmes et les hommes est de 7,98 % en faveur des hommes"],
  "état de durabilité, ESRS S1-16 (écart de rémunération non ajusté, méthode CSRD)", value=7.98)
P(s, "LAB_CEO_PAY_RATIO", ["le ratio de rémunération annuelle totale est de 29,15 % (ratio calculé entre la personne la mieux payée et la rémunération médiane de l’ensemble des salariés présents de manière continue depuis au moins deux exercices fiscaux)"],
  "état de durabilité, ESRS S1-16 (ratio de rémunération annuelle totale, écrit « 29,15 % » dans le rapport : la personne la mieux payée gagne 29,15 fois la médiane)", value=29.15)
P(s, "TAX_EFFECTIVE_RATE", ["TOTAL IMPÔT SUR LES RÉSULTATS 127,8 TAUX D'IMPÔT EFFECTIF -9,20 %"],
  "comptes consolidés au 31 mars 2026, note sur l'impôt (charge d'impôt sur une perte avant impôt)", value=-9.2)
P(s, "ENV_SCOPE3_DISCLOSED", ["La plus grande partie des émissions du Groupe sont liées aux émissions de scope 3, représentant plus de 98 % des émissions globales"],
  "état de durabilité, ESRS E1-6 (émissions de scope 3)", vtype="boolean", boolean="true", norm=1)
P(s, "SUP_VIGILANCE_PLAN", ["5.7.2 RISQUES DIRECTS LIÉS AUX ACTIVITÉS DU GROUPE : CARTOGRAPHIE DES RISQUES", "5.7.4 MISE EN PLACE ET SUIVI DES MESURES"],
  VIG + " (« Le Plan de vigilance »)", vtype="category", text="complet", norm=1)
P(s, "LAB_LIVING_WAGE", ["Ubisoft a identifié 7 cas de non-adéquation avec le salaire décent en Serbie, représentant 7,37 % des effectifs au niveau du pays et moins de 0,1 % au niveau du Groupe"],
  "état de durabilité, ESRS S1-10 (salaire décent : analyse interne couvrant 95 % des effectifs, sans vérification par un tiers)", vtype="category", text="policy", norm=0.5)

# ---------------------------------------------------------------- Lotus Bakeries (version anglaise du rapport)
s = "lotus-bakeries"
trend(s, "ENV_GHG_TREND", ["GHG Indicators unit of measure 2025 2024 Base year 2023 variance 2025-2024 variance 2025-2023",
                           "Total GHG emissions (market-based) tCO 2 e 640,963 606,923 557,275 5.6% 15.0%"],
      "sustainability statement, ESRS E1-6, émissions totales de GES, scopes 1, 2 et 3 (fondées sur le marché, tCO2e ; colonnes 2025, 2024, 2023 (référence))",
      2023, 2025, 640963, 557275)
P(s, "ENV_SCOPE3_DISCLOSED", ["SCOPE 3 tCO 2 e 597,579 569,021 516,802 5.0% 15.6%"],
  "sustainability statement, ESRS E1-6 (émissions de scope 3 ; colonnes 2025, 2024, 2023)", vtype="boolean", boolean="true", norm=1)
P(s, "LAB_LIVING_WAGE", ["All our employees are paid adequate wages"],
  "sustainability statement, ESRS S1-10 (salaire adéquat : déclaration, sans vérification par un tiers)", vtype="category", text="policy", norm=0.5)
J(s, "LAB_GENDER_PAYGAP", "autre_forme", "Rapport annuel 2025 lu (ESEF, version anglaise) : écart publié comme une fourchette, sans valeur — « Maintain the gender pay gap below 5% % -5% to +5% <5% <5% » (2025, 2024).")
J(s, "PLA_RECYCLED", "autre_forme", "Rapport annuel 2025 lu (ESEF, version anglaise) : contenu recyclé publié par matériau, sans part globale — « recycled content in paper & pulp- and glass-based packaging of 78% and 45% respectively. Recycled content for plastic packaging in food-contact applications is minimal ».")
J(s, "WAT_INTENSITY", "non_trouvee", "Rapport annuel 2025 lu (ESEF, version anglaise) : l'eau n'est pas un enjeu matériel pour l'entreprise — « water stewardship did not come forward as material for Lotus Bakeries » ; aucune intensité publiée.")

# ================================================================ Documents de l'AMF (BDIF)
# ---------------------------------------------------------------- Bonduelle (exercice clos le 30/06/2025)
s = "bonduelle"
trend_pct(s, "PLA_REDUCTION", ["45 % de réduction du plastique vierge d'origine fossile utilisé dans nos emballages, par rapport à 2020"],
          "chiffres clés de l'exercice 2024-2025 (plastique vierge d'origine fossile des emballages, en volume, par rapport à l'exercice 2019-2020)",
          2020, 2025, -45)
P(s, "PLA_RECYCLED", ["98 % de nos emballages sont conçus pour être recyclables ou réutilisables"],
  "chiffres clés de l'exercice 2024-2025 (emballages conçus pour être recyclables ou réutilisables)", value=98)
P(s, "WAT_INTENSITY", ["Près de 9 millions m 3 d'eau prélevée par nos usines Intensité hydrique 4 076 m 3 / M€ chiffre d'affaires"],
  "état de durabilité, ESRS E3 (intensité hydrique publiée sur les prélèvements rapportés au chiffre d'affaires, exercice 2024-2025)", value=4076)
P(s, "ENV_TAXONOMY_CAPEX", ["CapEx des activités durables sur le plan environnemental (alignées sur la taxonomie) (A.1) N/A 531 0 % 100 %"],
  "taxonomie verte de l'UE (règlement 2020/852, art. 8), tableau réglementaire des CapEx (montant aligné en milliers d'euros, part alignée arrondie à 0 %)",
  value=0, text="0 %", norm=0)

# ---------------------------------------------------------------- Carrefour
s = "carrefour"
P(s, "PLA_RECYCLED", ["la part des emballages recyclables, réutilisables ou réemployables progresse de 11 pts", "67 % en 2025 contre 56 % en 2024), elle reste inférieure à la cible de 100 % fixée pour 2025"],
  "état de durabilité (emballages des produits à marque Carrefour recyclables, réutilisables ou réemployables)", value=67)
J(s, "PLA_REDUCTION", "non_trouvee", "Document d'enregistrement universel 2025 lu (AMF) : engagement publié sans évolution chiffrée — « supprimer 15 000 tonnes de plastique vierge dans les emballages de ses produits à marques propres d’ici 2030 (soit une réduction de 10 % de la quantité de plastique vierge utilisée dans ses emballages à usage unique) ».")

# ---------------------------------------------------------------- Crédit Mutuel Alliance Fédérale
s = "credit-mutuel-alliance-federale"
J(s, "ENV_GHG_TREND", "non_trouvee", "Document d'enregistrement universel 2025 lu (AMF) : une seule année de comparaison — « Émissions totales de GES (basées sur le marché) (tCO2eq) 21 630 092 22 366 449 -3 % » (2025, 2024) ; une baisse sur un an ne dit pas une trajectoire.")
J(s, "ENV_TAXONOMY_CAPEX", "autre_forme", "Document d'enregistrement universel 2025 lu (AMF) : établissement financier — l'alignement sur la taxonomie verte se publie par le ratio d'actifs verts (GAR), non par la part des CapEx.")
J(s, "WAT_INTENSITY", "non_trouvee", "Document d'enregistrement universel 2025 lu (AMF) : « ESRS E3-4 Consommation d’eau totale en m3 par rapport au chiffre d’affaires net … Non matériel » — donnée non publiée, jugée non matérielle.")

# ---------------------------------------------------------------- Danone
s = "danone"
P(s, "PLA_RECYCLED", ["Danone a atteint 84,9 % d’emballages recyclables, réutilisables ou compostables et a récupéré 62,7 % du plastique mis sur le marché via des systèmes de collectes (contre respectivement 85 % et 60 % en 2024)"],
  "état de durabilité (emballages recyclables, réutilisables ou compostables, 2025)", value=84.9)
P(s, "LAB_LIVING_WAGE", ["Danone a obtenu la certification Living Wage en 2025",
                         "Obtenir et conserver la certification d’employeur assurant un salaire décent du Fair Wage Network (FWN) 2025 Certification Living Wage Employer du FWN"],
  "état de durabilité, ESRS S1-10 (salaire décent ; certification par un organisme tiers)", vtype="category", text="verified", norm=1)
P(s, "ENV_TAXONOMY_CAPEX", ["Parmi ces CapEx éligibles, 59 millions d’euros sont considérés comme alignés avec les critères de la taxonomie européenne, ce qui représente 3,4 % du total CapEx du Groupe"],
  "taxonomie verte de l'UE (règlement 2020/852, art. 8), CapEx alignés (bâtiments, 2025)", value=3.4, text="3,4 %", norm=0.034)

# ---------------------------------------------------------------- Hermès
s = "hermes"
P(s, "ENV_TAXONOMY_CAPEX", ["2025 CapEx éligibles CapEx alignés Montant en % du total des CapEx Montant en % du total des CapEx CapEx alignés CapEx exigibles Total général CapEx taxonomie 1 911 1 257 66 % 424 22 % 34 %"],
  "taxonomie verte de l'UE (règlement 2020/852, art. 8), CapEx en millions d'euros : total 1 911, éligibles 1 257 (66 %), alignés 424 (22 % du total)", value=22, text="22 %", norm=0.22)
P(s, "WAT_INTENSITY", ["2025 2024 Intensité hydrique sur les prélèvements en m 3 d’eau industrielle/M€ de CA 1 37 41 Intensité hydrique sur les consommations en m 3 d’eau industrielle/M€ de CA 2 3 1"],
  "état de durabilité, ESRS E3-4 (intensité hydrique sur les consommations d'eau industrielle ; après le renvoi de note, colonnes 2025, 2024)", value=3)
P(s, "LAB_LIVING_WAGE", ["Hermès garantit à ses collaborateurs un salaire décent, conformément à la réglementation locale et aux indices de référence applicables. L’analyse menée par le groupe a confirmé ce fait"],
  "état de durabilité, ESRS S1-10 (salaire décent : analyse interne, sans vérification par un tiers)", vtype="category", text="policy", norm=0.5)

# ---------------------------------------------------------------- Kering
s = "kering"
P(s, "ENV_TAXONOMY_CAPEX", ["Part des Capex associés à des activités économiques éligibles ou alignées sur la taxonomie pour 2025 (par activité )",
                            "TOTAL CAPEX 81 % 398 17 % 17 %"],
  "taxonomie verte de l'UE (règlement 2020/852, art. 8), tableau réglementaire des CapEx (éligibles 81 %, alignés 398 M€, soit 17 %)", value=17, text="17 %", norm=0.17)

# ---------------------------------------------------------------- LVMH
s = "lvmh"
P(s, "PLA_RECYCLED", ["Pourcentage de matériaux recyclés dans les emballages clients pour le verre et le plastique (en pourcentage du poids) 49 % 41 % 70 % (2030)"],
  "programme LIFE 360 (matériaux recyclés dans les emballages clients en verre et en plastique ; colonnes 2025, 2024, objectif 2030)", value=49)
J(s, "PLA_REDUCTION", "non_trouvee", "Document d'enregistrement universel 2025 lu (AMF) : une seule année de comparaison — « Quantité de plastique vierge d’origine fossile dans les emballages remis aux clients (en tonnes) 7 401 8 326 0 (2026) » (2025, 2024, objectif 2026) ; une baisse sur un an ne dit pas une trajectoire.")

# ================================================================ Rapports légaux publiés sur le site de l'émetteur
# ---------------------------------------------------------------- Savencia
s = "savencia"
P(s, "GOV_BOARD_INDEP", ["2025 2024 Pourcentage de membres du conseil d'administration indépendants 53,3 % 60%"],
  "gouvernance (indépendance du conseil d'administration ; colonnes 2025, 2024)", value=53.3, norm=0.533)
trend(s, "ENV_GHG_TREND", ["Total des émissions scope 1, 2 et 3 (en market based) 9 858 044 9 494 676 10 123 659 3,8 % -2,6 %",
                           "Bilan carbone en TCO2 2025 2024 2019 Variation vs A-1 Variation vs 2019"],
      "environnement, ESRS E1-6, émissions totales de GES, scopes 1, 2 et 3 (fondées sur le marché, tCO2 ; colonnes 2025, 2024, 2019 (référence))",
      2019, 2025, 9858044, 10123659)
P(s, "ENV_GHG_INTENSITY", ["Intensité des émissions GES par revenu net", "Emissions totales scope 1,2 et 3 en market based par revenu net (Tco2/m€) 1 417 1 330 2 022 6,6 % -29,9 %"],
  "environnement, ESRS E1-6 (intensité de GES par revenu net, fondée sur le marché ; colonnes 2025, 2024, 2019)", value=1417)
P(s, "ENV_SCOPE3_DISCLOSED", ["Scope 3 amont 9 037 574 8 629 693 9 069 971 4,7 % -0,4 %"],
  "environnement, ESRS E1-6 (émissions de scope 3 ; colonnes 2025, 2024, 2019)", vtype="boolean", boolean="true", norm=1)
J(s, "LAB_GENDER_PAYGAP", "autre_forme", "Rapport de durabilité 2025 lu (site de la société) : écart publié pour la France seulement — « En 2025, sur le périmètre SAVENCIA Fromage & Dairy France l’écart de rémunération moyenne entre femmes et hommes est de 3% ».")
J(s, "LAB_CEO_PAY_RATIO", "autre_forme", "Rapport de durabilité 2025 lu (site de la société) : ratios publiés par dirigeant et pour la France seulement — « Ratio rémunération du dirigeant mandataire social / rémunération médiane des salariés France 25,4 32,2 25,4 29,4 ».")

# ---------------------------------------------------------------- Nestlé
s = "nestle"
trend_pct(s, "PLA_REDUCTION", ["We reduced the usage of virgin plastic by 28.0% versus the 2018 baseline"],
          "résumé (plastique vierge, par rapport à l'année de référence 2018)", 2018, 2025, -28.0, dec=1)
P(s, "PLA_RECYCLED", ["In 2025, the proportion of our packaging that was recyclable, reusable or compostable was 89.5%"],
  "Part 2, économie circulaire (emballages recyclables, réutilisables ou compostables)", value=89.5)
trend(s, "ENV_GHG_TREND", ["Indicator Unit Baseline value (2018) 2022 2023 2024 2025",
                           "SBTi Net zero gross GHG emissions Million metric tonnes of CO₂ equivalents (tCO₂e) 87.09 71.26 69.04"],
      "annexe 4, indicateurs climat (émissions BRUTES du périmètre de l'objectif zéro émission nette validé par la SBTi, en millions de tCO2e ; colonnes 2018 (référence), 2024, 2025 ; "
      "la réduction nette, après absorptions, publiée à 24,52 %, n'est pas retenue)", 2018, 2025, 69.04, 87.09)
fx(s, "ENV_GHG_INTENSITY", ["Total GHG emissions intensity market-based Metric tonnes of CO₂ equivalents (tCO₂e)/Million CHF 772"],
   "annexe 4 (intensité de GES par chiffre d'affaires, fondée sur le marché, 2025 : 772 t CO2e par million de francs suisses)", 772, "CHF", "t CO2e/M€")

# ---------------------------------------------------------------- Les Mousquetaires
s = "mousquetaires"
J(s, "LAB_GENDER_PAYGAP", "autre_forme", "Rapport de durabilité 2025 lu (site du groupe) : écart publié pour les cadres seulement — « Au sein de la catégorie cadres, un écart de rémunération femmes-hommes moyen de +5,7% subsiste en faveur des hommes » ; pour l'ensemble, seulement « inférieur à la moyenne française et européenne ».")

# ---------------------------------------------------------------- Henkel
s = "henkel"
P(s, "LAB_CEO_PAY_RATIO", ["Remuneration metrics Unit 2024 2025 Unadjusted gender pay gap % 1.8 0.7 Remuneration ratio of the highest paid individual to the median for all employees Ratio 137 142"],
  "sustainability statement, ESRS S1-16 (ratio de rémunération de la personne la mieux payée à la médiane ; colonnes 2024, 2025)", value=142)
P(s, "LAB_GENDER_PAYGAP", ["Remuneration metrics Unit 2024 2025 Unadjusted gender pay gap % 1.8 0.7"],
  "sustainability statement, ESRS S1-16 (écart de rémunération non ajusté ; colonnes 2024, 2025)", value=0.7)
trend(s, "ENV_GHG_TREND", ["GHG emissions Emissions Base year 2021 N = 2024 N = 2025",
                           "Total GHG emissions (SBTi target scope) (t CO2e) 18,768,446 14,911,095 13,352,035 -10.5% -28.9%"],
      "sustainability statement, ESRS E1-6, émissions totales du périmètre de l'objectif validé par la SBTi (tCO2e ; colonnes 2021 (référence), 2024, 2025) ; "
      "le total complet n'est publié que pour 2024 et 2025 (35 463 917 puis 33 847 942 t CO2e, fondées sur le marché)", 2021, 2025, 13352035, 18768446)
P(s, "ENV_TAXONOMY_CAPEX", ["CapEx of environmentally sustainable activities (Taxonomy-aligned) (A.1) 7.9 1%"],
  "taxonomie verte de l'UE (règlement 2020/852, art. 8), tableau réglementaire des CapEx (7,9 M€ alignés, soit 1 %)", value=1, text="1 %", norm=0.01)
P(s, "WAT_INTENSITY", ["Water Metric Unit 2024 2025 Total water consumption m³ 3,858,063 3,721,666",
                       "Total water consumption intensity per million EUR net revenue m³/EUR m 179 182"],
  "sustainability statement, ESRS E3-4 (intensité hydrique réglementaire : consommation d'eau rapportée au chiffre d'affaires ; colonnes 2024, 2025)", value=182)
P(s, "LAB_LIVING_WAGE", ["We ensure fair and timely pay based on performance and market standards • Adequate living wage reviews"],
  "sustainability statement, ESRS S1 (salaire adéquat : revues internes, sans vérification par un tiers)", vtype="category", text="policy", norm=0.5)

# ---------------------------------------------------------------- Mars (rapport volontaire)
s = "mars"
trend_pct(s, "ENV_GHG_TREND", ["6.4% annual reduction in GHGs compared to 2024 (as % of 2015), contributing to a total 16.9% reduction in GHGs across our full value chain from our 2015 baseline"],
          "Healthy Planet (émissions de GES de toute la chaîne de valeur, par rapport à l'année de référence 2015)", 2015, 2025, -16.9, ghg=True, dec=1)
trend_pct(s, "PLA_REDUCTION", ["in 2025, we have had a 5.9% reduction in virgin plastic compared to our 2019 baseline"],
          "Healthy Planet (plastique vierge, par rapport à l'année de référence 2019)", 2019, 2025, -5.9, dec=1)
P(s, "PLA_RECYCLED", ["67.6% of our consumer-facing packaging designed to be reusable, recyclable or compostable"],
  "Healthy Planet (emballages destinés aux consommateurs conçus pour être réutilisables, recyclables ou compostables)", value=67.6)
P(s, "ENV_SCOPE3_DISCLOSED", ["Scope 1 Scope 2 Scope 3 2025 GHG Emissions 26.65 MtCO2e 96% 1%3%"],
  "Healthy Planet (émissions de GES 2025 par scope ; le scope 3 en représente 96 %)", vtype="boolean", boolean="true", norm=1)

# ---------------------------------------------------------------- Lactalis (rapport RSE)
s = "lactalis"
P(s, "GOV_BOARD_GENDER", ["2025 Nombre de membres non exécutifs 4 Nombre de membres exécutifs 1 Nombre de représentants des salariés 0 Pourcentage de femmes (%) 40 % Pourcentage d’hommes (%) 60 % Pourcentage de membres indépendants au sein du Conseil de surveillance (%) 33 %"],
  "gouvernance (composition du conseil de surveillance, 2025)", value=40)
P(s, "GOV_BOARD_INDEP", ["Pourcentage de membres indépendants au sein du Conseil de surveillance (%) 33 %"],
  "gouvernance (indépendance du conseil de surveillance, 2025)", value=33, norm=0.33)
P(s, "SUP_VIGILANCE_PLAN", ["6. PLAN DE VIGILANCE 2025 128 6.1 Introduction 128 6.2 Gouvernance 128 6.3 Périmètre du plan de vigilance 128 6.4 Dialogue avec les parties prenantes 129 6.5 Cartographie des risques en matière de droits humains, santé & sécurité et environnement 129 6.6 Mesures d’évaluation régulières 134 6.7 Atténuation des risques et prévention des atteintes graves 137 6.8 Mécanisme d’alerte et de recueil des signalements 144 6.9 Suivi des mesures et évaluation de leur efficacité 145 6.10 Compte rendu du plan de vigilance 2025"],
  VIG, vtype="category", text="complet", norm=1)
P(s, "ENV_SCOPE3_DISCLOSED", ["Les principales sources d’émissions de GES de Lactalis se concentrent sur le scope 3 (95 % des émissions de GES totales)"],
  "environnement (émissions de scope 3)", vtype="boolean", boolean="true", norm=1)

# ---------------------------------------------------------------- Ferrero (exercice clos le 31/08/2025 ; rapport volontaire)
s = "ferrero"
trend(s, "ENV_GHG_TREND", ["Emissions Unit F Y 2022/23* FY 2023/24* FY 2024/25 GWP emissions total (Total Scope 1 + Scope 2 market-based + Scope 3) tCO2eq 10,924,391 10,192,517 10,233,649"],
      "annual emissions performance (émissions totales, scopes 1, 2 fondé sur le marché et 3, tCO2eq ; exercices 2022/23, 2023/24, 2024/25)", 2022, 2024, 10233649, 10924391)
P(s, "PLA_RECYCLED", ["The share of packaging recyclable, reusable or compostable in practice and at scale reached 86.8%"],
  "emballages (part recyclable, réutilisable ou compostable en pratique et à grande échelle, exercice 2024/25)", value=86.8)
P(s, "ENV_SCOPE3_DISCLOSED", ["GWP emissions total (Total Scope 1 + Scope 2 market-based + Scope 3) tCO2eq 10,924,391 10,192,517 10,233,649"],
  "annual emissions performance (émissions de scope 3 incluses et détaillées)", vtype="boolean", boolean="true", norm=1)

# ---------------------------------------------------------------- Unilever (rapport 20-F déposé à la SEC ; le site refuse les outils automatiques)
s = "unilever"
P(s, "PLA_RECYCLED", ["Plastics Goal Unilever Unilever (including Ice Cream) 2025 2025 2024 2023",
                      "100% of our plastic packaging to be reusable, recyclable or compostable (a)(f) 100% 57% 57% 57% 53%"],
  "objectifs de durabilité (emballages plastiques réutilisables, recyclables ou compostables ; colonnes : objectif, 2025, 2025 avec Ice Cream, 2024, 2023)", value=57)
P(s, "ENV_SCOPE3_DISCLOSED", ["Reduce absolute Scope 3 energy and industrial (E&I) GHG emissions by 42% by 2030 from a 2021 baseline (b)(c)(d) (42.0)% (11) % (11) % (7) %"],
  "objectifs climat (évolution publiée des émissions de scope 3 depuis 2021)", vtype="boolean", boolean="true", norm=1)
J(s, "ENV_GHG_TREND", "autre_forme", "Rapport 20-F 2025 lu (SEC) : évolutions publiées par périmètre, sans total des scopes 1, 2 et 3 — opérations (scopes 1 et 2) depuis 2015, « Scope 3 energy and industrial (E&I) » et « Scope 3 … (FLAG) » depuis 2021.")

# ---------------------------------------------------------------- Procter & Gamble (exercice clos le 30/06/2025 ; rapport volontaire)
s = "procter-gamble"
P(s, "PLA_RECYCLED", ["80% of our consumer packaging is designed to be recyclableor reusable 80% 78%"],
  "Data & Metrics Report, exercice 2025 (emballages grand public conçus pour être recyclables ou réutilisables ; colonnes 2025, 2024)", value=80)
P(s, "ENV_SCOPE3_DISCLOSED", ["Scope 3 Categories Estimated FY25 Metric Tons CO2eq Purchased Goods and Services21 13,700,000"],
  "Data & Metrics Report, exercice 2025 (émissions de scope 3 estimées par catégorie)", vtype="boolean", boolean="true", norm=1)
J(s, "PLA_REDUCTION", "autre_forme", "Data & Metrics Report de l'exercice 2025 lu (site de la société) : réduction publiée par unité vendue, non en tonnage — « Reduce our use of virgin petroleum plastic in our consumer packaging by 50% per unit (2018 baseline). 24% reduction ».")
J(s, "ENV_GHG_TREND", "autre_forme", "Data & Metrics Report de l'exercice 2025 lu (site de la société) : le total publié ne couvre que les scopes 1 et 2 — « Total GHG emissions 2,080 2,125 2,250 » (milliers de tCO2e, exercices 2025, 2024, 2023 ; « Total GHG emissions = Scope 1 + Scope 2 ») ; le scope 3 est estimé à part, par catégorie, pour 2025 seulement.")

# ---------------------------------------------------------------- Mondelēz International (fiche de données volontaire)
s = "mondelez"
trend_pct(s, "ENV_GHG_TREND", ["35% end-to-end CO₂e emissions reduction by 2030 (vs. 2018) (%) (3)(2) 21 12 3"],
          "Non-Financial Datasheet 2025 (réduction des émissions de bout en bout, chaîne de valeur entière, par rapport à 2018 ; colonnes 2025, 2024, 2023)",
          2018, 2025, -21, ghg=True)
trend_pct(s, "PLA_REDUCTION", ["Reduction in overall virgin plastic (vs. 2020) (%)(2)(10) 11.5 4.6 + 1.7 2.9"],
          "Non-Financial Datasheet 2025 (plastique vierge, par rapport à 2020 ; colonnes 2025, 2024, 2023, 2022)", 2020, 2025, -11.5, dec=1)
P(s, "PLA_RECYCLED", ["PackaGinG 2025 2024 2023 2022 Total weight of packaging (metric tonnes)(9) 908,200 875,800 915,500 943,600 Packaging designed to be recyclable (%)(10) 96 96 96 96"],
  "Non-Financial Datasheet 2025 (emballages conçus pour être recyclables ; colonnes 2025, 2024, 2023, 2022)", value=96)
P(s, "ENV_SCOPE3_DISCLOSED", ["Scope 3 (Other indirect) GHG emissions (metric tonnes CO₂e)(1) 29,174,000 32,194,000 35,067,000"],
  "Non-Financial Datasheet 2025 (émissions de scope 3 de bout en bout ; colonnes 2025, 2024, 2023)", vtype="boolean", boolean="true", norm=1)
