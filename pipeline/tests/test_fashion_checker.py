from diams.import_fashion_checker import ALIASES, SCALE, build_row, parse_answers

PAYLOAD = {"items": [
    {"company": "H&M", "year": 2026, "value": "E"},
    {"company": "Puma", "year": 2026, "value": "D"},
    {"company": "Devold of Norway AS", "year": 2026, "value": "B"},
    {"company": "H&M", "year": 2025, "value": "A"},          # autre année : ignorée
    {"company": "Inconnue", "year": 2026, "value": "Unknown"},  # hors barème : ignorée
]}


def test_lettres_et_annee():
    a = parse_answers(PAYLOAD, 2026)
    assert set(a) == {"H&M", "Puma", "Devold of Norway AS"}
    assert a["H&M"]["value"] == "E"


def test_bareme_e_vaut_zero():
    assert SCALE == {"A": 1.0, "B": 0.75, "C": 0.5, "D": 0.25, "E": 0.0}
    row = build_row("hm-group", "H&M", {"value": "E", "year": 2026}, "2026-09-14")
    assert row.indicator_code == "SUP_LIVING_WAGE" and row.normalized_value == 0.0
    assert row.source_code == "CCC" and row.observed_on == "2026-09-14"
    assert "« H&M » — note E" in row.excerpt and "aucun de ses travailleurs" in row.excerpt


def test_alias_exacts_sans_doublon():
    assert ALIASES["H&M"] == "hm-group"   # la note du groupe vaut pour ses marques
    assert len(set(ALIASES.values())) == len(ALIASES)
