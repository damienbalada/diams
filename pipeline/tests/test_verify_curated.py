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
