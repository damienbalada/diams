

def test_comite_sans_organisation_declaree():
    from diams.import_fec import committee_company, same_company
    assert committee_company("KEURIG DR PEPPER INC. PAC") == "KEURIG DR PEPPER INC"
    assert same_company("Yum! Brands", committee_company("YUM BRANDS INC. GOOD GOVERNMENT FUND"))
    assert same_company("Amazon", committee_company("AMAZON.COM SERVICES LLC SEPARATE SEGREGATED FUND (AMAZON PAC)"))
    assert not same_company("Mars", committee_company("MARSH & MCLENNAN COMPANIES, INC. POLITICAL ACTION COMMITTEE (MARSH PAC)"))


def test_apostrophe():
    from diams.import_fec import same_company
    assert same_company("McDonald's", "MCDONALDS CORPORATION")
    assert not same_company("McDonald's", "MCDONALD HOPKINS LLC")
