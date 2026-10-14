"""Connecteur BDIF : DEU de l'exercice, émetteur exact."""
from diams.connectors import bdif


class _Resp:
    def __init__(self, data):
        self._d = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._d


class _Client:
    def __init__(self, data):
        self.data = data

    def get(self, *a, **k):
        return _Resp(self.data)


def item(numero, year, issuer, types=("DocumentEnregistrementUniversel",)):
    return {"numero": numero, "anneeComptable": year, "dateAction": "2026-03-19T00:00:00", "typesDocument": list(types),
            "societes": [{"raisonSociale": issuer, "role": "Emetteur"}],
            "documents": [{"format": "PDF", "accessible": True, "path": f"2026/{numero}/abc.pdf"},
                          {"format": "ZIP", "accessible": True, "path": f"2026/{numero}/esef.zip"}]}


def test_exercice_et_emetteur_exacts():
    data = {"result": [item("D.26-0114", 2025, "HERMES INTERNATIONAL"), item("D.25-0165", 2024, "HERMES INTERNATIONAL"),
                       item("D.26-0592", 2025, "MAISON POMMERY & ASSOCIES"), item("26-0072", 2025, "X", ("Prospectus",))]}
    res = bdif.find_urd("HERMES", 2025, _Client(data), issuer="Hermes International")
    assert [u.number for u in res] == ["D.26-0114"]
    assert res[0].pdf_url.endswith("/documents/2026/D.26-0114/abc.pdf") and res[0].filed == "2026-03-19"
    assert res[0].esef_url.endswith("/documents/2026/D.26-0114/esef.zip")
