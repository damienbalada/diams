"""Lot 103 : rapports annuels des groupes restants (collecte complète, partie C2) — tous les piliers.
Chaque preuve : citation(s) exacte(s) du rapport, cadre, calcul écrit en toutes lettres.
Les absences lues (« non matériel », publié autrement) vont au journal de relecture."""
import csv, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
S = os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
OUT = r"C:\Users\damie\Downloads\claude\awareness-score\pipeline\curated\groupes_2026-10_lot103_rapports_groupes.csv"
JOURNAL = os.path.join(S, "lot103_journal.json")
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

# ---------------------------------------------------------------- Essity (rapport annuel 2025, version anglaise)
s = "essity"
P(s, "GOV_BOARD_GENDER", ["Four of the AGM-elected Board members are women, corresponding to approximately 44% of the total number of AGM-elected Board members"],
  "rapport sur le gouvernement d'entreprise (part de femmes parmi les administrateurs élus par l'assemblée générale ; hors représentants des salariés)", value=44)
P(s, "LAB_CEO_PAY_RATIO", ["Annual total remuneration ratio of the President and CEO to the median annual total remuneration for all employees (excluding the President and CEO)",
                           "Median total remuneration excluding the President and CEO2) 0.56 Annual Total Remuneration Ratio 76.3"],
  "comptes consolidés, note C2 (ratio de rémunération annuelle totale du directeur général rapportée à la médiane des salariés, exercice 2025)", value=76.3)
P(s, "LAB_GENDER_PAYGAP", ["Remuneration metrics (S1-16) Gender pay gap % 2025 2024 Women/Men 4 6",
                           "The gender pay gap is calculated on the basis of average hourly pay"],
  "sustainability statements, ESRS S1-16 (écart de rémunération femmes-hommes, sur le salaire horaire moyen ; colonnes 2025, 2024)", value=4)
trend(s, "ENV_GHG_TREND", ["Total Scope 1, 2 and 3 GHG emissions, kton CO2e 2025 2024 2016",
                           "Total Scope 1, 2 and 3 GHG emissions (market-based) 9,093 9,071 10,439"],
      "sustainability statements, ESRS E1-6, émissions totales de GES, scopes 1, 2 et 3 (fondées sur le marché, kt CO2e ; colonnes 2025, 2024, 2016 (référence))",
      2016, 2025, 9093, 10439)
P(s, "ENV_SCOPE3_DISCLOSED", ["Total Scope 3 GHG emissions 6,737 6,635 7,082"],
  "sustainability statements, ESRS E1-6 (émissions de scope 3, kt CO2e ; colonnes 2025, 2024, 2016)", vtype="boolean", boolean="true", norm=1)
P(s, "TAX_EFFECTIVE_RATE", ["The tax expense was SEK 4,443m (4,331), corresponding to a tax rate of 25.9% (26.5)"],
  "rapport de gestion (charge d'impôt rapportée au résultat avant impôt, exercice 2025 ; entre parenthèses : 2024)", value=25.9)
P(s, "WAT_INTENSITY", ["Water intensity, defined as water consumption divided by net revenue, was 678 m³ per EURm"],
  "sustainability statements, ESRS E3-4 (intensité hydrique réglementaire : consommation d'eau rapportée au chiffre d'affaires, 2025)", value=678)
P(s, "PLA_RECYCLED", ["Packaging data1) 2025 2024 2023 2022",
                      "of which, recycled materials in plastic packaging 19 16 10 10"],
  "sustainability statements, ESRS E5 (part de matière recyclée dans les emballages plastiques des marques du groupe, % ; colonnes 2025 à 2022)", value=19)
J(s, "ENV_TAXONOMY_CAPEX", "non_trouvee", "Rapport annuel 2025 lu : aucun CapEx aligné sur la taxonomie — tableau réglementaire, ligne « CapEx2) 8,143 0 0 0 … » ; le rapport précise que les critères techniques de l'industrie papetière (NACE C17.22) ne sont pas encore définis par l'UE.")
J(s, "LAB_LIVING_WAGE", "absence_confirmee", "Rapport annuel 2025 lu : la table des exigences ESRS indique « S1-10 Adequate wages Not material » ; la donnée n'est pas publiée.")
J(s, "GOV_BOARD_INDEP", "autre_forme", "Rapport annuel 2025 lu : l'indépendance est indiquée administrateur par administrateur (« Independent of the company, corporate management and Essity’s major shareholders »), sans part globale pour le conseil.")
J(s, "ENV_GHG_INTENSITY", "autre_forme", "Rapport annuel 2025 lu : intensité publiée par chiffre d'affaires en couronnes suédoises — « GHG emissions intensity, market-based (total GHG emissions per net revenue), ton/kSEK 65.7 62.3 » ; l'unité publiée (tonnes par millier de couronnes) ne concorde pas avec les totaux publiés, la valeur n'est pas reprise.")

# ---------------------------------------------------------------- Richemont (exercice clos le 31/03/2026)
s = "richemont#nfr"
P(s, "ENV_GHG_INTENSITY", ["Group emissions intensity – market-based (ktCO 2e/€m sales) 0.10 0.07* 0.06"],
  "section environnement, GRI 305-4 (intensité des émissions de GES, scopes 1, 2 et 3 fondées sur le marché, par million d'euros de ventes ; colonnes CY2019 (référence), FY25, FY26 ; valeur publiée arrondie au centième)",
  value=60, calc="conversion : 0,06 kt/M€ × 1 000 = 60 t/M€")
P(s, "ENV_SCOPE3_DISCLOSED", ["Total GHG Emissions by Scope ktCO2e Base Year CY19** FY25 FY26", "Scope 3 1 123.9* 1 412.6* 1 364.8"],
  "section environnement, GRI 305-3 (émissions de scope 3, kt CO2e ; colonnes CY2019, FY25, FY26)", vtype="boolean", boolean="true", norm=1)

# ---------------------------------------------------------------- Puig
s = "puig#nfr"
P(s, "GOV_BOARD_GENDER", ["Gender of the members of the Board of Directors Female 30.8% Male 69.2%"],
  "informations générales (composition du conseil d'administration au 31/12/2025)", value=30.8)
P(s, "GOV_BOARD_INDEP", ["a number of independent directors representing 46.15% over its total members"],
  "informations générales (part d'administrateurs indépendants au conseil)", value=46.15, norm=0.4615)
P(s, "LAB_CEO_PAY_RATIO", ["Remuneration metrics 2024 2025 Gender wage gap. 24.7% 24.9% The annual total remuneration ratio of the highest paid individual to the median annual total remuneration for all employees (excluding the highest-paid individual). 230 122"],
  "état de durabilité, ESRS S1-16 (ratio de rémunération annuelle totale de la personne la mieux payée à la médiane des salariés ; colonnes 2024, 2025 ; hors Charlotte Tilbury en 2025)", value=122)
P(s, "LAB_GENDER_PAYGAP", ["Remuneration metrics 2024 2025 Gender wage gap. 24.7% 24.9%"],
  "état de durabilité, ESRS S1-16 (écart de rémunération femmes-hommes non corrigé ; colonnes 2024, 2025 ; à poste, ancienneté et pays égaux, l'écart publié est de −1,3 % en 2025)", value=24.9)
J(s, "ENV_GHG_TREND", "autre_forme", "État d'information non financière 2025 lu : émissions totales publiées pour 2024 et 2025 seulement (« Total GHG emissions (market-based) (tCO2eq) 565,710 564,286 (0.3%) ») ; une baisse sur un an ne suffit pas à établir une trajectoire (deux ans au moins).")
P(s, "ENV_GHG_INTENSITY", ["GHG Intensity per net revenue Intensity calculated: tCO2e/€M* 2024 2025 2025/2024",
                           "Intensity Scope 1,2,3 (market-based) 118.1 111.9 (5%)"],
  "état de durabilité, ESRS E1-6 (intensité de GES par chiffre d'affaires net, scopes 1, 2 et 3 fondées sur le marché ; colonnes 2024, 2025)", value=111.9)
P(s, "ENV_SCOPE3_DISCLOSED", ["Total Gross indirect (Scope 3) GHG emissions (tCO2eq) 561,281 559,282 (0.4%)"],
  "état de durabilité, ESRS E1-6 (émissions de scope 3, tCO2e ; colonnes 2024, 2025)", vtype="boolean", boolean="true", norm=1)
J(s, "ENV_TAXONOMY_CAPEX", "non_trouvee", "État d'information non financière 2025 lu : aucun CapEx aligné sur la taxonomie — tableau réglementaire, ligne « CapEx of environmentally sustainable activities (Taxonomy-aligned) (A.1) 0.00 0% ».")
J(s, "WAT_INTENSITY", "autre_forme", "État d'information non financière 2025 lu : seuls les prélèvements d'eau des usines sont publiés (« Water Withdrawal Performance25 2024 2025 2025/2024 Total 151,690.21 168,752.34 11% »), sans intensité rapportée au chiffre d'affaires.")
J(s, "PLA_RECYCLED", "autre_forme", "État d'information non financière 2025 lu : part de matière recyclée publiée pour les seuls emballages de parfums (« an average of 12% of the materials used in Puig’s fragrances packaging are post-consumer recycled (PCR) »), sans taux pour l'ensemble des emballages.")
s = "puig"
P(s, "TAX_EFFECTIVE_RATE", ["(Thousand euros) 2025 2024 Profit before taxes 819,804 692,506",
                            "Corporate income tax income / (expense) (202,702) (149,973) Effective tax rate 24.7% 21.7%"],
  "comptes consolidés, note sur l'impôt (taux effectif ; colonnes 2025, 2024)", value=24.7)

# ---------------------------------------------------------------- Beiersdorf
s = "beiersdorf"
P(s, "LAB_CEO_PAY_RATIO", ["Ratio of the Remuneration of the Highest-Paid Individual to the Median Remuneration of All Employees Consumer tesa Group 132.54 108.55 125.83"],
  "sustainability statement, ESRS S1-16 (ratio de la rémunération cible de la personne la mieux payée à la médiane des salariés ; colonnes Consumer, tesa, groupe ; 2025)", value=125.83)
P(s, "ENV_TAXONOMY_CAPEX", ["Total Proportion of Taxonomy eligible activities Taxonomy aligned activities Proportion of Taxonomy aligned activities",
                            "CapEx 520,789 31.1% 12,283 2.4% 2.4%"],
  "taxonomie verte de l'UE (règlement 2020/852, art. 8), tableau réglementaire des CapEx (total en k€, part éligible, montant aligné en k€, part alignée ; activité alignée : acquisition et détention de bâtiments)",
  value=2.4, text="2,4 %", norm=0.024)
trend_pct(s, "PLA_REDUCTION", ["Reduction of Virgin-Based Fossil Plastic Target By 2025, the volume of virgin fossil-based plastic in our packaging is to be reduced by 50% compared to 2019",
                               "total reduction from 2019 to 2025: 37%; we therefore did not achieve our target"],
          "sustainability statement, ESRS E5 (plastique fossile vierge des emballages, secteur Consumer ; objectif de −50 % non atteint)", 2019, 2025, -37)
P(s, "PLA_RECYCLED", ["Recycled Material in Our Plastic Packaging Target By 2025, our plastic packaging was to consist of 30% recycled material",
                      "30% recycled material in 2025; target achieved"],
  "sustainability statement, ESRS E5 (part de matière recyclée dans les emballages plastiques, secteur Consumer, 2025)", value=30)
J(s, "WAT_INTENSITY", "autre_forme", "Rapport annuel 2025 lu : intensité en eau publiée par volume produit (« In 2025, water consumption per product manufactured was reduced by 8% compared to the base year to 464 liters/1,000 products »), sans intensité rapportée au chiffre d'affaires.")

# ---------------------------------------------------------------- LDC (exercice clos le 28/02/2026 ; données environnementales de l'année civile 2025)
s = "ldc"
P(s, "LAB_CEO_PAY_RATIO", ["Sur l’exercice 2025-2026, en France, le ratio de la rémunération totale annuelle de la personne la mieux payée par rapport à la rémunération totale médiane de tous les employés présents sur l’ensemble de l’année et à temps plein est de 18,1 contre 19,3 en 2024-2025"],
  "état de durabilité, ESRS S1-16 (ratio de rémunération de la personne la mieux payée à la médiane, périmètre France)", value=18.1)
P(s, "LAB_GENDER_PAYGAP", ["Écart de rémunération entre les femmes et les hommes 2025-2026 2024-2025 France Pologne Hongrie Pays de Galles Allemagne France Pologne Hongrie Ecart de rémunération entre les hommes et les femmes (%) * 9% 16% 12% 1% 18% 11% 21% 25%"],
  "état de durabilité, ESRS S1-16 (écart de rémunération femmes-hommes publié par pays ; valeur retenue : France, 2025-2026 ; Pologne 16 %, Hongrie 12 %, pays de Galles 1 %, Allemagne 18 %)", value=9)
trend(s, "ENV_GHG_TREND", ["Émissions de gaz à effet de serre Baseline 2024 Baseline 2024 2025 Comparatif 2025-2024 Objectif 2030",
                           "Émissions totales de GES scope1, 2 et 3 fondées sur le marché NC 6 289 154 6 637 762 5,5%"],
      "état de durabilité, ESRS E1-6, émissions totales de GES, scopes 1, 2 et 3 (fondées sur le marché, tCO2e ; colonnes 2024 publié, 2024 recalculé, 2025 au nouveau périmètre) ; "
      "la hausse inclut les acquisitions de l'exercice", 2024, 2025, 6637762, 6289154)
P(s, "ENV_GHG_INTENSITY", ["Intensité des GES par produit net 2024initial 2024 recalculé 2025 Comparaison 2024-2025",
                           "Émissions totales de GES fondées sur le marché par produit net Non publié 1,00 0,92 -8%"],
  "état de durabilité, ESRS E1-6 (intensité de GES, scopes 1, 2 et 3 fondées sur le marché, en tCO2e par millier d'euros de chiffre d'affaires net ; colonnes 2024 publié, 2024 recalculé, 2025)",
  value=920, calc="conversion : 0,92 t/k€ × 1 000 = 920 t/M€")
P(s, "ENV_SCOPE3_DISCLOSED", ["soit 84 % des émissions de scope 3 de l’ensemble du Groupe et de sa chaîne de valeur au cours de l’année de référence 2024 recalculée"],
  "état de durabilité, ESRS E1-6 (émissions de scope 3 publiées par poste ; objectif de −21 % par tonne vendue entre 2024 et 2030)", vtype="boolean", boolean="true", norm=1)
P(s, "WAT_INTENSITY", ["Intensité hydrique sur prélèvement (m3/M€ de CA) 1 930 1699",
                       "Intensité hydrique (m3/M€ de CA) ND 228"],
  "état de durabilité, ESRS E3-4 (intensité hydrique réglementaire : consommation d'eau rapportée au chiffre d'affaires ; colonnes 2024, 2025 ; sur les prélèvements : 1 699 m³/M€)", value=228)
J(s, "ENV_TAXONOMY_CAPEX", "non_trouvee", "Rapport annuel 2025-2026 lu : aucun CapEx aligné sur la taxonomie — « Le Groupe LDC ne présente pas de CapEx aligné au sens de la Taxonomie en 2025-2026 contrairement aux 4% générés en 2024-2025 ».")
J(s, "LAB_LIVING_WAGE", "autre_forme", "Rapport annuel 2025-2026 lu : « En matière de salaires décents, le Groupe s’appuie dans les pays européens où il est présent, sur les salaires minima légaux en vigueur » — référence au salaire minimum légal, pas d'engagement de salaire décent vérifié.")

# ---------------------------------------------------------------- Lanson-BCC (DEU 2025 : pas d'état de durabilité ESRS, tableau RSE volontaire)
s = "lanson-bcc"
J(s, "LAB_CEO_PAY_RATIO", "autre_forme", "Document d'enregistrement universel 2025 lu : seul un « ratio d’équité complémentaire » au SMIC est publié (« 388 700 / 21 876,36 : 17,77 »), sans ratio à la rémunération médiane des salariés.")
J(s, "SUP_VIGILANCE_PLAN", "autre_forme", "Document d'enregistrement universel 2025 lu : la table de concordance indique « Plan de vigilance élaboré par les sociétés mères en application de leur devoir de vigilance n/a » — la société ne s'estime pas soumise au devoir de vigilance.")
for code in ("LAB_GENDER_PAYGAP", "ENV_GHG_TREND", "ENV_GHG_INTENSITY", "ENV_SCOPE3_DISCLOSED", "ENV_TAXONOMY_CAPEX", "PLA_REDUCTION", "PLA_RECYCLED", "WAT_INTENSITY", "LAB_LIVING_WAGE"):
    J(s, code, "non_trouvee", "Rapport lu (document d'enregistrement universel 2025, déposé à l'AMF) : pas d'état de durabilité ; le tableau RSE volontaire ne publie pas cette donnée (indicateurs publiés : consommation d'énergie par rapport à 2021, allègement des bouteilles, origine des approvisionnements).")

# ---------------------------------------------------------------- Groupes américains : circulaires de procuration 2026 (SEC, DEF 14A)
J("amazon#proxy", "GOV_BOARD_GENDER", "autre_forme", "Circulaire de procuration 2026 lue (SEC) : seule la composition des administrateurs indépendants est chiffrée (« of our nine independent director nominees, four are women ») ; onze candidats au total, sans part globale publiée.")
for k in ("newell-brands", "hasbro", "kenvue", "brown-forman", "keurig-dr-pepper", "3m", "church-dwight", "spectrum-brands", "google"):
    J(k + "#proxy", "GOV_BOARD_GENDER", "non_trouvee", "Rapport lu (circulaire de procuration 2026 déposée à la SEC, formulaire DEF 14A) : aucune part de femmes au conseil écrite en toutes lettres ; la composition n'est donnée qu'en graphique ou administrateur par administrateur.")
