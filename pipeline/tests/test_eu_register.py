from paris_memoire.connectors import eu_register as eu
from paris_memoire.import_eu_register import match, rows_for
from paris_memoire.normalize.names import normalize_name

XML = b"""<?xml version='1.1' encoding='UTF-8'?>
<ListOfIRPublicDetail xmlns="http://intragate.ec.europa.eu/transparencyregister/odp">
  <metaData xmlns=""><exportDate>2026-10-10T20:00:00.081+00:00</exportDate></metaData>
  <resultList xmlns="">
    <interestRepresentative>
      <identificationCode>1849405799-88</identificationCode>
      <lastUpdateDate>2025-12-11T13:19:23.434+00:00</lastUpdateDate>
      <name><originalName>TotalEnergies SE</originalName></name>
      <webSiteURL>https://www.totalenergies.com/</webSiteURL>
      <registrationCategory>Companies &amp; groups</registrationCategory>
      <goals>Texte libre avec un caract&#x1;re de contr&#5;le.</goals>
      <members><membersFTE>4.25</membersFTE></members>
      <financialData><closedYear><startDate>2024-01-01</startDate><endDate>2024-12-01</endDate>
        <costs type="CostRange" currency="&#8364;"><range><min>3000000</min><max>3499999</max></range></costs>
      </closedYear></financialData>
    </interestRepresentative>
    <interestRepresentative>
      <identificationCode>1-1</identificationCode>
      <name><originalName>FuelsEurope</originalName></name>
      <registrationCategory>Trade and business associations</registrationCategory>
    </interestRepresentative>
  </resultList>
</ListOfIRPublicDetail>"""


def test_parse_xml11_companies_only():
    date, regs = eu.parse_export(XML)
    assert date == "2026-10-10"
    assert [r.name for r in regs] == ["TotalEnergies SE"]          # la fédération est écartée
    r = regs[0]
    assert (r.cost_min, r.cost_max, r.cost_mid, r.fte, r.year_start) == (3000000, 3499999, 3249999.5, 4.25, "2024-01-01")


def test_rows_and_matching():
    _d, regs = eu.parse_export(XML)
    by_name = {r.name: [r] for r in regs}
    by_norm = {normalize_name(r.name): [r] for r in regs}
    assert match("totalenergies", ["TotalEnergies"], by_name, by_norm).code == "1849405799-88"
    assert match("sony", ["Sony"], by_name, by_norm) is None
    transp, spend = rows_for("totalenergies", regs[0], "2026-10-10")
    assert transp.normalized_value == 1.0 and spend.normalized_value is None
    assert spend.value_numeric == 3249999.5
    assert "3 000 000 € à 3 499 999 €" in spend.excerpt and "4,25 équivalents temps plein" in spend.excerpt
