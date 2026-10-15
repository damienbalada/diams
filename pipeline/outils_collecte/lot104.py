"""Lot 104 : groupes américains (10-K, circulaires, rapports de durabilité volontaires) — tous les piliers.
Chaque preuve : citation(s) exacte(s) du rapport, cadre, calcul écrit en toutes lettres.
Les absences lues (« non matériel », publié autrement) vont au journal de relecture."""
import csv, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
S = os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
OUT = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline\curated\groupes_2026-10_lot104_groupes_americains.csv"
JOURNAL = os.path.join(S, "lot104_journal.json")
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

# ---------------------------------------------------------------- Taux d'impôt effectifs (10-K)
P("newell-brands#10k", "TAX_EFFECTIVE_RATE", ["The effective tax rate for 2025 was 5.3% as compared to 16.9% for 2024"],
  "rapport de gestion (taux d'impôt effectif publié, exercice 2025)", value=5.3)
P("general-mills#10k", "TAX_EFFECTIVE_RATE", ["The following table reconciles the United States federal statutory income tax with our effective income tax for fiscal 2026",
                                              "Effective income tax $ 414.3 102.2 %"],
  "comptes consolidés, note sur l'impôt (taux effectif de l'exercice clos le 31/05/2026 ; taux porté par une dépréciation de 1,5 Md$ de l'écart d'acquisition de l'activité Pet en Amérique du Nord, non déductible ; exercice précédent : 20,2 %)", value=102.2)
J("hasbro#10k", "TAX_EFFECTIVE_RATE", "autre_forme", "Rapport annuel 10-K 2025 lu (SEC) : « The effective income tax rate for 2025 was ( 212.1 )% compared to 20.7 % for 2024 » — taux négatif lié à une perte avant impôt, non représentatif.")
J("coty#10k", "TAX_EFFECTIVE_RATE", "autre_forme", "Rapport annuel 10-K de l'exercice clos le 30/06/2026 lu (SEC) : « The 3.3% effective tax rate in fiscal 2026 results from reporting losses before income taxes » — taux calculé sur une perte, non représentatif.")

# ---------------------------------------------------------------- General Mills (rapport de responsabilité 2026, exercice 2025)
s = "general-mills#esg"
trend(s, "ENV_GHG_TREND", ["General Mills GHG emissions by scope (metric tons CO2e) SBTi Target boundary GHG Protocol Scope Fiscal 2025 Fiscal 2020 (baseline)* Fiscal 2025 Fiscal 2020 (baseline)*",
                           "Total*** 10,968,000 12,724,000 15,222,000 17,620,000"],
      "annexe, tableaux de données (émissions totales de GES, scopes 1, 2 et 3, périmètre du GHG Protocol, tCO2e ; colonnes « GHG Protocol Scope » : exercice 2025, exercice 2020 (référence))",
      2020, 2025, 15222000, 17620000)
P(s, "ENV_SCOPE3_DISCLOSED", ["Scope 3 10,613,000 11,931,000 14,866,000 16,827,000"],
  "annexe, tableaux de données (émissions de scope 3, tCO2e ; périmètre SBTi puis GHG Protocol, exercices 2025 et 2020)", vtype="boolean", boolean="true", norm=1)

# ---------------------------------------------------------------- Keurig Dr Pepper (rapport d'impact 2025)
s = "keurig-dr-pepper#esg"
trend_pct(s, "PLA_REDUCTION", ["21% virgin plastic reduction across our packaging portfolio since 2019"],
          "économie circulaire (plastique vierge de l'ensemble des emballages)", 2019, 2025, -21)
P(s, "ENV_SCOPE3_DISCLOSED", ["Scope 3 emissions accounted for more than 97% of KDP’s 2025 GHG emissions"],
  "climat (émissions de scope 3 publiées par catégorie dans le tableau de données)", vtype="boolean", boolean="true", norm=1)
J(s, "WAT_INTENSITY", "autre_forme", "Rapport d'impact 2025 lu : intensité en eau publiée par litre de boisson produite (« Our efforts resulted in a 2.03 water use ratio across all beverage facilities »), sans intensité rapportée au chiffre d'affaires.")

# ---------------------------------------------------------------- Church & Dwight (rapport de durabilité 2025)
s = "church-dwight#esg"
trend(s, "ENV_GHG_TREND", ["SUSTAINABILITY PERFORMANCE DATA INDICATOR UNIT 2025 2024 2023 2022 2021 2020 GRI",
                           "T otal GHG Emissions (Scope 1 + 2 [location-based] + 3 [Excludes indirect emissions]) Metric T ons CO2e",
                           "2,163,791 2,234,403 2,496,123 2,525,582 2,365,765"],
      "tableau des données de performance (émissions totales publiées, scopes 1, 2 fondé sur la localisation et 3, tCO2e ; colonnes 2025 à 2020 ; total 2025 non encore publié, d'où la période 2020-2024)",
      2020, 2024, 2163791, 2365765)
P(s, "ENV_SCOPE3_DISCLOSED", ["Scope 3 GHG Emissions (Excludes indirect emissions) Metric T ons CO2e"],
  "tableau des données de performance (émissions de scope 3, tCO2e, 2021 à 2024)", vtype="boolean", boolean="true", norm=1)
P(s, "PLA_RECYCLED", ["Increased use of post-consumer recycled plastic to an average of approximately 21% across all global plastic packaging"],
  "faits marquants 2025 (part moyenne de plastique recyclé post-consommation dans les emballages plastiques ; objectif de 25 % fin 2025 non atteint)", value=21)
J(s, "PLA_REDUCTION", "autre_forme", "Rapport de durabilité 2025 lu : « Reduced use of virgin plastic across our global packaging portfolio by almost 30% compared to our original baseline level » — ni l'année de référence ni la valeur exacte ne sont précisées.")

# ---------------------------------------------------------------- Stanley Black & Decker (rapport d'impact 2025)
s = "stanley-black-decker#esg"
P(s, "ENV_SCOPE3_DISCLOSED", ["Impact Performance Data Indicators Units Base Year (2022) 2023 2024 2025",
                              "Scope 3—Category 1—Purchased Goods & Services Metric Tons CO2e 10,354,009 7,909,988 8,381,918 7,567,523"],
  "annexe, données de performance (émissions de scope 3 par catégorie, tCO2e ; colonnes 2022 (référence) à 2025)", vtype="boolean", boolean="true", norm=1)
J(s, "ENV_GHG_TREND", "autre_forme", "Rapport d'impact 2025 lu : émissions publiées par scope et par catégorie de scope 3 (achats, transport amont, utilisation des produits vendus), sans total pour l'ensemble des émissions.")
J(s, "WAT_INTENSITY", "autre_forme", "Rapport d'impact 2025 lu : seuls les prélèvements d'eau sont publiés, en gallons (« Water Withdrawals Gallons 505,960,345 505,140,433 508,223,626 »), sans intensité rapportée au chiffre d'affaires.")

# ---------------------------------------------------------------- Brown-Forman (rapport annuel intégré, exercice clos le 30/04/2026)
s = "brown-forman#ars"
P(s, "ENV_SCOPE3_DISCLOSED", ["Reduce Scope 3 by 25% by 2030 from 2023 baseline 35% decrease in fiscal 2025 against a fiscal 2023 baseline"],
  "gestion environnementale (objectifs et avancement : émissions de scope 3 de l'exercice 2025 comparées à l'exercice 2023)", vtype="boolean", boolean="true", norm=1)
J(s, "ENV_GHG_TREND", "autre_forme", "Rapport annuel intégré 2026 lu (SEC, formulaire ARS) : baisses publiées séparément — « Reduce Scope 1 and 2 by 40% by 2030 from 2023 baseline 12% decrease in fiscal 2025 » et scope 3 « 35% decrease in fiscal 2025 against a fiscal 2023 baseline » — sans total des émissions.")
J(s, "PLA_RECYCLED", "autre_forme", "Rapport annuel intégré 2026 lu (SEC, formulaire ARS) : seule la part d'emballages recyclables ou réutilisables est publiée (« 97% recyclable or reusable packaging »), pas la part de matière recyclée.")

# ---------------------------------------------------------------- Kenvue (rapport « Healthy Lives Mission » 2025)
s = "kenvue#esg"
trend_pct(s, "PLA_REDUCTION", ["Virgin plastics reduction Reduced total percentage of virgin plastics by 33% from a 2020 base year, exceeding our goal of 25% by 2025"],
          "faits marquants 2025 (part de plastique vierge dans les emballages)", 2020, 2025, -33)
P(s, "PLA_RECYCLED", ["This resulted in Kenvue’s use of recycled content increasing to 18.5%, up from 8.7%"],
  "économie circulaire (part de contenu recyclé dans les emballages, 2025 ; année précédente : 8,7 %)", value=18.5)
P(s, "ENV_SCOPE3_DISCLOSED", ["Approximately 95% of our total GHG emissions are Scope 3 emissions"],
  "plan de transition climatique (émissions de scope 3 publiées par catégorie)", vtype="boolean", boolean="true", norm=1)

# ---------------------------------------------------------------- Google (rapport environnemental 2026, exercice 2025)
s = "google#esg"
P(s, "ENV_SCOPE3_DISCLOSED", ["In 2025, our total scope 3 (ambition-based) emissions were approximately 11.6 million tCO 2e, representing 80% of our total 2025 carbon footprint"],
  "empreinte carbone (émissions de scope 3, périmètre « ambition-based » ; hausse de 25 % sur un an)", vtype="boolean", boolean="true", norm=1)
