import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "outils_collecte"))
import compositions as C  # noqa: E402


def test_matieres_animales():
    a = C.analyse("Extérieur : 80 % laine, 20 % polyamide. Doublure : 100 % soie")
    assert a["animaux"] == ["laine", "soie"]
    assert a["statut"] == "ingredient_animal"


def test_imitations_ecartees():
    for t in ["100 % polyester (laine polaire)", "Dessus : similicuir 100 % polyuréthane", "Fausse fourrure 100 % acrylique",
              "Tissu peau de pêche 100 % coton", "Effet cuir : 100 % polyuréthane", "Garnissage synthétique, sans duvet ni plumes"]:
        assert C.analyse(t)["animaux"] == [], t


def test_duvet_et_plumes():
    a = C.analyse("Garnissage : 90 % duvet de canard, 10 % plumes")
    assert a["animaux"] == ["duvet", "plumes"]


def test_coton_seul():
    a = C.analyse("100 % coton biologique")
    assert a["statut"] == "aucun_ingredient_animal_declare"


def test_bloc_composition():
    page = ("Pull col rond Nouveautés Matières Laine Coton Description Un pull doux. Composition : 70 % laine, "
            "30 % cachemire Entretien Lavage à la main à 30 °C Livraison offerte")
    assert C.bloc_composition(page) == "70 % laine, 30 % cachemire"


def test_bloc_absent_sans_pourcentage():
    assert C.bloc_composition("Matières : découvrez nos matières naturelles et responsables Livraison") is None


def test_fin_de_bloc_dim():
    page = "Composition 87% Polyamide, 13% Elasthanne Qualités et caractéristiques environnementales Fiche produit"
    assert C.bloc_composition(page) == "87% Polyamide, 13% Elasthanne"
    assert C.bloc_composition("Composition 96% Coton, 4% Elasthanne 40°C Lavage") == "96% Coton, 4% Elasthanne"


def test_intitules_retires():
    page = "Composition et entretien Matières Matière principale : 84 % polyester, 16 % élasthanne Instructions de lavage"
    assert C.bloc_composition(page) == "Matière principale : 84 % polyester, 16 % élasthanne"
