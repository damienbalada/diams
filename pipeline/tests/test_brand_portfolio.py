from paris_memoire.import_brand_portfolio import check_rows, name_in_quote, quote_in_document


def test_nom_de_marque_en_mot_entier_casse_et_accents_ignores():
    q = "Nos marques : Côte d'Or, Milka, LU, Prince et Petit Écolier"
    assert name_in_quote("Cote d’Or", q)
    assert name_in_quote("Petit Ecolier", q)
    assert name_in_quote("lu", q)
    assert not name_in_quote("Lustucru", q)
    assert not name_in_quote("Prin", q)
    assert name_in_quote("Ben & Jerry's", "brands such as Ben and Jerry's and Magnum")


def test_citation_retrouvee_malgre_les_espaces_de_mise_en_page():
    assert quote_in_document("Nos marques : Milka, LU", "… Nos mar ques : Milka,  LU …")
    assert not quote_in_document("Nos marques : Milka, Oreo", "Nos marques : Milka, LU")


def _row(**kw):
    base = {"brand_slug": "milka", "brand_name": "Milka", "group_slug": "mondelez", "sector_code": "food",
            "source_kind": "legal", "source_url": "u", "doc": "d", "quote": "Milka, LU", "observed_on": "2026-01-01"}
    return {**base, **kw}


def test_conflit_si_la_marque_appartient_a_un_autre_groupe():
    ents = {"mondelez": {"id": "g1", "slug": "mondelez", "is_brand": False, "parent_id": None},
            "nestle": {"id": "g2", "slug": "nestle", "is_brand": False, "parent_id": None},
            "milka": {"id": "b1", "slug": "milka", "is_brand": True, "parent_id": "g2"}}
    res = check_rows([_row()], ents, {"food": "s"}, lambda u: "Nos marques : Milka, LU")
    assert res[0][1] == "CONFLIT"


def test_ecart_si_la_marque_n_est_pas_dans_la_citation_ou_le_document():
    ents = {"mondelez": {"id": "g1", "slug": "mondelez", "is_brand": False, "parent_id": None}}
    res = check_rows([_row(brand_name="Oreo", brand_slug="oreo")], ents, {"food": "s"}, lambda u: "Milka, LU")
    assert res[0][1] == "ÉCART"
    res = check_rows([_row()], ents, {"food": "s"}, lambda u: "autre texte")
    assert res[0][1] == "ÉCART"
    res = check_rows([_row()], ents, {"food": "s"}, lambda u: "… Milka, LU …")
    assert res[0][1] == "OK"


def test_signes_de_marque_deposee_ignores():
    assert name_in_quote("Ben's Original", "brands like Ben’s Original™, Dolmio ®")
    assert name_in_quote("Dolmio", "brands like Ben’s Original™, Dolmio®")
