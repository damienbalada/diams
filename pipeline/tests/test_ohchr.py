"""Base du HCDH : lecture de l'annexe et correspondance exacte des noms."""
from diams.import_ohchr import match, parse_annex

ANNEX = """Annex I Business enterprises involved in listed activities
No. Business enterprise Listed activity Home State
5 Airbnb Inc. (e) United States of America 6 Alon Blue Square Israel Ltd. (e), (g) Israel
27 Booking Holdings Inc. (e) United States of America 52 Egis (e) France 53 Egis Rail (e) France
Annex II Removed"""


def test_lecture_de_l_annexe():
    rows = parse_annex(ANNEX)
    names = [n for n, _ in rows]
    assert "Airbnb Inc." in names and "Booking Holdings Inc." in names and "Egis Rail" in names
    assert dict(rows)["Egis"] == "France"


def test_correspondance_exacte_seulement():
    ents = [{"slug": "airbnb", "display_name": "Airbnb", "legal_name": "Airbnb, Inc."},
            {"slug": "booking-x", "display_name": "Booking Express"}]
    hits = match(parse_annex(ANNEX), ents)
    assert [e["slug"] for e, _, _ in hits] == ["airbnb"]  # « Booking Express » ≠ « Booking Holdings »
