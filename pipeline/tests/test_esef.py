"""Connecteur ESEF : faits IFRS de l'exercice, taux effectif contrôlé, citation CbCR."""
from diams.connectors.esef import annual_currency, annual_facts, cbcr_quote, effective_tax_rate

Y25 = "2025-01-01T00:00:00/2026-01-01T00:00:00"
Y24 = "2024-01-01T00:00:00/2025-01-01T00:00:00"


def fact(concept, period, value, **dims):
    return {"value": value, "dimensions": {"concept": concept, "period": period, "unit": "iso4217:EUR", **dims}}


XBRL = {"facts": {
    "a": fact("ifrs-full:ProfitLossBeforeTax", Y25, "17065000000"),
    "b": fact("ifrs-full:IncomeTaxExpenseContinuingOperations", Y25, "4207000000"),
    "c": fact("ifrs-full:ProfitLoss", Y25, "12858000000"),
    "d": fact("ifrs-full:ProfitLoss", Y25, "633000000", **{"ifrs-full:ComponentsOfEquityAxis": "ifrs-full:NoncontrollingInterestsMember"}),
    "e": fact("ifrs-full:ProfitLossBeforeTax", Y24, "16188000000"),
}}


def test_faits_de_l_exercice_sans_dimension():
    f = annual_facts(XBRL, "2025-12-31")
    assert f == {"pbt": 17065000000.0, "tax": 4207000000.0, "net": 12858000000.0}


def test_avant_impot_non_balise_reconstitue_et_signale():
    tr = effective_tax_rate({"tax": 2363.1, "net": 6133.7})
    assert tr is not None and tr.derived and tr.rate_pct == 27.8 and round(tr.pbt, 1) == 8496.8
    tr = effective_tax_rate({"tax": 574.0, "net": 1674.0, "disc": 0.0})
    assert tr is not None and tr.rate_pct == 25.5
    # charge d'impôt négative ou perte : ambigu, rien n'est publié
    assert effective_tax_rate({"tax": -100.0, "net": 900.0}) is None
    assert effective_tax_rate({"tax": 50.0, "net": -900.0}) is None
    assert effective_tax_rate({"tax": 900.0, "net": 100.0}) is None   # 90 % : implausible


def test_extrait_dit_que_le_sous_total_est_reconstitue():
    from diams.connectors.esef import Filing
    from diams.import_esef import tax_rate_row
    f = Filing("X", "2025-12-31", "2026-03-24", "j", None, "v", 0)
    row = tax_rate_row("loreal", f, effective_tax_rate({"tax": 2363.1e6, "net": 6133.7e6}), "EUR")
    assert "reconstitué" in row.excerpt and "27,8 %" in row.excerpt


def test_taux_effectif_avec_controle_d_integrite():
    tr = effective_tax_rate(annual_facts(XBRL, "2025-12-31"))
    assert tr is not None and tr.rate_pct == 24.7


def test_devise_lue_dans_le_balisage_jamais_supposee():
    assert annual_currency(XBRL, "2025-12-31") == "EUR"
    usd = {"facts": {"a": {"value": "1", "dimensions": {"concept": "ifrs-full:ProfitLossBeforeTax", "period": Y25, "unit": "iso4217:USD"}}}}
    assert annual_currency(usd, "2025-12-31") == "USD"
    assert annual_currency({"facts": {}}, "2025-12-31") is None


def test_extrait_libelle_dans_la_devise_du_rapport():
    from diams.connectors.esef import Filing, TaxRate
    from diams.import_esef import tax_rate_row
    f = Filing("X", "2025-12-31", "2026-03-01", "j", None, "v", 0)
    row = tax_rate_row("shell", f, TaxRate(39.1, 29756e6, 11635e6, 18121e6), "USD")
    assert "29 756 M$" in row.excerpt and "M€" not in row.excerpt


def test_charge_d_impot_signee_negativement():
    tr = effective_tax_rate({"pbt": 1000.0, "tax": -250.0, "net": 750.0})
    assert tr is not None and tr.rate_pct == 25.0 and tr.tax == 250.0


def test_triplet_incoherent_ou_perte_rejete():
    assert effective_tax_rate({"pbt": 1000.0, "tax": 250.0, "net": 900.0}) is None
    assert effective_tax_rate({"pbt": -100.0, "tax": 10.0, "net": -110.0}) is None
    assert effective_tax_rate({"pbt": 1000.0}) is None


BNP_TOC = ("8.5 Investissements 8.6 Informations sur les implantations et les activités relatives à l'exercice 2025 "
           "8.7 Actes constitutifs et statuts 8.8 Rapport spécial. ")
BNP_CONCORDANCE = ("Informations sur les implantations et les activités de la Société (L. 511-45 et R. 511-16-4 du Code "
                   "monétaire et financier) 316-333 ; 898-914 II. Facteurs de risques. ")
BNP_SECTION = ("8.6 Informations sur les implantations et les activités relatives à l'exercice 2025 Conformément à "
               "l'article L.511-45 du Code monétaire et au décret n° 2014-1657 du 29 décembre 2014, les établissements "
               "de crédit doivent publier des informations sur leurs implantations. Suite du texte.")


def test_citation_cbcr_vise_la_section_pas_le_sommaire_ni_la_concordance():
    q = cbcr_quote(BNP_TOC + BNP_CONCORDANCE + BNP_SECTION)
    assert q and q.startswith("8.6 Informations sur les implantations") and "Conformément" in q


def test_citation_cbcr_redactions_variees():
    lbp = ("4.9.9 Informations relatives aux implantations et activités au 31 décembre 2025 L'article L. 511-45 du "
           "Code monétaire et financier impose aux établissements de crédit de publier des informations. Fin.")
    arkea = ("Informations relatives aux implantations et activités incluses dans le périmètre de consolidation au "
             "31 décembre 2025 Les principales informations relatives aux implantations agrégées à l'échelle des "
             "États et territoires sont les suivantes. Fin.")
    bpce = "12.6.2. Implantation des entités pays par pays PAYS D'IMPLANTATION Activités ALGÉRIE NATIXIS ALGERIE Banque."
    for t in (lbp, arkea, bpce):
        assert cbcr_quote(t) is not None, t[:40]


def test_citation_cbcr_renvoi_ignore_au_profit_de_la_section():
    t = ("Les informations relatives aux implantations et activités au 31 décembre 2025 sont disponibles en section "
         "4.9.9 du présent document. Autre texte. 4.9.9 Informations relatives aux implantations et activités au 31 "
         "décembre 2025 L'article L. 511-45 du Code monétaire et financier impose aux établissements de crédit de "
         "publier des informations. Fin.")
    assert cbcr_quote(t).startswith("4.9.9 Informations relatives")


def test_citation_cbcr_redigee_dans_une_phrase():
    ca = ("Les informations prévues par la loi, complétées par le décret n° 2014-1657 du 29 décembre 2014, pris pour "
          "l'application de l'article L. 511-45 du Code monétaire et financier, sont détaillées ci-après. Ces "
          "informations publiées portent sur les implantations et activités incluses dans le périmètre. Fin.")
    q = cbcr_quote(ca)
    assert q and "L. 511-45" in q and "implantations et activités" in q


def test_citation_cbcr_absente():
    assert cbcr_quote("Le texte cite l'article L. 511-45 à propos des territoires non coopératifs. Fin.") is None
    assert cbcr_quote(BNP_TOC + BNP_CONCORDANCE) is None
