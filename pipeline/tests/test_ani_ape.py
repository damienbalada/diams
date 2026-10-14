from paris_memoire.import_ani_ape import ape_is_animal, build_rows, parse_avis

AVIS = ("Identifiant SIREN 783 423 270 Dénomination UNION LAITIERE VITTELLOISE Catégorie juridique 6317 - "
        "Société coopérative agricole Activité Principale Exercée (APE) 10.51C - Fabrication de fromage "
        "Appartenance au champ de l’ESS1 Oui")


def test_codes_animaux():
    for code in ["10.51C", "10.13B", "10.11Z", "10.20Z", "01.47Z", "03.21Z", "46.38A", "47.22Z"]:
        assert ape_is_animal(code), code
    for code in ["10.52Z", "46.33Z", "10.85Z", "10.72Z", "70.10Z", "10.51E", None, ""]:
        assert not ape_is_animal(code), code


def test_ligne_ape_lue_mot_pour_mot():
    assert parse_avis(AVIS) == ("10.51C", "Fabrication de fromage")
    assert parse_avis("aucune activité") is None


def test_societe_et_marques_directes_hors_vegetales_et_deja_documentees():
    co = {"id": "c1", "slug": "ulv", "legal_name": "UNION LAITIERE VITTELLOISE", "siren": "783423270"}
    brands = {"c1": [{"id": "b1", "slug": "ermitage"}, {"id": "b2", "slug": "vegetal", "animal_free": True},
                     {"id": "b3", "slug": "deja"}]}
    avis = {"783423270": ("10.51C", "Fabrication de fromage", "https://exemple/avis.pdf")}
    rows = build_rows([co], brands, avis, documented={"deja"}, today="2026-10-14")
    assert [r.entity_slug for r in rows] == ["ulv", "ermitage"]
    assert all(r.normalized_value == 0.0 and r.source_code == "INPI_SIRENE" for r in rows)
    assert "« Activité Principale Exercée (APE) 10.51C - Fabrication de fromage »" in rows[1].excerpt
    assert "propriétaire de la marque" in rows[1].excerpt


def test_activite_non_animale_ignoree():
    co = {"id": "c1", "slug": "biscuits", "siren": "1"}
    assert build_rows([co], {}, {"1": ("10.72Z", "Fabrication de biscuits", "u")}, set(), "2026-10-14") == []
