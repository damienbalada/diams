from diams.paradis_europe import compter


def _table(*rows):
    return "<table>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</table>"


def test_decompte_des_filiales_et_exclusions():
    raw = _table(
        ["Pernod Ricard Nederland BV", "Pays-Bas", "100", "100"],          # compte
        ["Exane Solutions Luxembourg SA", "Luxembourg", "IG", "100,0 %"],  # compte
        ["BNPP SA (succ. Hong Kong)", "Hong Kong", "IG", "100,0 %"],       # succursale : exclue
        ["Bonny Gas Transport Limited", "15,00%", "E", "Bermudes"],        # mise en équivalence : exclue
        ["Brass Holdings B.V.", "100,00%", "Nigéria", "Pays-Bas"],         # immatriculée au Nigéria : exclue
        ["En millions de dollars américains", "750", "5,250%", "Luxembourg"],  # emprunt : exclu
        ["Brice Thommen", "46", "M", "Suisse"],                           # personne : exclue
        ["Pernod Ricard Nederland BV", "Pays-Bas", "100", "100"],          # doublon : exclu
        ["Heineken Nederland B.V.", "The Netherlands", "100.0", "100.0"],  # compte (sauf siège NL)
    )
    n, cit, lignes = compter(raw, "FR")
    assert dict(n) == {"NL": 2, "LU": 1}
    assert cit["NL"][0] == "Pernod Ricard Nederland BV Pays-Bas"
    n_nl, _, _ = compter(raw, "NL")
    assert dict(n_nl) == {"LU": 1}
