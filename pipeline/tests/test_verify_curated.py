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
