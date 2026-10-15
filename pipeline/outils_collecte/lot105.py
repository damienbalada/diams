"""Lot 105 : nouvelles tentatives — sanctions DGCCRF, rapports de Colgate et de Coty — tous les piliers.
Chaque preuve : citation(s) exacte(s) du rapport, cadre, calcul écrit en toutes lettres.
Les absences lues (« non matériel », publié autrement) vont au journal de relecture."""
import csv, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
S = os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
OUT = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline\curated\groupes_2026-10_lot105_nouvelles_tentatives.csv"
JOURNAL = os.path.join(S, "lot105_journal.json")
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
    rows.append({**{c: "" for c in COLS}, "entity_slug": DEP[slug].get("slug", slug), "indicator_code": code, "source_code": DEP[slug].get("source", "ESEF"), "nature": "result",
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
DEJA = set()


def J(slug, code, outcome, detail):
    journal.append({"slug": DEP[slug].get("slug", slug), "code": code, "outcome": outcome, "detail": detail, "source_url": DEP[slug]["report_url"]})


VIG = "plan de vigilance (C. com. L225-102-4) : analyse des risques, mesures, alerte et suivi"

# ---------------------------------------------------------------- DGCCRF : amendes pour retards de paiement (publications officielles)
DATES = {"advini": "2026-04-20", "dim-france": "2026-07-15", "paul-hartmann": "2026-08-27",
         "bretagne-viandes-distribution": "2026-10-12", "daucy-france": "2026-10-12"}
MONTANT = {"advini": (350000, "0,35 M€"), "dim-france": (300000, "0,3 M€"), "paul-hartmann": (55000, "0,055 M€"),
           "bretagne-viandes-distribution": (65000, "0,065 M€"), "daucy-france": (33000, "0,033 M€")}
for slug, d in json.load(open(os.path.join(S, "dgccrf_corps.json"), encoding="utf-8")).items():
    corps = d["corps"]
    q = corps.split(". La constatation")[0]
    m, txt = MONTANT[slug]
    rows.append({**{c: "" for c in COLS}, "entity_slug": slug, "indicator_code": "GOV_SANCTIONS", "source_code": "FR_DGCCRF",
                 "nature": "controversy", "observed_on": DATES[slug], "value_type": "category",
                 "value_text": f"amende de {txt} (retards de paiement aux fournisseurs)", "normalized_value": 0.5, "confidence": 0.95,
                 "source_url": d["url"],
                 "excerpt": f"DGCCRF, sanction publiée sur son site (page du {'/'.join(reversed(DATES[slug].split('-')))}, SIRET de la société, SIREN {d['siren']}) : « {q} » — amende administrative pour retards de paiement ; sévérité 0,5."})

# ---------------------------------------------------------------- Colgate-Palmolive (rapport 2025 de durabilité et d'impact social)
s = "colgate-palmolive#esg"
trend_pct(s, "PLA_REDUCTION", ["We achieved a 32% reduction in the use of virgin plastic by weight in our packaging vs. 2019"],
          "stratégie 2020-2025, bilan (plastique vierge des emballages, en poids)", 2019, 2025, -32)
P(s, "PLA_RECYCLED", ["We surpassed this target, using 27% post-consumer recycled plastic in our packaging"],
  "stratégie 2020-2025, bilan (part de plastique recyclé post-consommation dans les emballages, 2025 ; objectif : 25 %)", value=27)
P(s, "ENV_SCOPE3_DISCLOSED", ["Emissions 2020 2021 2022 2023 2024 2025", "Scope 3 Emissions* - Thousand MT CO2e 46,900 41,908 42,292 42,353 40,670 39,846"],
  "tableau des indicateurs (émissions de scope 3, milliers de tCO2e, 2020 à 2025)", vtype="boolean", boolean="true", norm=1)
J(s, "ENV_GHG_TREND", "autre_forme", "Rapport 2025 de durabilité lu : émissions publiées par scope (scope 1, scope 2 selon la localisation et selon le marché, scope 3), sans total de l'ensemble des émissions.")
J(s, "WAT_INTENSITY", "autre_forme", "Rapport 2025 de durabilité lu : intensité en eau publiée par unité produite (« Since 2002, we have reduced the water consumed per unit of production »), sans intensité rapportée au chiffre d'affaires.")

# ---------------------------------------------------------------- Coty (rapport de durabilité de l'exercice clos le 30/06/2025)
s = "coty#esg"
P(s, "GOV_BOARD_INDEP", ["% independent board members 77% 7 out of 9 are independent"],
  "gouvernance (part d'administrateurs indépendants au conseil)", value=77, norm=0.77)
P(s, "LAB_GENDER_PAYGAP", ["REMUNERATION METRICS", "Gender pay gap (average) 3.2%"],
  "personnel, indicateurs de rémunération selon l'ESRS S1-16 (écart de rémunération moyen femmes-hommes, exercice 2025)", value=3.2)
P(s, "LAB_CEO_PAY_RATIO", ["Annual total remuneration ratio of the highest paid individual to the median annual total remuneration for all employees (excluding the highest-paid individual) 411.80"],
  "personnel, indicateurs de rémunération selon l'ESRS S1-16 (ratio de la personne la mieux payée à la médiane des salariés, exercice 2025)", value=411.8)
trend(s, "ENV_GHG_TREND", ["RETROSPECTIVE MILESTONES AND TARGET YEARS Base year (recalculated) FY24* FY25 FY25 vs FY24 FY25 vs base year 2030 2050",
                           "Total GHG emissions (market-based) (tCO₂e) 1,227,169 913,509 862,351 -5%** -30%**",
                           "Reduce absolute Scope 3 GHG emissions by 28% by 2030 (SBTi-approved target). Year: 2019"],
      "planète, émissions totales de GES, scopes 1, 2 et 3 (fondées sur le marché, tCO2e ; colonnes : année de référence 2019 recalculée, exercice 2024, exercice 2025)",
      2019, 2025, 862351, 1227169)
fx(s, "ENV_GHG_INTENSITY", ["GHG emissions intensity METRIC VALUE (tCO2e PER $1M) Location-based 149 Market-based 146"],
   "planète (intensité de GES par million de dollars de chiffre d'affaires, fondée sur le marché, exercice 2025)", 146, "USD", "tCO2e/M€", d=0)
P(s, "WAT_INTENSITY", ["Water intensity ratio (total water consumption in m3 per mill EUR net revenue) 31"],
  "planète, eau (intensité hydrique : consommation d'eau rapportée au chiffre d'affaires net, exercice 2025)", value=31)
trend_pct(s, "PLA_REDUCTION", ["Reduce virgin plastic by 60% by 2030. Year: 2019 Value: 40,617 tonnes All plastic packaging In the first year since setting our target, we reduced our use of virgin plastic by 51%"],
          "planète, emballages (plastique vierge de l'ensemble des emballages plastiques, depuis l'année de référence 2019)", 2019, 2025, -51)
P(s, "PLA_RECYCLED", ["In FY25, our products are made of 10% post-consumer recycled materials"],
  "planète, emballages (part de matière recyclée post-consommation dans l'ensemble des matériaux d'emballage, exercice 2025)", value=10)
P(s, "ENV_SCOPE3_DISCLOSED", ["Total gross indirect (Scope 3) GHG emissions (tCO₂e) 1,169,373 903,087 850,240"],
  "planète (émissions de scope 3, tCO2e : année de référence, exercices 2024 et 2025)", vtype="boolean", boolean="true", norm=1)
J(s, "LAB_LIVING_WAGE", "autre_forme", "Rapport de durabilité de l'exercice 2025 lu : « In FY25, all Coty employees were paid an adequate wage, meeting or exceeding applicable legal minimums » — référence au minimum légal, pas d'engagement de salaire décent vérifié.")

# ---------------------------------------------------------------- Sodiaal (déclaration de performance extra-financière 2025)
s = "sodiaal"
P(s, "ENV_SCOPE3_DISCLOSED", ["Total émissions Scope 3 ktCo2e 6 522"],
  "annexe du rapport d'assurance limitée du commissaire aux comptes (indicateurs vérifiés : émissions de scope 3, 2025)", vtype="boolean", boolean="true", norm=1)
J(s, "ENV_GHG_TREND", "autre_forme", "Déclaration de performance extra-financière 2025 lue : évolutions publiées séparément — « Évolution de l’empreinte carbone Scope 1 et 2 depuis 2019 % - 23% » et « Évolution de l’empreinte carbone Scope 3 depuis 2019 % - 21% » — sans total des émissions de l'année de référence.")
J(s, "SUP_VIGILANCE_PLAN", "autre_forme", "Déclaration de performance extra-financière 2025 lue : « Le Code de Conduite du Groupe Sodiaal V4 a été diffusé en 2025 ainsi que le plan de Vigilance V3 » — plan mentionné, intégré au code de conduite, sans cartographie des risques ni compte rendu de mise en œuvre publiés dans le rapport.")
J(s, "WAT_INTENSITY", "autre_forme", "Déclaration de performance extra-financière 2025 lue : seule l'évolution des consommations d'eau des sites est publiée (« Évolution des consommations d’eau des sites depuis 2019 % - 24% »), sans intensité rapportée au chiffre d'affaires.")
J(s, "PLA_RECYCLED", "autre_forme", "Déclaration de performance extra-financière 2025 lue : seule la part d'emballages recyclables est publiée (« Part des emballages ménagers PGC recyclables (Candia, Sodiaal Fromage, Yoplait) % 90,5 »), pas la part de matière recyclée.")
for code in ("GOV_BOARD_GENDER", "GOV_BOARD_INDEP", "LAB_CEO_PAY_RATIO", "LAB_GENDER_PAYGAP", "ENV_GHG_INTENSITY", "TAX_EFFECTIVE_RATE", "ENV_TAXONOMY_CAPEX", "PLA_REDUCTION", "LAB_LIVING_WAGE"):
    J(s, code, "non_trouvee", "Rapport lu (déclaration de performance extra-financière 2025 de Sodiaal) : la donnée n'y figure pas.")

# ---------------------------------------------------------------- Avril et Pierre Fabre : rapports annuels narratifs
for s, doc in (("avril", "rapport annuel intégré 2025 d'Avril"), ("pierre-fabre", "rapport annuel 2025 des Laboratoires Pierre Fabre")):
    for code in ("GOV_BOARD_GENDER", "GOV_BOARD_INDEP", "LAB_CEO_PAY_RATIO", "LAB_GENDER_PAYGAP", "ENV_GHG_TREND", "ENV_GHG_INTENSITY",
                 "ENV_SCOPE3_DISCLOSED", "TAX_EFFECTIVE_RATE", "SUP_VIGILANCE_PLAN", "ENV_TAXONOMY_CAPEX", "PLA_REDUCTION", "PLA_RECYCLED",
                 "WAT_INTENSITY", "LAB_LIVING_WAGE"):
        J(s, code, "non_trouvee", f"Rapport lu ({doc}, publié par la société) : document de présentation, sans indicateur chiffré sur ce point.")

# ---------------------------------------------------------------- De'Longhi (rapport annuel 2025, traduction anglaise publiée par la société)
s = "delonghi#en"
P(s, "GOV_BOARD_GENDER", ["composition and diversity of the administrative, management and control bodies 2023 2024 2025 Board of Directors 11 11 12",
                          "Gender split Female 45% 45% 42%"],
  "état de durabilité, ESRS 2 GOV-1 (composition du conseil d'administration ; colonnes 2023, 2024, 2025)", value=42)
P(s, "GOV_BOARD_INDEP", ["composition and diversity of the administrative, management and control bodies 2023 2024 2025 Board of Directors 11 11 12",
                         "% of independent board members 63% 63% 58%"],
  "état de durabilité, ESRS 2 GOV-1 (part d'administrateurs indépendants ; colonnes 2023, 2024, 2025)", value=58, norm=0.58)
P(s, "LAB_CEO_PAY_RATIO", ["The ratio of the highest-earning individual’s total annual remu - neration to the median total annual remuneration of all em - ployees is 301 (245 in 2024)"],
  "état de durabilité, ESRS S1-16 (ratio de la personne la mieux payée à la médiane des salariés, 2025)", value=301)
P(s, "LAB_GENDER_PAYGAP", ["The pay gap, defined as the difference between the average compensation paid to female and male employees, expressed as a percentage of the average compensation paid to male employees, was 40% in 2025"],
  "état de durabilité, ESRS S1-16 (écart de rémunération moyen femmes-hommes non corrigé, 2025 ; hors plans d'intéressement à long terme : 34 % selon le rapport)", value=40)
trend(s, "ENV_GHG_TREND", ["TABLE 7 - GHG EMISSIONS (IN TCO 2) (E1-6 AR 48) (MDR-M 77C) 2023 2024 2025 % N / N-1",
                           "Total GHG emissions (market-based) (tCO 2eq) 6,725,476.2 7,731,303.7 +15%"],
      "état de durabilité, ESRS E1-6, émissions totales de GES, scopes 1, 2 et 3 (fondées sur le marché, tCO2e ; deux valeurs publiées, 2024 et 2025, et la variation sur un an)",
      2024, 2025, 7731303.7, 6725476.2)
P(s, "ENV_GHG_INTENSITY", ["Greenhouse gas intensity based on net revenues (E1-6, 53) (MDR-M 77C) UDM 2023 2024 2025 % N / N-1",
                           "Total greenhouse gas emissions (market-based) per net revenue (tCO 2eq/monetary unit) tons of CO2e/€k 2.22 1.95 2.06 +6%"],
  "état de durabilité, ESRS E1-6 (intensité de GES par chiffre d'affaires net, fondée sur le marché, en tCO2e par millier d'euros ; colonnes 2023, 2024, 2025)",
  value=2060, calc="conversion : 2,06 t/k€ × 1 000 = 2 060 t/M€")
P(s, "ENV_SCOPE3_DISCLOSED", ["the Group commits to reducing absolute Scope 3 GHG emissions by 35% within the same timeframe"],
  "état de durabilité, ESRS E1 (émissions de scope 3 publiées par catégorie, tableau 7)", vtype="boolean", boolean="true", norm=1)
J(s, "ENV_TAXONOMY_CAPEX", "non_trouvee", "Rapport annuel 2025 lu (traduction anglaise) : aucun CapEx aligné sur la taxonomie — « because the Group has not identified Taxono - my-aligned activities ».")
