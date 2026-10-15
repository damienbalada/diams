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
    return "Rapport financier annuel 2025 (ESEF)" if DEP[slug]["period_end"].startswith("2025-12") else \
        f"Rapport annuel de l'exercice clos le {'/'.join(reversed(DEP[slug]['period_end'].split('-')))} (ESEF)"


def P(slug, code, quotes, cadre, value=None, vtype="numeric", text="", boolean="", norm="", calc=""):
    q = " ; ".join(f"« {x} »" for x in quotes)
    rows.append({**{c: "" for c in COLS}, "entity_slug": slug, "indicator_code": code, "source_code": "ESEF", "nature": "result",
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


def trend_pct(slug, code, quotes, cadre, y0, y1, pct, ghg=False):
    """Variation publiée depuis l'année de référence (pct < 0 = baisse)."""
    n = y1 - y0
    r = round(((1 + pct / 100) ** (1 / n) - 1) * 100, 2)
    sign = "−" if pct < 0 else "+"
    calc = f"rythme annuel moyen ({y0} → {y1}, {n} an{'s' if n > 1 else ''}) : (1 {sign} {fr(abs(pct), 0 if pct == int(pct) else 1).lstrip('+')} %)^(1/{n}) − 1 = {fr(r).lstrip('+')} %"
    P(slug, code, quotes, cadre, value=r, norm=(round(max(0.0, min(1.0, -r / 4.2)), 4) if ghg else ""), calc=calc)


def fx(slug, code, quotes, cadre, a, cur, unit_out, year="2025", d=1):
    rate = FX[cur]
    c = round(a * rate, d)
    calc = f"taux de change annuel moyen {year} de la BCE (1 € = {str(rate).replace('.', ',')} {cur}) : {str(a).replace('.', ',')} × {str(rate).replace('.', ',')} = {str(c).replace('.', ',')}"
    P(slug, code, quotes, f"{cadre} (converti en {unit_out})", value=c, calc=calc)


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
