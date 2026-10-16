"""Vérification déterministe des preuves curées (BOCC, HATVP)."""
from diams.load import EvidenceRow
from diams.verify_curated import check_hatvp, parse_bocc_text, verify_bocc

BOCC_TEXT = """
Financing to Upstream Oil & Gas Expansion
Companies (Exploration & Production)
28 Société Générale $6.1 $4.1 $1.1 $2.0 $2.6 $15.8 +$0.6 B 29.0%
64 Crédit Mutuel $0.0 $0.0 $0.0 $0.0 $0.0 $0.0 - -
Financing to Midstream Oil & Gas Expansion Companies (Pipelines and LNG Infrastructure)
23 Société
Générale
$5.7 $3.5 $2.3 $2.1 $4.2 $17.8 +$2.0 B 95%
64 Crédit Mutuel $0.0 $0.0 $0.1 $0.0 $0.0 $0.2 - -
Financing to Gas Power Expansion Companies
28 Société
Générale
$3.7 $0.9 $0.7 $1.3 $2.6 $9.2 +$1.3 B 101%
61 Crédit Mutuel $0.1 $0.0 $0.1 $0.0 $0.0 $0.2 +$0.0 B 93%
"""


def row(slug, value, excerpt, **kw):
    return EvidenceRow(entity_slug=slug, indicator_code=kw.get("ind", "INV_FOSSIL_FINANCING"),
                       source_code=kw.get("src", "BOCC"), nature="result", observed_on="2026-06-09",
                       value_type="numeric", value_numeric=value, excerpt=excerpt,
                       source_url=kw.get("url", "https://example.org"), reviewer="ai:test")


def test_tableaux_bocc_lus_meme_avec_noms_coupes():
    t = parse_bocc_text(BOCC_TEXT)
    assert t["Upstream"]["societe generale"][4] == 2.6
    assert t["Midstream"]["societe generale"][4] == 4.2
    assert t["Gas Power"]["societe generale"][4] == 2.6


def test_bocc_concorde():
    ex = "… (amont 2,6 + transport/GNL 4,2 + centrales à gaz 2,6, valeurs arrondies)."
    assert verify_bocc(row("societe-generale", 9.4, ex), parse_bocc_text(BOCC_TEXT)).status == "OK"


def test_bocc_ecart_si_total_ou_composante_differe():
    t = parse_bocc_text(BOCC_TEXT)
    ex = "(amont 2,6 + transport/GNL 4,2 + centrales à gaz 2,6)"
    assert verify_bocc(row("societe-generale", 9.5, ex), t).status == "ÉCART"
    assert verify_bocc(row("societe-generale", 9.4, ex.replace("4,2", "4,1")), t).status == "ÉCART"


def test_bocc_perimetre_plus_large_que_l_entite_reste_humain():
    ex = "(amont 0,0 + transport/GNL 0,0 + centrales à gaz 0,0)"
    assert verify_bocc(row("credit-mutuel-alliance-federale", 0.0, ex), parse_bocc_text(BOCC_TEXT)).status == "JUGEMENT"


RECORD = {
    "publicationCourante": {"denomination": "BNP PARIBAS", "identifiantNational": "662042449",
                            "datePremierePublication": "23/11/2017 12:59:42"},
    "exercices": [
        {"publicationCourante": {"dateDebut": "01-01-2025", "montantDepense": "> = 500 000 euros et < 600 000 euros", "nombreActivite": 5}},
        {"publicationCourante": {"dateDebut": "01-01-2024", "noActivite": True, "nombreActivite": 0}},
    ],
}
HATVP_EX = "Inscrite depuis le 23/11/2017 ; dépenses de lobbying déclarées pour 2025 : 500 000 à 600 000 €."


def test_hatvp_concorde():
    r = row("bnp-paribas", None, HATVP_EX, ind="GEO_LOBBYING_TRANSP", src="HATVP")
    assert check_hatvp(r, RECORD, "662042449").status == "OK"


def test_hatvp_ecart_sur_date_ou_montant():
    r = row("bnp-paribas", None, HATVP_EX.replace("23/11", "24/11"), ind="GEO_LOBBYING_TRANSP", src="HATVP")
    assert check_hatvp(r, RECORD, "662042449").status == "ÉCART"
    r = row("bnp-paribas", None, HATVP_EX.replace("500 000 à 600 000", "400 000 à 500 000"), ind="GEO_LOBBYING_TRANSP", src="HATVP")
    assert check_hatvp(r, RECORD, "662042449").status == "ÉCART"


def test_hatvp_fiche_d_une_autre_entite_reste_humaine():
    r = row("credit-mutuel-alliance-federale", None, HATVP_EX, ind="GEO_LOBBYING_TRANSP", src="HATVP")
    assert check_hatvp(r, RECORD, "588505354").status == "JUGEMENT"


REPORT = ("… 3.1.3.7 Indicateurs de rémunération L’écart de rémunération entre les femmes et les hommes au sein de "
          "Crédit Agricole S.A. est de 31,68 % en 2025. Intensité de GES - basée sur le marché 2 773,87 tonnes éqCO₂/M€ …")


def esef_row(ind, value, quote):
    return row("x", value, f"Rapport financier annuel 2025 (ESEF) : « {quote} »", ind=ind, src="ESEF")


def test_esef_citation_verbatim_valeur_et_indicateur():
    from diams.verify_curated import check_esef_quote
    q = "L'écart de rémunération entre les femmes et les hommes au sein de Crédit Agricole S.A. est de 31,68 % en 2025"
    assert check_esef_quote(esef_row("LAB_GENDER_PAYGAP", 31.68, q), REPORT).status == "OK"
    q2 = "Intensité de GES - basée sur le marché 2 773,87 tonnes éqCO₂/M€"
    # deux colonnes côte à côte (2025, 2024) ne fusionnent pas en un seul nombre
    report = REPORT + " Ratio entre la rémunération la plus élevée et la rémunération médiane des salariés 44,61 48,60"
    q3 = "Ratio entre la rémunération la plus élevée et la rémunération médiane des salariés 44,61 48,60"
    assert check_esef_quote(esef_row("LAB_CEO_PAY_RATIO", 44.61, q3), report).status == "OK"
    assert check_esef_quote(esef_row("ENV_GHG_INTENSITY", 2773.87, q2), REPORT).status == "OK"


def test_signe_moins_typographique():
    from diams.verify_curated import check_esef_quote
    rep = "The ↗ Gender Pay Gap was –9.9% (2024:–10.1%)."
    q = "The ↗ Gender Pay Gap was –9.9%"
    assert check_esef_quote(esef_row("LAB_GENDER_PAYGAP", -9.9, q), rep).status == "OK"
    assert check_esef_quote(esef_row("LAB_GENDER_PAYGAP", 9.9, q), rep).status == "ÉCART"
    rep2 = "Mr. Jassy’s compensation was $2,069,861, resulting in a ratio of those amounts of 1-to-51."
    q2 = "resulting in a ratio of those amounts of 1-to-51"
    assert check_esef_quote(esef_row("LAB_CEO_PAY_RATIO", 51, q2 + " » ; « median"), rep2 + " median").status == "OK"


def test_ecart_en_faveur_des_femmes_compte_negatif():
    from diams.verify_curated import check_esef_quote
    rep = "In 2025 , the total gender pay gap at HEINEKEN was 30.1% ( 2024 : 28.4%) in favour of women. The"
    q = "In 2025 , the total gender pay gap at HEINEKEN was 30.1% ( 2024 : 28.4%) in favour of women"
    assert check_esef_quote(esef_row("LAB_GENDER_PAYGAP", -30.1, q), rep).status == "OK"
    q2 = "In 2025 , the total gender pay gap at HEINEKEN was 30.1%"
    assert check_esef_quote(esef_row("LAB_GENDER_PAYGAP", -30.1, q2), rep).status == "ÉCART"  # sens non dit
    rep3 = ("Écart de rémunération entre les femmes et les hommes selon la méthodologie de la CSRD (a) Non publié "
            "(8,0) % (a) Ce tableau montre que la rémunération totale est en moyenne 8,0% supérieur pour les "
            "salariées femmes que pour les salariés hommes.")
    q3 = ("Écart de rémunération entre les femmes et les hommes selon la méthodologie de la CSRD » ; « la "
          "rémunération totale est en moyenne 8,0% supérieur pour les salariées femmes que pour les salariés hommes")
    assert check_esef_quote(esef_row("LAB_GENDER_PAYGAP", -8.0, q3), rep3).status == "OK"
    q4 = "Écart de rémunération entre les femmes et les hommes selon la méthodologie de la CSRD (a) Non publié (8,0) %"
    assert check_esef_quote(esef_row("LAB_GENDER_PAYGAP", -8.0, q4), rep3).status == "OK"  # notation comptable
    assert check_esef_quote(esef_row("LAB_GENDER_PAYGAP", 8.0, q4), rep3).status == "ÉCART"


def test_pourcentage_tire_des_effectifs_cites():
    from diams.verify_curated import check_esef_quote
    rep = "Key elements of our Board independence include: • 11 of 12 director nominees are independent • All"
    q = "11 of 12 director nominees are independent"
    assert check_esef_quote(esef_row("GOV_BOARD_INDEP", 91.7, q), rep).status == "OK"
    assert check_esef_quote(esef_row("GOV_BOARD_INDEP", 92.0, q), rep).status == "ÉCART"
    rep2 = "Le Conseil d’Administration d’ENGIE comprend six femmes Administratrices sur 14 membres."
    q2 = "Conseil d’Administration d’ENGIE comprend six femmes Administratrices sur 14 membres"
    assert check_esef_quote(esef_row("GOV_BOARD_GENDER", 42.9, q2), rep2).status == "OK"


def test_nombres_en_notation_anglaise():
    from diams.verify_curated import check_esef_quote
    report = "For 2025, the ratio of the annual total compensation of our CEO to the median employee was 1,980 to 1."
    q = "the ratio of the annual total compensation of our CEO to the median employee was 1,980 to 1"
    assert check_esef_quote(esef_row("LAB_CEO_PAY_RATIO", 1980, q), report).status == "OK"
    report2 = "Our median employee pay ratio was 533.2:1 in 2025"
    assert check_esef_quote(esef_row("LAB_CEO_PAY_RATIO", 533.2, "median employee pay ratio was 533.2:1"), report2).status == "OK"


def test_plusieurs_citations_toutes_verifiees():
    from diams.verify_curated import check_esef_quote
    report = "3.2 Plan de vigilance 3.2.7 Dispositif de suivi des mesures. Ailleurs : une cartographie des risques achats."
    ok = esef_row("SUP_VIGILANCE_PLAN", None, "3.2 Plan de vigilance 3.2.7 Dispositif de suivi des mesures » et « une cartographie des risques achats")
    assert check_esef_quote(ok, report).status == "OK"
    ko = esef_row("SUP_VIGILANCE_PLAN", None, "3.2 Plan de vigilance 3.2.7 Dispositif de suivi des mesures » et « une cartographie inventée")
    assert check_esef_quote(ko, report).status == "ÉCART"


def test_esef_colonnes_voisines_de_trois_chiffres():
    from diams.verify_curated import check_esef_quote
    report = "Intensité des GES par chiffre d’affaires net tCO 2 e/M€ 345 352 2 Suite"
    q = "Intensité des GES par chiffre d’affaires net tCO 2 e/M€ 345 352"
    assert check_esef_quote(esef_row("ENV_GHG_INTENSITY", 352, q), report).status == "OK"
    assert check_esef_quote(esef_row("ENV_GHG_INTENSITY", 353, q), report).status == "ÉCART"


def test_esef_ecart_si_citation_absente_valeur_differente_ou_hors_sujet():
    from diams.verify_curated import check_esef_quote
    q = "L'écart de rémunération entre les femmes et les hommes au sein de Crédit Agricole S.A. est de 31,68 % en 2025"
    assert check_esef_quote(esef_row("LAB_GENDER_PAYGAP", 31.7, q), REPORT).status == "ÉCART"
    assert check_esef_quote(esef_row("LAB_GENDER_PAYGAP", 31.68, q.replace("31,68", "30,68")), REPORT).status == "ÉCART"
    assert check_esef_quote(esef_row("GOV_BOARD_INDEP", 31.68, q), REPORT).status == "ÉCART"


def test_hatvp_fiche_vide_est_un_ecart():
    r = row("la-nef", None, "Inscrite.", ind="GEO_LOBBYING_TRANSP", src="HATVP")
    assert check_hatvp(r, {"publicationCourante": {}, "exercices": []}, "339799116").status == "ÉCART"


def test_seul_un_ok_de_tier_1_2_sans_note_est_approuvable():
    from diams.verify_curated import Verdict, finalize
    ok = Verdict("OK", [])
    assert finalize(ok, "", "regulatory").status == "OK"
    assert finalize(ok, "", "audited_ngo").status == "OK"
    assert finalize(ok, "", "press").status == "JUGEMENT"      # rapport d'entreprise, presse
    assert finalize(ok, "", None).status == "JUGEMENT"         # tier inconnu : prudence
    assert finalize(ok, "définition voisine", "regulatory").status == "JUGEMENT"
    assert finalize(Verdict("ÉCART", []), "", "regulatory").status == "ÉCART"


def test_conversion_de_devise_au_taux_bce():
    from diams.verify_curated import check_esef_quote
    rep = ("GHG intensity per net revenue 1 (tonnes CO2e/SEK m) 2025 2024 2023 2019 Comparison … "
           "Total GHG emissions (market–based) per net revenue 30 33 32 44 –10.1 –31.7 1. Net revenue")
    q = ("GHG intensity per net revenue 1 (tonnes CO2e/SEK m) 2025 2024 2023 2019 » ; « "
         "Total GHG emissions (market–based) per net revenue 30 33 32 44")
    conv = " ; converti au taux de change annuel moyen 2025 de la BCE (1 € = 11,0663 SEK) : 30 × 11,0663 = 332"
    r = row("x", 332, f"Rapport annuel 2025 (t CO2e par million de couronnes) : « {q} »{conv}",
            ind="ENV_GHG_INTENSITY", src="ANNUAL_REPORT")
    rates = {("SEK", "2025"): 11.0663058823529}
    assert check_esef_quote(r, rep, rates=rates).status == "OK"
    assert check_esef_quote(r, rep, rates={("SEK", "2025"): 11.4325}).status == "ÉCART"  # mauvais taux
    assert check_esef_quote(r, rep, rates={}).status == "ÉCART"                            # taux non vérifié
    r2 = row("x", 340, f"Rapport annuel 2025 : « {q} »{conv.replace('= 332', '= 340')}",
             ind="ENV_GHG_INTENSITY", src="ANNUAL_REPORT")
    assert check_esef_quote(r2, rep, rates=rates).status == "ÉCART"                       # calcul faux


def test_rythme_annuel_des_emissions_recalcule():
    from diams.verify_curated import check_esef_quote, trend_score
    rep = ("Total GHG emissions (market–based) (tCO 2e) 6,855,000 7,831,000 7,548,000 10,227,000 –12.5 –33 "
           "1. For Scope 3 emissions")
    q = "Total GHG emissions (market–based) (tCO 2e) 6,855,000 7,831,000 7,548,000 10,227,000"
    calc = " ; rythme annuel moyen (2019 → 2025, 6 ans) : (6855000 / 10227000)^(1/6) − 1 = −6,45 %"
    def r(value, norm, c=calc):
        x = row("x", value, f"Rapport 2025 (colonnes 2025, 2024, 2023, 2019) : « {q} »{c}",
                ind="ENV_GHG_TREND", src="ANNUAL_REPORT")
        x.normalized_value = norm
        return x
    assert trend_score(-6.45) == 1.0 and trend_score(2.0) == 0.0 and trend_score(-2.1) == 0.5
    assert check_esef_quote(r(-6.45, 1.0), rep).status == "OK"
    assert check_esef_quote(r(-6.45, 0.8), rep).status == "ÉCART"                      # note fausse
    assert check_esef_quote(r(-5.0, 1.0, calc.replace("−6,45", "−5,00")), rep).status == "ÉCART"  # calcul faux
    assert check_esef_quote(r(-6.45, 1.0, calc.replace("6 ans", "5 ans")), rep).status == "ÉCART"  # années
    assert check_esef_quote(r(-6.45, 1.0, calc.replace("6855000", "6855001")), rep).status == "ÉCART"  # total absent


def test_rythme_avec_totaux_decimaux():
    from diams.verify_curated import check_esef_quote
    rep = "Émissions totales de GES Location-Based 265,1 145,2 157,2 Émissions totales de GES Market-Based"
    q = "Émissions totales de GES Location-Based 265,1 145,2 157,2"
    calc = " ; rythme annuel moyen (2017 → 2025, 8 ans) : (145,2 / 265,1)^(1/8) − 1 = −7,25 %"
    x = row("x", -7.25, f"Rapport (Mt) : « {q} »{calc}", ind="ENV_GHG_TREND", src="ESEF")
    x.normalized_value = 1.0
    assert check_esef_quote(x, rep).status == "OK"


def test_rythme_avec_espaces_de_milliers():
    from diams.verify_curated import check_esef_quote
    rep = "Émissions totales de GES (scope 2 market-based) 622 429 747 810 658 455 - 11,9 %"
    q = "Émissions totales de GES (scope 2 market-based) 622 429 747 810 658 455"
    calc = " ; rythme annuel moyen (2018 → 2025, 7 ans) : (658455 / 622429)^(1/7) − 1 = 0,81 %"
    x = row("x", 0.81, f"DEU (colonnes 2018, 2024, 2025) : « {q} »{calc}", ind="ENV_GHG_TREND", src="AMF_BDIF")
    x.normalized_value = 0.0
    assert check_esef_quote(x, rep).status == "OK"


def test_delegation_tier3_seulement_si_verifie():
    from diams.verify_curated import Verdict, finalize
    ok = Verdict("OK", ["citation retrouvée ✓"])
    assert finalize(ok, "", "press").status == "JUGEMENT"                      # sans délégation : humain
    assert finalize(ok, "", "press", delegated=True).status == "OK-DÉLÉGUÉ"    # délégation : approuvable
    assert finalize(ok, "", "crowd", delegated=True).status == "JUGEMENT"      # jamais le tier crowd
    assert finalize(Verdict("ÉCART", []), "", "press", delegated=True).status == "ÉCART"
    assert finalize(ok, "note", "press", delegated=True).status == "JUGEMENT"  # jugement signalé : humain



def test_baisse_sur_un_an_refusee_hausse_acceptee():
    from diams.verify_curated import check_esef_quote
    rep = "Total GHG emissions (market-based) million tonnes 1,142 1,166 and 887.4 828.5"
    def r(q, calc, value, norm):
        x = row("x", value, f"Rapport : « {q} »{calc}", ind="ENV_GHG_TREND", src="ESEF")
        x.normalized_value = norm
        return x
    baisse = r("Total GHG emissions (market-based) million tonnes 1,142 1,166",
               " ; rythme annuel moyen (2024 → 2025, 1 an) : (1142 / 1166)^(1/1) − 1 = −2,06 %", -2.06, 0.4905)
    assert check_esef_quote(baisse, rep).status == "ÉCART"
    hausse = r("Total GHG emissions (market-based) million tonnes 1,142 1,166 and 887.4 828.5", " ; rythme annuel moyen (2024 → 2025, 1 an) : (887,4 / 828,5)^(1/1) − 1 = 7,11 %", 7.11, 0.0)
    assert check_esef_quote(hausse, rep).status == "OK"



def test_effectifs_en_notation_barre():
    from diams.verify_curated import check_esef_quote
    rep = "Director Nominee Highlights Board Composition 4 /10 women 6 /10 men 3 /10 members"
    q = "Director Nominee Highlights Board Composition 4 /10 women 6 /10 men"
    assert check_esef_quote(esef_row("GOV_BOARD_GENDER", 40.0, q), rep).status == "OK"
    assert check_esef_quote(esef_row("GOV_BOARD_GENDER", 45.0, q), rep).status == "ÉCART"



def test_rythme_depuis_une_variation_publiee():
    from diams.verify_curated import check_esef_quote
    rep = "Reach net zero across our value chain by 2040 2025 progress and results 19% CO 2 reduction vs. 2022 baseline in Scope 1, 2 and 3 emissions"
    q = "2025 progress and results 19% CO 2 reduction vs. 2022 baseline in Scope 1, 2 and 3 emissions"
    calc = " ; rythme annuel moyen (2022 → 2025, 3 ans) : (1 − 19 %)^(1/3) − 1 = −6,78 %"
    x = row("x", -6.78, f"Rapport : « {q} »{calc}", ind="ENV_GHG_TREND", src="ESEF")
    x.normalized_value = 1.0
    assert check_esef_quote(x, rep).status == "OK"
    y = row("x", -6.78, f"Rapport : « {q} »{calc.replace('19 %', '29 %')}", ind="ENV_GHG_TREND", src="ESEF")
    y.normalized_value = 1.0
    assert check_esef_quote(y, rep).status == "ÉCART"   # pourcentage absent de la citation


def test_sanction_gravite_relue_dans_la_citation():
    from diams.verify_curated import check_esef_quote
    rep = ("The Commission has fined 15 major car manufacturers. The breakdown of the fines imposed on each party is as "
           "follows: Stellantis 50% €74 934 000 BMW €24 587 000. The European Commission has fined Google €2.95 billion "
           "for breaching EU antitrust rules. Mercedes-Benz was not fined, as it revealed the cartel")

    def s(slug, vt, norm, q):
        x = row(slug, None, f"Commission européenne : « {q} »", ind="GOV_SANCTIONS", src="EU_COMPETITION")
        x.value_numeric, x.value_text, x.normalized_value, x.nature = None, vt, norm, "controversy"
        return x
    assert check_esef_quote(s("stellantis", "amende de 74,9 M€ (entente)", 0.5, "The Commission has fined 15 major car manufacturers » ; « Stellantis 50% €74 934 000"), rep).status == "OK"
    assert check_esef_quote(s("google", "amende de 2,95 Md€ (abus)", 0.9,
                              "The European Commission has fined Google €2.95 billion"), rep).status == "OK"
    # Gravité surévaluée, ou montant absent de la citation : écart.
    assert check_esef_quote(s("bmw", "amende de 24,6 M€ (entente)", 0.7, "The Commission has fined 15 major car manufacturers » ; « BMW €24 587 000"), rep).status == "ÉCART"
    assert check_esef_quote(s("bmw", "amende de 34,6 M€ (entente)", 0.5, "The Commission has fined 15 major car manufacturers » ; « BMW €24 587 000"), rep).status == "ÉCART"
    # Immunité de clémence : infraction constatée, sans amende.
    assert check_esef_quote(s("mercedes-benz", "infraction constatée, immunité d'amende (clémence)", 0.5,
                              "Mercedes-Benz was not fined, as it revealed the cartel"), rep).status == "OK"


def test_sanction_montant_en_francais():
    from diams.verify_curated import check_esef_quote
    rep = ("Le 1 er septembre 2025, la CNIL a sanctionné la société INFINITE STYLES SERVICES CO. LIMITED, filiale "
           "irlandaise du groupe SHEIN, d'une amende de 150 millions d'euros pour avoir déposé des cookies. "
           "la CNIL a sanctionné la société SAMARITAINE SAS d'une amende de 100 000 euros")

    def s(vt, norm, q):
        x = row("shein", None, f"CNIL : « {q} »", ind="GOV_SANCTIONS", src="GDPR_DPA")
        x.value_numeric, x.value_text, x.normalized_value, x.nature = None, vt, norm, "controversy"
        return x
    q = "filiale irlandaise du groupe SHEIN, d'une amende de 150 millions d'euros"
    assert check_esef_quote(s("amende de 150 M€ (cookies)", 0.7, q), rep).status == "OK"
    assert check_esef_quote(s("amende de 150 M€ (cookies)", 0.9, q), rep).status == "ÉCART"
    assert check_esef_quote(s("amende de 0,1 M€ (caméras)", 0.5,
                              "SAMARITAINE SAS d'une amende de 100 000 euros"), rep).status == "OK"


def test_sanction_tableau_en_euros():
    from diams.verify_curated import check_esef_quote
    rep = ("l'Autorité de la concurrence inflige une sanction de 187,5 millions d'euros à TotalEnergies Marketing "
           "France, à deux sociétés du groupe Rubis et à EG Retail. Entreprises Montants des sanctions (en euros) "
           "TEMF 115 820 000 Rubis 64 670 000")
    q = ("inflige une sanction de 187,5 millions d'euros à TotalEnergies Marketing France » ; « "
         "Montants des sanctions (en euros) TEMF 115 820 000")
    x = row("totalenergies", None, f"Autorité de la concurrence : « {q} »", ind="GOV_SANCTIONS", src="FR_COMPETITION")
    x.value_numeric, x.value_text, x.normalized_value, x.nature = None, "amende de 115,8 M€ (entente)", 0.7, "controversy"
    assert check_esef_quote(x, rep).status == "OK"
    x.value_text = "amende de 64,7 M€ (entente)"   # montant d'une autre société, absent de la citation
    assert check_esef_quote(x, rep).status == "ÉCART"


def test_sanction_virgule_decimale_devant_billion():
    from diams.verify_curated import check_esef_quote
    rep = "Italian Competition Authority: Amazon fined over € 1,128 billion for abusing its dominant position"
    x = row("amazon", None, f"AGCM : « {rep} »", ind="GOV_SANCTIONS", src="IT_COMPETITION")
    x.value_numeric, x.value_text, x.normalized_value, x.nature = None, "amende de 1,13 Md€ (abus)", 0.9, "controversy"
    assert check_esef_quote(x, rep).status == "OK"


def test_montants_en_euros_toutes_ecritures():
    from diams.verify_curated import euro_amounts
    def has(q, v):
        return any(abs(x - v) < 0.5 for x in euro_amounts(q))
    assert has("fined Apple over €1.8 billion", 1.8e9)
    assert has("Amazon fined over € 1,128 billion", 1.128e9)
    assert has("fines are therefore equal to EUR 114,681,657 for the Apple Group", 114_681_657)
    assert has("imposed a 98,635,416.67 euro fine on Apple Inc.", 98_635_416.67)
    assert has("Amazon EU S.àr.l. 1 million euro for the misleading advertising", 1e6)
    assert has("a fine of EUR 10 million jointly and severally", 1e7)
    assert has("Meta Platforms Inc. EUR 3.5 million for two unfair commercial practices", 3.5e6)
    assert has("d'une amende de 150 millions d'euros", 1.5e8)
    assert has("une sanction de 187,5 millions d'euros", 1.875e8)
    assert has("d'une amende de 100 000 euros", 1e5)
    assert has("Stellantis 50% €74 934 000", 74_934_000)


def test_independance_tous_sauf_le_pdg():
    from diams.verify_curated import check_esef_quote
    rep = ("To elect the twelve directors nominated by our board of directors. All of our director nominees are "
           "independent, with the exception of our CEO.")
    q = "To elect the twelve directors nominated by our board of directors » ; « All of our director nominees are independent, with the exception of our CEO"
    ok = row("meta", 91.7, f"Circulaire : « {q} » ; calcul : (12 − 1) / 12 = 91,7 %", ind="GOV_BOARD_INDEP", src="SEC_FILING")
    assert check_esef_quote(ok, rep).status == "OK"
    faux = row("meta", 92.7, f"Circulaire : « {q} » ; calcul : (12 − 1) / 12 = 92,7 %", ind="GOV_BOARD_INDEP", src="SEC_FILING")
    assert check_esef_quote(faux, rep).status == "ÉCART"
    autre = row("meta", 90.9, f"Circulaire : « {q} » ; calcul : (11 − 1) / 11 = 90,9 %", ind="GOV_BOARD_INDEP", src="SEC_FILING")
    assert check_esef_quote(autre, rep).status == "ÉCART"   # effectif 11 non cité


def test_mixite_depuis_deux_effectifs_cites():
    from diams.verify_curated import check_esef_quote
    rep = ("The Board nominated each of the 10 incumbent directors listed here. The Director nominees vary in age "
           "from 59 to 70, include four women, and collectively bring a range of professional and life experiences")
    q = "The Board nominated each of the 10 incumbent directors listed here » ; « The Director nominees vary in age from 59 to 70, include four women"
    ok = row("mondelez", 40.0, f"Circulaire : « {q} » ; calcul : 4 / 10 = 40 %", ind="GOV_BOARD_GENDER", src="SEC_FILING")
    assert check_esef_quote(ok, rep).status == "OK"
    faux = row("mondelez", 50.0, f"Circulaire : « {q} » ; calcul : 5 / 10 = 50 %", ind="GOV_BOARD_GENDER", src="SEC_FILING")
    assert check_esef_quote(faux, rep).status == "ÉCART"   # « cinq » n'est pas cité


def test_note_normalisee_de_la_mixite_controlee():
    from diams.verify_curated import check_esef_quote
    rep = "Notre conseil compte 40 % de femmes administratrices."
    x = row("x", 40.0, "Rapport : « Notre conseil compte 40 % de femmes administratrices »", ind="GOV_BOARD_GENDER", src="ESEF")
    x.normalized_value = 0.8
    assert check_esef_quote(x, rep).status == "OK"
    x.normalized_value = 0.4   # 40 % rapporté à 100 au lieu de la parité
    assert check_esef_quote(x, rep).status == "ÉCART"


def test_plastique_vierge_rythme_classe_entre_pairs():
    from diams.verify_curated import check_esef_quote
    rep = ("Entre 2019 et 2025 , il a ainsi réduit de 10.1 % son utilisation d’emballages en plastique et de 17 .7 % "
           "son utilisation de plastique vierge issu de ressources fossiles.")
    q = "Entre 2019 et 2025 , il a ainsi réduit de 10.1 % son utilisation d’emballages en plastique et de 17 .7 % son utilisation de plastique vierge issu de ressources fossiles"
    calc = " ; rythme annuel moyen (2019 → 2025, 6 ans) : (1 − 17,7 %)^(1/6) − 1 = −3,19 %"
    x = row("danone", -3.19, f"Rapport : « {q} »{calc}", ind="PLA_REDUCTION", src="ESEF")
    x.normalized_value = None
    assert check_esef_quote(x, rep).status == "OK"
    x.normalized_value = 0.76   # pas de note de seuil : classement entre pairs
    assert check_esef_quote(x, rep).status == "ÉCART"


def test_plastique_vierge_variations_annuelles_composees():
    from diams.verify_curated import check_esef_quote
    rep = ("Target metrics 2030 Target 2025 2024 2023 Comments Achieve an average of 2% year-over-year reduction in "
           "our absolute tonnage of virgin plastics through 2030 2% YOY 6%1 5%1 Goal refined in 2025")
    q = "Achieve an average of 2% year-over-year reduction in our absolute tonnage of virgin plastics through 2030 2% YOY 6%1 5%1"
    calc = " ; rythme annuel moyen (2023 → 2025, 2 ans) : ((1 − 5 %) × (1 − 6 %))^(1/2) − 1 = −5,50 %"
    x = row("pepsico", -5.5, f"Données : « {q} »{calc}", ind="PLA_REDUCTION", src="COMPANY_REPORT")
    x.normalized_value = None
    assert check_esef_quote(x, rep).status == "OK"
    y = row("pepsico", -5.5, f"Données : « {q} »" + calc.replace("2023 → 2025, 2 ans", "2022 → 2025, 3 ans").replace("^(1/2)", "^(1/3)"),
            ind="PLA_REDUCTION", src="COMPANY_REPORT")
    y.normalized_value = None
    assert check_esef_quote(y, rep).status == "ÉCART"   # trois ans pour deux variations


def test_conversion_d_unite_et_nombres_a_espaces():
    from diams.verify_curated import check_esef_quote
    rep = ("Intensité des GES par produit net 2025 2024 Émissions totales de GES (fondées sur le marché) par produit net (en teqCO2/EUR) 0,00039 0,00039 -1 % "
           "Résultat avant impôt 6 052 5 325 +13,6 % Impôt sur les bénéfices -1 834 -1 201")
    q1 = "Intensité des GES par produit net 2025 2024 Émissions totales de GES (fondées sur le marché) par produit net (en teqCO2/EUR) 0,00039 0,00039"
    x = row("cm", 390.0, f"Rapport : « {q1} » ; conversion : 0,00039 t/€ × 1 000 000 = 390 t/M€", ind="ENV_GHG_INTENSITY", src="AMF_BDIF")
    assert check_esef_quote(x, rep).status == "OK"
    x.value_numeric = 39.0
    assert check_esef_quote(x, rep).status == "ÉCART"
    q2 = "Résultat avant impôt 6 052 5 325 +13,6 % Impôt sur les bénéfices -1 834 -1 201"
    y = row("cm", 30.3, f"Rapport : « {q2} » ; calcul : 1834 / 6052 = 30,3 %", ind="TAX_EFFECTIVE_RATE", src="AMF_BDIF")
    assert check_esef_quote(y, rep).status == "OK"


def test_conversion_depuis_des_kilogrammes_par_euro_en_anglais():
    from diams.verify_curated import check_esef_quote
    rep = "GHG intensity (Location-based approach) (kgCO₂-e/EUR) 0.24 0.25 GHG intensity (Market-based approach) (kgCO₂-e/EUR) 0.23 0.24"
    q = "GHG intensity (Market-based approach) (kgCO₂-e/EUR) 0.23 0.24"
    x = row("philips", 230.0, f"Rapport : « {q} » ; conversion : 0,23 kg/€ × 1 000 = 230 t/M€ (intensité par million d'euros de chiffre d'affaires)",
            ind="ENV_GHG_INTENSITY", src="ESEF")
    assert check_esef_quote(x, rep).status == "OK"
    x.value_numeric = 23.0
    assert check_esef_quote(x, rep).status == "ÉCART"
    y = row("philips", 230.0, f"Rapport : « {q} » ; conversion : 0,25 kg/€ × 1 000 = 250 t/M€", ind="ENV_GHG_INTENSITY", src="ESEF")
    y.value_numeric = 250.0
    assert check_esef_quote(y, rep).status == "ÉCART"     # 0,25 n'est pas dans la citation


def test_conversion_depuis_des_kilotonnes_par_million_d_euros():
    from diams.verify_curated import check_esef_quote
    q = "Group emissions intensity – market-based (ktCO 2e/€m sales) 0.10 0.07* 0.06"
    x = row("richemont", 60.0, f"Rapport : « {q} » ; conversion : 0,06 kt/M€ × 1 000 = 60 t/M€", ind="ENV_GHG_INTENSITY", src="ANNUAL_REPORT")
    assert check_esef_quote(x, q).status == "OK"
    x.value_numeric = 0.06
    assert check_esef_quote(x, q).status == "ÉCART"


def test_conversion_depuis_des_tonnes_par_millier_d_euros():
    from diams.verify_curated import check_esef_quote
    q = "Émissions totales de GES fondées sur le marché par produit net Non publié 1,00 0,92 -8%"
    h = "Intensité des GES par produit net 2024initial 2024 recalculé 2025"
    rep = h + " Comparaison 2024-2025 (en teqCO2/milliers d’euros) " + q
    x = row("ldc", 920.0, f"Rapport : « {h} » ; « {q} » ; conversion : 0,92 t/k€ × 1 000 = 920 t/M€", ind="ENV_GHG_INTENSITY", src="ANNUAL_REPORT")
    assert check_esef_quote(x, rep).status == "OK"
    x.value_numeric = 920000.0
    assert check_esef_quote(x, rep).status == "ÉCART"


def test_colonnes_de_ratios_non_fusionnees_en_milliers():
    from diams.verify_curated import check_esef_quote
    q = "CEO pay ratio Year Methodology used Lower quartile Median Upper quartile 2025 Option B 137:1 126:1 104:1"
    x = row("abf", 126.0, f"Rapport : « {q} »", ind="LAB_CEO_PAY_RATIO", src="ESEF")
    assert check_esef_quote(x, q).status == "OK"
    x.value_numeric = 1126.0
    assert check_esef_quote(x, q).status == "ÉCART"


def test_taux_d_impot_recalcule_depuis_des_montants_a_l_anglaise():
    from diams.verify_curated import check_esef_quote
    rep = "Profit before income taxes 650,574 802,505 Income tax expense (191,421) (218,364) Profit for the year 459,153 584,141"
    q = "Profit before income taxes 650,574 802,505 Income tax expense (191,421) (218,364)"
    ok = row("fast-retailing", 27.2, f"Résultats annuels : « {q} » ; calcul : 218364 / 802505 = 27,2 %",
             ind="TAX_EFFECTIVE_RATE", src="ANNUAL_REPORT")
    assert check_esef_quote(ok, rep).status == "OK"
    faux = row("fast-retailing", 29.4, f"Résultats annuels : « {q} » ; calcul : 191421 / 650574 = 29,4 %",
               ind="TAX_EFFECTIVE_RATE", src="ANNUAL_REPORT")
    assert check_esef_quote(faux, rep).status == "OK"        # exercice précédent : cité, donc vérifiable
    absent = row("fast-retailing", 27.0, f"Résultats annuels : « {q} » ; calcul : 218364 / 808000 = 27,0 %",
                 ind="TAX_EFFECTIVE_RATE", src="ANNUAL_REPORT")
    assert check_esef_quote(absent, rep).status == "ÉCART"   # 808 000 n'est pas cité


def test_citation_propre_retrouvee_malgre_les_mots_coupes_du_pdf():
    from diams.verify_curated import check_esef_quote
    rep = "Currently, five out of 15 Board members ar e women (same ratio as last re porting year)."
    ok = row("ab-inbev", 33.3, "Rapport : « Currently, five out of 15 Board members are women » ; calcul : 5 / 15 = 33,3 %",
             ind="GOV_BOARD_GENDER", src="ESEF")
    v = check_esef_quote(ok, rep)
    assert v.status == "OK" and "espaces de mise en page ignorés" in v.details[0]
    autre = row("ab-inbev", 33.3, "Rapport : « Currently, five out of 15 Board members are men » ; calcul : 5 / 15 = 33,3 %",
                ind="GOV_BOARD_GENDER", src="ESEF")
    assert check_esef_quote(autre, rep).status == "ÉCART"


def test_effectif_publie_en_deux_parties():
    from diams.verify_curated import check_esef_quote
    rep = ("the Board, which is composed of two executive directors and 13 non-executive directors with diverse "
           "backgrounds. The non-executive directors are, without exception, indisputably independent in character and judgment.")
    q = ("which is composed of two executive directors and 13 non-executive directors » ; « The non-executive directors "
         "are, without exception, indisputably independent in character and judgment")
    ok = row("richemont", 86.7, f"Rapport : « {q} » ; calcul : 13 / (2 + 13) = 86,7 %", ind="GOV_BOARD_INDEP", src="ANNUAL_REPORT")
    assert check_esef_quote(ok, rep).status == "OK"
    faux = row("richemont", 81.3, f"Rapport : « {q} » ; calcul : 13 / (3 + 13) = 81,3 %", ind="GOV_BOARD_INDEP", src="ANNUAL_REPORT")
    assert check_esef_quote(faux, rep).status == "ÉCART"   # « 3 » n'est pas cité


def test_numerateur_en_deux_parties():
    from diams.verify_curated import check_esef_quote
    rep = ("Our Supervisory Board comprises twelve members. In 2025 six members were employee representatives. "
           "the Supervisory Board considers it to be adequate if at least three of its shareholder members are independent")
    q = ("Our Supervisory Board comprises twelve members » ; « six members were employee representatives » ; "
         "« at least three of its shareholder members are independent")
    ok = row("beiersdorf", 75.0, f"Rapport : « {q} » ; calcul : (6 + 3) / 12 = 75,0 %", ind="GOV_BOARD_INDEP", src="ANNUAL_REPORT")
    assert check_esef_quote(ok, rep).status == "OK"
    faux = row("beiersdorf", 83.3, f"Rapport : « {q} » ; calcul : (6 + 4) / 12 = 83,3 %", ind="GOV_BOARD_INDEP", src="ANNUAL_REPORT")
    assert check_esef_quote(faux, rep).status == "ÉCART"


def test_conseil_entierement_independant():
    from diams.verify_curated import check_esef_quote
    rep = ("The Chair and all members of the Board of Directors are independent, were not previously members of the "
           "Nestlé management. Le Conseil de Surveillance a constaté que l’ensemble de ses membres est indépendant "
           "(hors membre représentant les salariés). All members of the Board are non-executive.")
    en = row("nestle", 100, "Rapport : « The Chair and all members of the Board of Directors are independent »",
             ind="GOV_BOARD_INDEP", src="ANNUAL_REPORT")
    assert check_esef_quote(en, rep).status == "OK"
    fr = row("bonduelle", 100, "Rapport : « Le Conseil de Surveillance a constaté que l’ensemble de ses membres est indépendant »",
             ind="GOV_BOARD_INDEP", src="AMF_BDIF")
    assert check_esef_quote(fr, rep).status == "OK"
    non = row("nestle", 100, "Rapport : « All members of the Board are non-executive »", ind="GOV_BOARD_INDEP", src="ANNUAL_REPORT")
    assert check_esef_quote(non, rep).status == "ÉCART"
    moins = row("nestle", 90, "Rapport : « The Chair and all members of the Board of Directors are independent »",
                ind="GOV_BOARD_INDEP", src="ANNUAL_REPORT")
    assert check_esef_quote(moins, rep).status == "ÉCART"


def test_exception_composee_executifs_et_representant():
    from diams.verify_curated import check_esef_quote
    rep = ("As at 31 December 2025, the Board comprised nine Directors: the Board Chair, two Executive Directors and six "
           "Non-Executive Directors (NEDs). The majority (88%) of the NEDs were independent, except for Reginaldo Ecclissato.")
    q = ("As at 31 December 2025, the Board comprised nine Directors: the Board Chair, two Executive Directors and six "
         "Non-Executive Directors (NEDs) » ; « The majority (88%) of the NEDs were independent, except for Reginaldo Ecclissato")
    ok = row("tmicc", 66.7, f"Rapport : « {q} » ; calcul : (9 − (2 + 1)) / 9 = 66,7 %", ind="GOV_BOARD_INDEP", src="ESEF")
    assert check_esef_quote(ok, rep).status == "OK"
    trois = row("tmicc", 55.6, f"Rapport : « {q} » ; calcul : (9 − (3 + 1)) / 9 = 55,6 %", ind="GOV_BOARD_INDEP", src="ESEF")
    assert check_esef_quote(trois, rep).status == "ÉCART"   # « trois » n'est pas cité
    deux_un = row("tmicc", 66.7, f"Rapport : « {q} » ; calcul : (9 − (1 + 1 + 1)) / 9 = 66,7 %", ind="GOV_BOARD_INDEP", src="ESEF")
    assert check_esef_quote(deux_un, rep).status != "OK"


def test_president_independant_compte_pour_un():
    from diams.verify_curated import check_esef_quote
    rep = ("As at 31 December 2025, the Unilever Board comprised ten Directors: the Chair, two Executive Directors and "
           "seven independent Non-Executive Directors. The Chair was considered to be independent on appointment.")
    q = ("As at 31 December 2025, the Unilever Board comprised ten Directors: the Chair, two Executive Directors and "
         "seven independent Non-Executive Directors » ; « The Chair was considered to be independent on appointment")
    ok = row("unilever", 80.0, f"Rapport : « {q} » ; calcul : (7 + 1) / 10 = 80,0 %", ind="GOV_BOARD_INDEP", src="ESEF")
    assert check_esef_quote(ok, rep).status == "OK"
    q2 = "As at 31 December 2025, the Unilever Board comprised ten Directors: the Chair, two Executive Directors and seven independent Non-Executive Directors"
    sans = row("unilever", 80.0, f"Rapport : « {q2} » ; calcul : (7 + 1) / 10 = 80,0 %", ind="GOV_BOARD_INDEP", src="ESEF")
    assert check_esef_quote(sans, rep).status == "ÉCART"   # indépendance du président non citée


def test_effectif_publie_en_trois_parties():
    from diams.verify_curated import check_esef_quote
    rep = "The Board has 1 executive director, 6 non-executive directors and 3 independent directors."
    q = "The Board has 1 executive director, 6 non-executive directors and 3 independent directors"
    ok = row("lotus", 30.0, f"Rapport : « {q} » ; calcul : 3 / (1 + 6 + 3) = 30,0 %", ind="GOV_BOARD_INDEP", src="ESEF")
    assert check_esef_quote(ok, rep).status == "OK"
    faux = row("lotus", 27.3, f"Rapport : « {q} » ; calcul : 3 / (1 + 7 + 3) = 27,3 %", ind="GOV_BOARD_INDEP", src="ESEF")
    assert check_esef_quote(faux, rep).status == "ÉCART"   # « 7 » n'est pas cité


def test_denominateur_hors_representants_des_salaries():
    from diams.verify_curated import check_esef_quote
    rep = "Le Conseil de Surveillance est composé de 17 membres dont 4 membres sont indépendants et 2 sont des représentants des salariés."
    q = "Le Conseil de Surveillance est composé de 17 membres dont 4 membres sont indépendants et 2 sont des représentants des salariés"
    ok = row("ldc", 26.7, f"Rapport : « {q} » ; calcul : 4 / (17 − 2) = 26,7 %", ind="GOV_BOARD_INDEP", src="ESEF")
    assert check_esef_quote(ok, rep).status == "OK"
    faux = row("ldc", 25.0, f"Rapport : « {q} » ; calcul : 4 / (17 − 1) = 25,0 %", ind="GOV_BOARD_INDEP", src="ESEF")
    assert check_esef_quote(faux, rep).status == "ÉCART"   # « 1 » n'est pas cité


def test_conseil_sans_independant_et_une_seule_femme():
    from diams.verify_curated import check_esef_quote
    rep = ("Pas de parité au Conseil : une seule femme était administratrice en 2025 ( sur 12 membres). "
           "Absence d’administrateurs indépendants : les membres du Conseil sont uniquement des adhérents. "
           "Des administrateurs indépendants siègent au comité d'audit.")
    zero = row("mousquetaires", 0, "Rapport : « Absence d’administrateurs indépendants : les membres du Conseil sont "
               "uniquement des adhérents »", ind="GOV_BOARD_INDEP", src="COMPANY_REPORT")
    assert check_esef_quote(zero, rep).status == "OK"
    # La règle ne vaut que pour 0 % : une autre valeur doit être citée.
    dix = row("mousquetaires", 10, "Rapport : « Absence d’administrateurs indépendants : les membres du Conseil sont "
              "uniquement des adhérents »", ind="GOV_BOARD_INDEP", src="COMPANY_REPORT")
    assert check_esef_quote(dix, rep).status == "ÉCART"
    # Une phrase qui mentionne des indépendants ne vaut pas 0 %.
    faux = row("mousquetaires", 0, "Rapport : « Des administrateurs indépendants siègent au comité d'audit »",
               ind="GOV_BOARD_INDEP", src="COMPANY_REPORT")
    assert check_esef_quote(faux, rep).status == "ÉCART"
    une = row("mousquetaires", 8.3, "Rapport : « Pas de parité au Conseil : une seule femme était administratrice en "
              "2025 ( sur 12 membres) » ; calcul : 1 / 12 = 8,3 %", ind="GOV_BOARD_GENDER", src="COMPANY_REPORT")
    v = check_esef_quote(une, rep)
    assert v.status == "OK", v.details
    deux = row("mousquetaires", 16.7, "Rapport : « Pas de parité au Conseil : une seule femme était administratrice en "
               "2025 ( sur 12 membres) » ; calcul : 2 / 12 = 16,7 %", ind="GOV_BOARD_GENDER", src="COMPANY_REPORT")
    assert check_esef_quote(deux, rep).status == "ÉCART"


def test_independance_exception_nommee_a_part():
    from diams.verify_curated import check_esef_quote
    rep = ("The Board has selected the following eight nominees for election to the Board. As a result of these "
           "reviews, the Board affirmatively determined that all of the Company’s current non-management directors "
           "are, and, during their service on the Board in 2025, were “independent” of the Company and its management "
           "within the meaning of the applicable Nasdaq rules. Mr. Peterson is not considered an independent director "
           "nominee because of his employment as President and CEO of the Company.")
    q = ("The Board has selected the following eight nominees for election to the Board » ; « the Board affirmatively "
         "determined that all of the Company’s current non-management directors are, and, during their service on the "
         "Board in 2025, were “independent” of the Company and its management within the meaning of the applicable "
         "Nasdaq rules » ; « Mr. Peterson is not considered an independent director nominee")
    ok = row("newell", 87.5, f"Circulaire : « {q} » ; calcul : (8 − 1) / 8 = 87,5 %", ind="GOV_BOARD_INDEP", src="SEC_FILING")
    v = check_esef_quote(ok, rep)
    assert v.status == "OK", v.details
    # Sans la phrase « tous les autres sont indépendants », l'exception seule ne suffit pas.
    seul = row("newell", 87.5, "Circulaire : « The Board has selected the following eight nominees for election to the "
               "Board » ; « Mr. Peterson is not considered an independent director nominee » ; calcul : (8 − 1) / 8 = 87,5 %",
               ind="GOV_BOARD_INDEP", src="SEC_FILING")
    assert check_esef_quote(seul, rep).status == "ÉCART"


def test_montants_groupes_en_colonnes_voisines():
    from diams.verify_curated import check_esef_quote
    rep = ("RÉSULTAT AVANT IMPÔTS 430 809 336 503 Impôts sur les sociétés 19.2 ( 104 665 ) ( 90 161 ) "
           "RÉSULTAT CONSOLIDÉ 326 144 246 342")
    q = "RÉSULTAT AVANT IMPÔTS 430 809 336 503 Impôts sur les sociétés 19.2 ( 104 665 ) ( 90 161 )"
    ok = row("ldc", 24.3, f"Rapport : « {q} » ; calcul : 104665 / 430809 = 24,3 %", ind="TAX_EFFECTIVE_RATE", src="AMF")
    v = check_esef_quote(ok, rep)
    assert v.status == "OK", v.details
    # 809 336 n'est pas un montant de la citation lu au bon endroit : le numérateur 104665
    # rapporté à 336503 (colonne 2024-2025) donne une autre part.
    faux = row("ldc", 24.3, f"Rapport : « {q} » ; calcul : 104665 / 336503 = 24,3 %", ind="TAX_EFFECTIVE_RATE", src="AMF")
    assert check_esef_quote(faux, rep).status == "ÉCART"
    # Le milieu d'un groupe (« 809 336 ») n'est pas un montant cité.
    milieu = row("ldc", 12.9, f"Rapport : « {q} » ; calcul : 104665 / 809336 = 12,9 %", ind="TAX_EFFECTIVE_RATE", src="AMF")
    assert check_esef_quote(milieu, rep).status == "ÉCART"


def test_mixite_tableau_sexe_feminin():
    from diams.verify_curated import check_esef_quote
    rep = ("21.d Sexe Pourcentage Féminin 0 % Masculin 100 % TOTAL 100 % Le Conseil d’administration compte un "
           "administrateur indépendant parmi les six administrateurs qui le composent.")
    q = "21.d Sexe Pourcentage Féminin 0 % Masculin 100 % TOTAL 100 % Le Conseil d’administration compte un administrateur"
    ok = row("auchan", 0, f"Rapport : « {q} »", ind="GOV_BOARD_GENDER", src="ANNUAL_REPORT")
    v = check_esef_quote(ok, rep)
    assert v.status == "OK", v.details
    faux = row("auchan", 20, f"Rapport : « {q} »", ind="GOV_BOARD_GENDER", src="ANNUAL_REPORT")
    assert check_esef_quote(faux, rep).status == "ÉCART"


def test_mots_cles_exploitation_animale_alimentation():
    import re
    from diams.verify_curated import ESEF_KEYWORDS
    pat = re.compile(ESEF_KEYWORDS["ANI_EXPLOITATION"][0], re.I)
    for ok in ["Fabrication de fromage", "galettes pur beurre", "Charcuterie", "Transformation et conservation de poisson",
               "foie gras de canard", "Élevage de volailles", "Aquaculture en mer", "Pêche en mer", "crème fraîche"]:
        assert pat.search(ok), ok
    for ko in ["beurre de cacahuète", "beurre de karité", "Fabrication de biscuits", "pâte à tartiner aux noisettes"]:
        assert not pat.search(ko), ko


def test_value_variants_trois_decimales():
    from diams.verify_curated import _value_variants
    assert "3,147" in _value_variants(3.147) and "3.147" in _value_variants(3.147)
    assert "3,15" in _value_variants(3.15) and not any(len(x) > 4 for x in _value_variants(3.15) if "," in x and x.startswith("3,"))


def test_trend_pct_unite_dans_intitule():
    from types import SimpleNamespace
    from diams.verify_curated import check_trend_pct
    q = "Reduction in overall virgin plastic (vs. 2020) (%)(2)(10) 11.5 4.6 + 1.7 2.9"
    row = SimpleNamespace(indicator_code="PLA_REDUCTION", value_numeric=-2.41, normalized_value=None,
                          excerpt="… « x » ; rythme annuel moyen (2020 → 2025, 5 ans) : (1 − 11,5 %)^(1/5) − 1 = −2,41 %")
    ok, details, actif = check_trend_pct(row, q)
    assert actif and ok, details
    # Sans « (%) » dans l'intitulé, un nombre nu ne suffit pas.
    ok2, _, _ = check_trend_pct(row, q.replace("(%)", ""))
    assert not ok2


def test_canon_accents_decomposes():
    import unicodedata
    from diams.verify_curated import _canon
    nfd = unicodedata.normalize("NFD", "sanctionne quatre sociétés")
    assert _canon("sanctionne quatre sociétés") in _canon("La décision " + nfd)


def test_montant_suivi_du_symbole_euro():
    from diams.verify_curated import euro_amounts
    assert 55000.0 in euro_amounts("une amende de 55 000 € a été prononcée")
    assert 65000.0 in euro_amounts("une amende de 65 000 euros a été prononcée")


def test_intensite_par_million_de_dollars():
    import re
    from diams.verify_curated import ESEF_KEYWORDS
    assert re.search(ESEF_KEYWORDS["ENV_GHG_INTENSITY"][1], "GHG emissions intensity METRIC VALUE (tCO2e PER $1M) Market-based 146", re.I)


def test_mots_animaux_francais_et_anglais():
    import re
    from diams.verify_curated import ESEF_KEYWORDS
    kw = ESEF_KEYWORDS["ANI_EXPLOITATION"][0]
    for oui in ("Les œufs bio de Loué", "des oeufs frais", "specialty cheese brand", "salted butter", "Salmon Grillers", "brand fish",
                "für Fisch- und Fleischprodukte", "Milch und Käse"):
        assert re.search(kw, oui, re.I), oui
    for non in ("Almond Butter Protein Bars", "cocoa butter", "peanut butter"):
        assert not re.search(kw, non, re.I), non


def test_sanction_en_livres_convertie_au_taux_de_la_bce():
    from diams.verify_curated import check_esef_quote
    rep = "The fines for each company are: BMW £10,660,781 £400,144 £11,060,925 (20% settlement reduction) Ford"
    q = "The fines for each company are: BMW £10,660,781 £400,144 £11,060,925 (20% settlement reduction)"
    x = row("bmw", None, f"CMA : « {q} » — amende", ind="GOV_SANCTIONS", src="UK_COMPETITION")
    x.value_numeric, x.value_text, x.normalized_value, x.nature = None, "amende de 11,1 M£ (entente)", 0.5, "controversy"
    x.observed_on = "2025-04-01"
    assert check_esef_quote(x, rep, rates={("GBP", "2025"): 0.8568}).status == "OK"
    # Sans taux de la BCE, la gravité ne peut pas être calculée : écart.
    assert check_esef_quote(x, rep, rates={}).status == "ÉCART"
    x.value_text = "amende de 11,1 M€ (entente)"   # devise erronée : aucun montant en euros cité
    assert check_esef_quote(x, rep, rates={("GBP", "2025"): 0.8568}).status == "ÉCART"


def test_independants_nommes_comptes_dans_la_citation():
    from diams.verify_curated import check_esef_quote
    rep = ("The Board is currently comprised of ten members. The Board has determined that Messrs. Dinkins, Douglas, "
           "Pizula and Vidergauz and Mses. Demel, Hall and Jackson are independent, as that term is defined")
    q = ("The Board is currently comprised of ten members » ; « The Board has determined that Messrs. Dinkins, Douglas, "
         "Pizula and Vidergauz and Mses. Demel, Hall and Jackson are independent")
    x = row("monster-beverage", 70.0, f"Circulaire : « {q} » ; calcul : 7 administrateurs nommés indépendants / 10 = 70 % (administrateurs indépendants).",
            ind="GOV_BOARD_INDEP", src="SEC_FILING")
    x.normalized_value = 0.7
    assert check_esef_quote(x, rep).status == "OK"
    y = row("monster-beverage", 80.0, f"Circulaire : « {q} » ; calcul : 8 administrateurs nommés indépendants / 10 = 80 % (administrateurs indépendants).",
            ind="GOV_BOARD_INDEP", src="SEC_FILING")
    y.normalized_value = 0.8
    assert check_esef_quote(y, rep).status == "ÉCART"   # 7 noms seulement


def test_montants_abreges_m_et_bn():
    from diams.verify_curated import euro_amounts
    assert any(abs(x - 17e6) < 1 for x in euro_amounts("imposing a fine of €17m on Meta Platforms"))
    assert any(abs(x - 1.2e9) < 1 for x in euro_amounts("a fine of €1.2bn"))
    assert not any(abs(x - 17e6) < 1 for x in euro_amounts("€17 per month"))


def test_sanction_en_dollars_milliard():
    from diams.verify_curated import check_esef_quote, foreign_amounts
    assert any(abs(x - 1e9) < 1 for x in foreign_amounts("pay a $1 billion civil penalty", "USD"))
    rep = "Amazon will be required to pay a $1 billion civil penalty, provide $1.5 billion in refunds"
    x = row("amazon", None, f"FTC : « {rep} »", ind="GOV_SANCTIONS", src="US_FTC")
    x.value_numeric, x.value_text, x.normalized_value, x.nature = None, "amende de 1 Md$ (Prime)", 0.7, "controversy"
    x.observed_on = "2025-09-25"
    assert check_esef_quote(x, rep, rates={("USD", "2025"): 1.13}).status == "OK"       # ≈ 885 M€ : 0,7
    x.normalized_value = 0.9
    assert check_esef_quote(x, rep, rates={("USD", "2025"): 1.13}).status == "ÉCART"


def test_dollars_australiens_lus_sans_prefixe():
    # Les jugements australiens écrivent « $60 million » : le dollar y est australien.
    from diams.verify_curated import foreign_amounts
    assert 60e6 in foreign_amounts("penalties cumulatively totalling $60 million for the said", "AUD")
    assert 14e6 in foreign_amounts("pecuniary penalties of A$14 million", "AUD")


def test_taux_d_impot_sur_une_perte_refuse():
    from diams.verify_curated import check_esef_quote
    from diams.load import EvidenceRow
    row = EvidenceRow(entity_slug="x", indicator_code="TAX_EFFECTIVE_RATE", source_code="ESEF", nature="result",
                      observed_on="2026-03-01", value_type="numeric", value_numeric=16.1, confidence=0.9,
                      source_url="u", excerpt="Note sur l'impôt (produit d'impôt sur une perte avant impôt) : « Effective tax rate 16.1 % »")
    v = check_esef_quote(row, "Total Tax benefit Effective tax rate 16.1 % for the year")
    assert v.status != "OK"
