"""Lecture des ingrédients des fiches produits (outil d'essai outils_collecte/ingredients.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "outils_collecte"))
import ingredients as I  # noqa: E402


def test_bloc_s_arrete_a_la_rubrique_suivante():
    t = ("Ingrédients : Sucre, amidon modifié, gélifiant: carraghénanes, arôme. Produit en France. "
         "UTILISATION Versez la crème liquide bien froide")
    b = I.bloc_ingredients(t)
    assert b.endswith("Produit en France.")
    assert I.analyse(b)["statut"] == "aucun_ingredient_animal_declare"


def test_texte_qui_n_est_pas_une_liste_ecarte():
    assert I.bloc_ingredients("Ingrédients sélectionnés 100 % végétal, pauvre en acides gras, et lait d'amande, etc.") is None


def test_ingredients_animaux_hors_traces_et_vegetaux():
    a = I.analyse("Sucre, lait écrémé en poudre, beurre de cacao, lécithine. Peut contenir des traces d'œufs.")
    assert a["animaux"] == ["lait"] and a["statut"] == "ingredient_animal"
    assert I.analyse("Eau, amandes 2 %, sel. Lait d'amande sans lactose, beurre de karité.")["animaux"] == []


def test_ingredients_douteux_signales_sans_conclure():
    a = I.analyse("Sucre, sirop de glucose, arôme naturel, vitamine D3.")
    assert a["statut"] == "aucun_ingredient_animal_declare" and "vitamine d3" in a["douteux"]


def test_liste_en_minuscule_acceptee_presentation_ecartee():
    assert I.bloc_ingredients("Ingrédients : farine de blé* 40%, sucre, miel* 12%, oeufs frais. *bio") is not None
    assert I.bloc_ingredients("Ingrédients pour satisfaire les palais exigeants des bébés. Blédichef, c'est aussi : du poisson, des légumes, etc.") is None


def test_description_sans_ingredient_ecartee():
    t = "Ingrédients Des belles airelles cueillies au bon moment, choisies avec soin et triées à la main, à déguster"
    assert I.bloc_ingredients(t) is None
