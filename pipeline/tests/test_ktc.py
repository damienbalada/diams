from diams.connectors import benchmarks as bm
from diams.import_ktc import build_row, match_group

HTML = (
    '<script>var _Flourish_data = {"data":['
    '{"color_category":"Danone","filter":"2025-2026","metadata":["u","19","12","T1","x","44"]},'
    '{"color_category":"Danone","filter":"2022-2023","metadata":["u","22","9","T1","x","60"]},'
    '{"color_category":"Danone","filter":"2018","metadata":["u","40","3","T1","x","43"]},'
    '{"color_category":"Coca-Cola","filter":"2022-2023","metadata":["u","29","7","T1","x","60"]}'
    ']},\n_Flourish_data_column_names = {"data":{"metadata":'
    '["company_dashboard","Total Score","Rank","T1_name","T1","benchmark_size"]}},\n'
    '_Flourish_x = 1;</script>'
)


def test_parse_and_latest_edition():
    rows = bm.parse_ktc_flourish(HTML, "fb")
    assert [(r.company, r.edition) for r in rows] == [
        ("Danone", "2025-2026"), ("Danone", "2022-2023"), ("Coca-Cola", "2022-2023")]  # 2018 ignorée
    latest = bm.latest_ktc(rows)
    assert latest["Danone"].score == 19 and latest["Danone"].published == 2026
    assert latest["Danone"].rank == 12 and latest["Danone"].size == 44
    assert latest["Coca-Cola"].score == 29


def test_latest_across_benchmarks():
    a = bm.KtcScore("Amazon.com", "af", "2022-2023", 2023, 32, None, None)
    b = bm.KtcScore("Amazon.com", "ict", "2025-2026", 2025, 27, None, None)
    assert bm.latest_ktc([a, b])["Amazon.com"].score == 27


def test_match_groups_only_and_aliases():
    groups = [{"slug": "coca-cola", "display_name": "The Coca-Cola Company", "legal_name": "The Coca-Cola Company"},
              {"slug": "danone", "display_name": "Danone", "legal_name": "Danone SA"},
              {"slug": "hm-group", "display_name": "H&M", "legal_name": "H & M Hennes & Mauritz AB"}]
    assert match_group("Coca-Cola", groups)["slug"] == "coca-cola"
    assert match_group("Danone", groups)["slug"] == "danone"
    assert match_group("Hennes & Mauritz (H&M)", groups)["slug"] == "hm-group"
    assert match_group("Coca-Cola HBC AG", groups) is None


def test_row_excerpt_and_values():
    s = bm.KtcScore("Danone", "fb", "2025-2026", 2026, 19, 12, 44)
    r = build_row("danone", s)
    assert r.normalized_value == 0.19 and r.value_numeric == 19 and r.observed_on == "2026-01-01"
    assert "rang 12 sur 44" in r.excerpt and "« Danone »" in r.excerpt
