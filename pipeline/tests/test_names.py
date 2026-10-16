from diams.normalize.names import best_match, is_strong_match, normalize_name


def test_normalize_strips_accents_suffixes_punct():
    assert normalize_name("Guccio Gucci S.p.A.") == "guccio gucci"
    assert normalize_name("LVMH Moët Hennessy Louis Vuitton SE") == "lvmh moet hennessy louis vuitton"
    assert normalize_name("Kering SA") == "kering"


def test_strong_match_equality_and_inclusion():
    assert is_strong_match("Kering SA", "KERING") is True
    assert is_strong_match("Guccio Gucci SpA", "GUCCIO GUCCI S.P.A.") is True
    # inclusion multi-mots tolérée
    assert is_strong_match("Hermès Sellier", "Hermès Sellier SAS") is True


def test_no_false_positive_on_single_token():
    # un mot unique ne doit pas matcher une entreprise homonyme
    assert is_strong_match("Hermès", "Hermes Microwave Components") is False
    assert is_strong_match("Kering", "L'Oréal") is False


def test_best_match_picks_only_clear():
    candidates = [{"nom": "Société Anonyme XYZ"}, {"nom": "Christian Dior Couture SE"}]
    assert best_match("Christian Dior Couture", candidates, "nom")["nom"] == "Christian Dior Couture SE"
    assert best_match("Balenciaga", candidates, "nom") is None


def test_sigles_a_esperluette_conserves():
    # 16/10/2026 : « H&M Group » et « B&S Group » se réduisaient tous deux à « group ».
    from diams.normalize.names import normalize_name, is_strong_match
    assert normalize_name("H&M Group") == "hm group"
    assert normalize_name("B&S Group S.A.") == "bs group"
    assert normalize_name("AT&T Inc.") == "att"
    assert normalize_name("Barilla S.p.A.") == "barilla"
    assert not is_strong_match("H&M Group", "B&S Group S.A.")
    assert is_strong_match("H&M Group", "H&M Group AB")


def test_nom_generique_ne_correspond_a_rien():
    from diams.normalize.names import is_strong_match
    assert not is_strong_match("Group", "Groupe")
    assert not is_strong_match("International Holding", "International Holding")


def test_lettres_isolees_differentes():
    from diams.normalize.names import is_strong_match
    assert not is_strong_match("Bio-D", "U BIO")
    assert is_strong_match("E.Leclerc", "Leclerc")
