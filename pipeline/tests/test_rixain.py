from diams.connectors.rixain import RixainRecord, latest_by_siren, _pct
from diams.import_rixain import build_rows


def test_derniere_declaration_calculee():
    recs = [RixainRecord(2024, "552032534", "DANONE", 50.0, 25.0),
            RixainRecord(2025, "552032534", "DANONE", 50.32, 26.09),
            RixainRecord(2026, "552032534", "DANONE", 51.0, None)]   # « NC » : ignorée
    best = latest_by_siren(recs)
    assert best["552032534"].year == 2025 and best["552032534"].membres_f == 26.09
    assert _pct("NC") is None and _pct(33) == 33.0


def test_preuve_instances_dirigeantes_et_non_conseil():
    rec = RixainRecord(2025, "552032534", "DANONE", None, 26.09)
    (r,) = build_rows([{"slug": "danone", "siren": "552032534"}, {"slug": "x", "siren": None}], {"552032534": rec})
    assert r.indicator_code == "GOV_EXEC_GENDER" and r.source_code == "RIXAIN"
    assert r.observed_on == "2026-03-01" and r.value_numeric == 26.09
    assert "26,09 % de femmes parmi les membres des instances dirigeantes" in r.excerpt
    assert "non calculable (NC) parmi les cadres dirigeants" in r.excerpt
