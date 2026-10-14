"""Connecteur Finansol : lecture de la liste FAIR et rattachement strict."""
from diams.connectors.finansol import Product, by_entity, parse_page
from diams.import_finansol import build_rows

PAGE = """
<li  class="entity-list-item products-item"><div class="item-card">
  <a href="/fr/produits/livret-agir" title="x"></a>
  <p class="item-card-product-manager item-card-text-small">Géré par : <span class="item-card-text-highlight">Crédit Coopératif</span></p>
  <p class="item-card-product-distributor item-card-text-small item-card-top">Distribué par : <span class="item-card-text-highlight">  Crédit Coopératif
  </span></p>
  <h3 class="item-card-title"><span class="field field--name-title field--type-string field--label-hidden">Livret Agir</span></h3>
  <p class="item-card-type">Produit bancaire</p>
</div></li>
<li  class="entity-list-item products-item"><div class="item-card">
  <a href="/fr/produits/fcp-solidarite" title="x"></a>
  <p class="item-card-product-distributor item-card-text-small item-card-top">Distribué par : <span class="item-card-text-highlight">Amundi</span></p>
  <h3 class="item-card-title"><span class="field field--name-title field--type-string field--label-hidden">FCP Solidarité</span></h3>
</div></li>
"""


def test_lecture_d_une_page():
    prods = parse_page(PAGE)
    assert [p.title for p in prods] == ["Livret Agir", "FCP Solidarité"]
    assert prods[0].distributor == "Crédit Coopératif"
    assert prods[0].url.endswith("/fr/produits/livret-agir")


def test_rattachement_strict_pas_de_filiale_de_gestion():
    grouped = by_entity(parse_page(PAGE))
    assert set(grouped) == {"credit-cooperatif"}  # Amundi n'est pas rattachée au Crédit Agricole


def test_distributeur_commun_rattache_aux_deux():
    p = Product(title="Livret", url="u", distributor="Crédit Mutuel / CIC", manager="", kind="")
    assert set(by_entity([p])) == {"credit-mutuel-alliance-federale", "cic"}


def test_preuve_positive_seulement():
    rows = build_rows(by_entity(parse_page(PAGE)), "2026-10-11")
    assert len(rows) == 1 and rows[0].value_boolean is True and "Livret Agir" in rows[0].excerpt
