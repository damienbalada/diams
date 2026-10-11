"""Connecteur SEC : identité par le nom déposé, taux effectif balisé et contrôlé."""
from paris_memoire.connectors.sec import effective_tax_rate, norm
from paris_memoire.import_sec import same_company


def fact(val, end, start, form="10-K", filed="2026-02-01", accn="0000-26-1"):
    return {"val": val, "end": end, "start": start, "form": form, "filed": filed, "accn": accn}


def facts(rate, tax, pbt):
    us = {
        "EffectiveIncomeTaxRateContinuingOperations": {"units": {"pure": rate}},
        "IncomeTaxExpenseBenefit": {"units": {"USD": tax}},
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest": {"units": {"USD": pbt}},
    }
    return {"facts": {"us-gaap": us}}


def test_noms_comparables_sans_forme_juridique_ni_ponctuation():
    assert norm("MCDONALDS CORP") == norm("McDonald's Corporation")
    assert norm("PROCTER & GAMBLE Co") == norm("The Procter & Gamble Company")
    assert norm("COCA COLA CO") == norm("THE COCA-COLA COMPANY")
    assert same_company("google", "Alphabet Inc.", ["Alphabet Inc. (Google)"])
    assert not same_company("apple", "Apple Hospitality REIT, Inc.", ["Apple Inc."])


def test_taux_du_dernier_exercice_controle():
    f = facts([fact(0.241, "2024-12-31", "2024-01-01"), fact(0.156, "2025-12-31", "2025-01-01")],
              [fact(2400, "2024-12-31", "2024-01-01"), fact(1560, "2025-12-31", "2025-01-01")],
              [fact(10000, "2024-12-31", "2024-01-01"), fact(10000, "2025-12-31", "2025-01-01")])
    tr = effective_tax_rate(f)
    assert tr is not None and tr.rate_pct == 15.6 and tr.fy_end == "2025-12-31"


def test_taux_incoherent_ou_trimestriel_ou_perte_ecarte():
    y = ("2025-12-31", "2025-01-01")
    assert effective_tax_rate(facts([fact(0.156, *y)], [fact(3000, *y)], [fact(10000, *y)])) is None   # 15,6 ≠ 30
    q = ("2025-12-31", "2025-10-01")
    assert effective_tax_rate(facts([fact(0.156, *q)], [fact(1560, *q)], [fact(10000, *q)])) is None   # trimestre
    assert effective_tax_rate(facts([fact(0.1, *y)], [fact(-100, *y)], [fact(-1000, *y)])) is None    # perte
