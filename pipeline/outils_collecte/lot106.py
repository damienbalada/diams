"""Lot 106 : groupes non cotés et étrangers restants (Schwarz, Castel, Intersnack, VTech, Euralis) — tous les piliers.
Chaque preuve : citation(s) exacte(s) du rapport, cadre, calcul écrit en toutes lettres.
Les absences lues (« non matériel », publié autrement) vont au journal de relecture."""
import csv, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
S = os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
OUT = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline\curated\groupes_2026-10_lot106_groupes_restants.csv"
JOURNAL = os.path.join(S, "lot106_journal.json")
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

# ---------------------------------------------------------------- Groupe Schwarz (Lidl, Kaufland) — exercice 2025 (01/03/2025 – 28/02/2026)
s = "schwarz-gruppe#kz"
P(s, "PLA_RECYCLED", ["REset Plastic: Zielerreichung GJ 2025 26,1 % Bis 2025 werden Lidl und Kauf- land durchschnittlich 25 Prozent Rezyklat in ihren aus Plastik bestehenden Eigenmarken- primärverpackungen einsetzen"],
  "économie circulaire (part de matière recyclée dans les emballages primaires en plastique des marques propres de Lidl et Kaufland, exercice 2025 ; objectif : 25 %)", value=26.1)
s = "schwarz-gruppe"
J(s, "PLA_REDUCTION", "autre_forme", "Rapport de durabilité de l'exercice 2025 lu : réduction publiée pour l'ensemble du plastique, vierge et recyclé (« 35,7 % ✓ weniger Plastik in Eigenmarkenverpackungen und Transporthilfen aus Plastik (im Vergleich zum Basisjahr 2017) »), pas pour le seul plastique vierge.")
J(s, "ENV_GHG_TREND", "autre_forme", "Rapport de durabilité et brochure des chiffres clés de l'exercice 2025 lus : objectifs de réduction publiés par scope (« SCOPE 1 & 2 betriebsbedingte Emissionen1 -48 % » d'ici 2030), sans total des émissions de l'exercice.")

# ---------------------------------------------------------------- Castel (rapport de durabilité de Castel-Vins, exercice 2025)
s = "castel-freres"
P(s, "ENV_SCOPE3_DISCLOSED", ["SCOPE 3 NON-FLAG SCOPE 3 FLAG SCOPE 1& 2", "•EMBALLAGES : 95 998 T"],
  "environnement, empreinte carbone de Castel-Vins (émissions publiées par poste, scope 3 compris, en tCO2e ; année 2024)", vtype="boolean", boolean="true", norm=1)
J(s, "WAT_INTENSITY", "autre_forme", "Rapport de durabilité de Castel-Vins lu : intensité en eau publiée par volume de vin (« 1 ,23 Hl eau nécessaire par Hl de vin »), sans intensité rapportée au chiffre d'affaires.")
J(s, "GOV_BOARD_GENDER", "autre_forme", "Rapport de durabilité de Castel-Vins lu : seule la part de femmes parmi les cadres permanents est publiée (« PART DE FEMMES DANS L'EFFECTIF CADRE PERMANENT 28,66 2 9,13 27 ,63 »), pas la composition du conseil.")

# ---------------------------------------------------------------- Intersnack (rapport d'avancement 2025 du groupe)
s = "intersnack-france"
P(s, "ENV_SCOPE3_DISCLOSED", ["Progress against our environment targets 2022 2023 2024 2025",
                              "30% reduction in Scope 3 tCO2e emissions of categories in SBTi target scope by 2032 versus 20212 -3.8% -4.3% -5.2% -13.0%"],
  "environnement, rapport du groupe Intersnack (maison mère d'Intersnack France) : émissions de scope 3 suivies par rapport à 2021", vtype="boolean", boolean="true", norm=1)
J(s, "ENV_GHG_TREND", "autre_forme", "Rapport d'avancement 2025 du groupe Intersnack lu : évolutions publiées séparément pour les scopes 1 et 2 (« -8.4% » en 2025 par rapport à 2021) et pour le scope 3 (« -13.0% »), sans total des émissions.")

# ---------------------------------------------------------------- VTech (rapport de durabilité de l'exercice 2026, groupe VTech Holdings)
s = "vtech-electronics-europe"
P(s, "ENV_SCOPE3_DISCLOSED", ["The total amount of Scope 3 emissions in FY2026 was 829,559 tonnes of CO2e"],
  "environnement, rapport du groupe VTech Holdings (maison mère de VTech Electronics Europe) : émissions de scope 3 de l'exercice clos le 31/03/2026", vtype="boolean", boolean="true", norm=1)
J(s, "WAT_INTENSITY", "autre_forme", "Rapport de durabilité de l'exercice 2026 du groupe VTech lu : seule l'évolution est publiée (« Compared with FY2025, total water consumption per revenue decreased by 10.1% »), sans valeur de l'intensité.")
J(s, "ENV_GHG_INTENSITY", "autre_forme", "Rapport de durabilité de l'exercice 2026 du groupe VTech lu : seule l'évolution est publiée (« Compared with FY2025, total Scope 1 and 2 GHG emission per revenue reduced by 2.5% »), sans valeur de l'intensité.")

# ---------------------------------------------------------------- Euralis (déclaration de performance extra-financière 2024-2025)
for code in ("GOV_BOARD_GENDER", "GOV_BOARD_INDEP", "LAB_CEO_PAY_RATIO", "LAB_GENDER_PAYGAP", "ENV_GHG_TREND", "ENV_GHG_INTENSITY",
             "ENV_SCOPE3_DISCLOSED", "TAX_EFFECTIVE_RATE", "SUP_VIGILANCE_PLAN", "ENV_TAXONOMY_CAPEX", "PLA_REDUCTION", "PLA_RECYCLED",
             "WAT_INTENSITY", "LAB_LIVING_WAGE"):
    J("euralis", code, "non_trouvee", "Rapport lu (déclaration de performance extra-financière 2024-2025 d'Euralis) : la donnée n'y figure pas sous forme chiffrée lisible (bilan carbone présenté en graphique).")
