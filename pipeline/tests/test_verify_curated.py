"""Vérification déterministe des preuves curées (BOCC, HATVP)."""
from paris_memoire.load import EvidenceRow
from paris_memoire.verify_curated import check_hatvp, parse_bocc_text, verify_bocc

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
    from paris_memoire.verify_curated import check_esef_quote
    q = "L'écart de rémunération entre les femmes et les hommes au sein de Crédit Agricole S.A. est de 31,68 % en 2025"
    assert check_esef_quote(esef_row("LAB_GENDER_PAYGAP", 31.68, q), REPORT).status == "OK"
    q2 = "Intensité de GES - basée sur le marché 2 773,87 tonnes éqCO₂/M€"
    # deux colonnes côte à côte (2025, 2024) ne fusionnent pas en un seul nombre
    report = REPORT + " Ratio entre la rémunération la plus élevée et la rémunération médiane des salariés 44,61 48,60"
    q3 = "Ratio entre la rémunération la plus élevée et la rémunération médiane des salariés 44,61 48,60"
    assert check_esef_quote(esef_row("LAB_CEO_PAY_RATIO", 44.61, q3), report).status == "OK"
    assert check_esef_quote(esef_row("ENV_GHG_INTENSITY", 2773.87, q2), REPORT).status == "OK"


def test_signe_moins_typographique():
    from paris_memoire.verify_curated import check_esef_quote
    rep = "The ↗ Gender Pay Gap was –9.9% (2024:–10.1%)."
    q = "The ↗ Gender Pay Gap was –9.9%"
    assert check_esef_quote(esef_row("LAB_GENDER_PAYGAP", -9.9, q), rep).status == "OK"
    assert check_esef_quote(esef_row("LAB_GENDER_PAYGAP", 9.9, q), rep).status == "ÉCART"
    rep2 = "Mr. Jassy’s compensation was $2,069,861, resulting in a ratio of those amounts of 1-to-51."
    q2 = "resulting in a ratio of those amounts of 1-to-51"
    assert check_esef_quote(esef_row("LAB_CEO_PAY_RATIO", 51, q2 + " » ; « median"), rep2 + " median").status == "OK"


def test_ecart_en_faveur_des_femmes_compte_negatif():
    from paris_memoire.verify_curated import check_esef_quote
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
    from paris_memoire.verify_curated import check_esef_quote
    rep = "Key elements of our Board independence include: • 11 of 12 director nominees are independent • All"
    q = "11 of 12 director nominees are independent"
    assert check_esef_quote(esef_row("GOV_BOARD_INDEP", 91.7, q), rep).status == "OK"
    assert check_esef_quote(esef_row("GOV_BOARD_INDEP", 92.0, q), rep).status == "ÉCART"
    rep2 = "Le Conseil d’Administration d’ENGIE comprend six femmes Administratrices sur 14 membres."
    q2 = "Conseil d’Administration d’ENGIE comprend six femmes Administratrices sur 14 membres"
    assert check_esef_quote(esef_row("GOV_BOARD_GENDER", 42.9, q2), rep2).status == "OK"


def test_nombres_en_notation_anglaise():
    from paris_memoire.verify_curated import check_esef_quote
    report = "For 2025, the ratio of the annual total compensation of our CEO to the median employee was 1,980 to 1."
    q = "the ratio of the annual total compensation of our CEO to the median employee was 1,980 to 1"
    assert check_esef_quote(esef_row("LAB_CEO_PAY_RATIO", 1980, q), report).status == "OK"
    report2 = "Our median employee pay ratio was 533.2:1 in 2025"
    assert check_esef_quote(esef_row("LAB_CEO_PAY_RATIO", 533.2, "median employee pay ratio was 533.2:1"), report2).status == "OK"


def test_plusieurs_citations_toutes_verifiees():
    from paris_memoire.verify_curated import check_esef_quote
    report = "3.2 Plan de vigilance 3.2.7 Dispositif de suivi des mesures. Ailleurs : une cartographie des risques achats."
    ok = esef_row("SUP_VIGILANCE_PLAN", None, "3.2 Plan de vigilance 3.2.7 Dispositif de suivi des mesures » et « une cartographie des risques achats")
    assert check_esef_quote(ok, report).status == "OK"
    ko = esef_row("SUP_VIGILANCE_PLAN", None, "3.2 Plan de vigilance 3.2.7 Dispositif de suivi des mesures » et « une cartographie inventée")
    assert check_esef_quote(ko, report).status == "ÉCART"


def test_esef_colonnes_voisines_de_trois_chiffres():
    from paris_memoire.verify_curated import check_esef_quote
    report = "Intensité des GES par chiffre d’affaires net tCO 2 e/M€ 345 352 2 Suite"
    q = "Intensité des GES par chiffre d’affaires net tCO 2 e/M€ 345 352"
    assert check_esef_quote(esef_row("ENV_GHG_INTENSITY", 352, q), report).status == "OK"
    assert check_esef_quote(esef_row("ENV_GHG_INTENSITY", 353, q), report).status == "ÉCART"


def test_esef_ecart_si_citation_absente_valeur_differente_ou_hors_sujet():
    from paris_memoire.verify_curated import check_esef_quote
    q = "L'écart de rémunération entre les femmes et les hommes au sein de Crédit Agricole S.A. est de 31,68 % en 2025"
    assert check_esef_quote(esef_row("LAB_GENDER_PAYGAP", 31.7, q), REPORT).status == "ÉCART"
    assert check_esef_quote(esef_row("LAB_GENDER_PAYGAP", 31.68, q.replace("31,68", "30,68")), REPORT).status == "ÉCART"
    assert check_esef_quote(esef_row("GOV_BOARD_INDEP", 31.68, q), REPORT).status == "ÉCART"


def test_hatvp_fiche_vide_est_un_ecart():
    r = row("la-nef", None, "Inscrite.", ind="GEO_LOBBYING_TRANSP", src="HATVP")
    assert check_hatvp(r, {"publicationCourante": {}, "exercices": []}, "339799116").status == "ÉCART"


def test_seul_un_ok_de_tier_1_2_sans_note_est_approuvable():
    from paris_memoire.verify_curated import Verdict, finalize
    ok = Verdict("OK", [])
    assert finalize(ok, "", "regulatory").status == "OK"
    assert finalize(ok, "", "audited_ngo").status == "OK"
    assert finalize(ok, "", "press").status == "JUGEMENT"      # rapport d'entreprise, presse
    assert finalize(ok, "", None).status == "JUGEMENT"         # tier inconnu : prudence
    assert finalize(ok, "définition voisine", "regulatory").status == "JUGEMENT"
    assert finalize(Verdict("ÉCART", []), "", "regulatory").status == "ÉCART"


def test_conversion_de_devise_au_taux_bce():
    from paris_memoire.verify_curated import check_esef_quote
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
    from paris_memoire.verify_curated import check_esef_quote, trend_score
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
    from paris_memoire.verify_curated import check_esef_quote
    rep = "Émissions totales de GES Location-Based 265,1 145,2 157,2 Émissions totales de GES Market-Based"
    q = "Émissions totales de GES Location-Based 265,1 145,2 157,2"
    calc = " ; rythme annuel moyen (2017 → 2025, 8 ans) : (145,2 / 265,1)^(1/8) − 1 = −7,25 %"
    x = row("x", -7.25, f"Rapport (Mt) : « {q} »{calc}", ind="ENV_GHG_TREND", src="ESEF")
    x.normalized_value = 1.0
    assert check_esef_quote(x, rep).status == "OK"


def test_rythme_avec_espaces_de_milliers():
    from paris_memoire.verify_curated import check_esef_quote
    rep = "Émissions totales de GES (scope 2 market-based) 622 429 747 810 658 455 - 11,9 %"
    q = "Émissions totales de GES (scope 2 market-based) 622 429 747 810 658 455"
    calc = " ; rythme annuel moyen (2018 → 2025, 7 ans) : (658455 / 622429)^(1/7) − 1 = 0,81 %"
    x = row("x", 0.81, f"DEU (colonnes 2018, 2024, 2025) : « {q} »{calc}", ind="ENV_GHG_TREND", src="AMF_BDIF")
    x.normalized_value = 0.0
    assert check_esef_quote(x, rep).status == "OK"


def test_delegation_tier3_seulement_si_verifie():
    from paris_memoire.verify_curated import Verdict, finalize
    ok = Verdict("OK", ["citation retrouvée ✓"])
    assert finalize(ok, "", "press").status == "JUGEMENT"                      # sans délégation : humain
    assert finalize(ok, "", "press", delegated=True).status == "OK-DÉLÉGUÉ"    # délégation : approuvable
    assert finalize(ok, "", "crowd", delegated=True).status == "JUGEMENT"      # jamais le tier crowd
    assert finalize(Verdict("ÉCART", []), "", "press", delegated=True).status == "ÉCART"
    assert finalize(ok, "note", "press", delegated=True).status == "JUGEMENT"  # jugement signalé : humain



def test_baisse_sur_un_an_refusee_hausse_acceptee():
    from paris_memoire.verify_curated import check_esef_quote
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
    from paris_memoire.verify_curated import check_esef_quote
    rep = "Director Nominee Highlights Board Composition 4 /10 women 6 /10 men 3 /10 members"
    q = "Director Nominee Highlights Board Composition 4 /10 women 6 /10 men"
    assert check_esef_quote(esef_row("GOV_BOARD_GENDER", 40.0, q), rep).status == "OK"
    assert check_esef_quote(esef_row("GOV_BOARD_GENDER", 45.0, q), rep).status == "ÉCART"



def test_rythme_depuis_une_variation_publiee():
    from paris_memoire.verify_curated import check_esef_quote
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
    from paris_memoire.verify_curated import check_esef_quote
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
    from paris_memoire.verify_curated import check_esef_quote
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
    from paris_memoire.verify_curated import check_esef_quote
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
    from paris_memoire.verify_curated import check_esef_quote
    rep = "Italian Competition Authority: Amazon fined over € 1,128 billion for abusing its dominant position"
    x = row("amazon", None, f"AGCM : « {rep} »", ind="GOV_SANCTIONS", src="IT_COMPETITION")
    x.value_numeric, x.value_text, x.normalized_value, x.nature = None, "amende de 1,13 Md€ (abus)", 0.9, "controversy"
    assert check_esef_quote(x, rep).status == "OK"


def test_montants_en_euros_toutes_ecritures():
    from paris_memoire.verify_curated import euro_amounts
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
    from paris_memoire.verify_curated import check_esef_quote
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
    from paris_memoire.verify_curated import check_esef_quote
    rep = ("The Board nominated each of the 10 incumbent directors listed here. The Director nominees vary in age "
           "from 59 to 70, include four women, and collectively bring a range of professional and life experiences")
    q = "The Board nominated each of the 10 incumbent directors listed here » ; « The Director nominees vary in age from 59 to 70, include four women"
    ok = row("mondelez", 40.0, f"Circulaire : « {q} » ; calcul : 4 / 10 = 40 %", ind="GOV_BOARD_GENDER", src="SEC_FILING")
    assert check_esef_quote(ok, rep).status == "OK"
    faux = row("mondelez", 50.0, f"Circulaire : « {q} » ; calcul : 5 / 10 = 50 %", ind="GOV_BOARD_GENDER", src="SEC_FILING")
    assert check_esef_quote(faux, rep).status == "ÉCART"   # « cinq » n'est pas cité


def test_note_normalisee_de_la_mixite_controlee():
    from paris_memoire.verify_curated import check_esef_quote
    rep = "Notre conseil compte 40 % de femmes administratrices."
    x = row("x", 40.0, "Rapport : « Notre conseil compte 40 % de femmes administratrices »", ind="GOV_BOARD_GENDER", src="ESEF")
    x.normalized_value = 0.8
    assert check_esef_quote(x, rep).status == "OK"
    x.normalized_value = 0.4   # 40 % rapporté à 100 au lieu de la parité
    assert check_esef_quote(x, rep).status == "ÉCART"


def test_plastique_vierge_rythme_classe_entre_pairs():
    from paris_memoire.verify_curated import check_esef_quote
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
    from paris_memoire.verify_curated import check_esef_quote
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
