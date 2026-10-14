from diams.connectors import bbfaw
from diams.import_bbfaw import build_row, match_group


class FakePage:
    """Page PDF minimale : (x, y, texte) restitués au visiteur comme pypdf."""

    def __init__(self, items):
        self.items = items

    def extract_text(self, visitor_text=None):
        for x, y, t in self.items:
            visitor_text(t, None, [1, 0, 0, 1, x, y], None, 9)
        return ""


PAGE = FakePage([
    (131, 707, "Tier 2"), (131, 654, "1"), (217, 654, "1"), (388, 654, "2"), (473, 654, "1"),
    (129, 642, "Greggs PLC   C"),
    (214, 642, "Groupe Danone SA  C"),
    (385, 642, "2 Sisters Food Group   F"), (385, 636, "(Boparan Holdings Ltd)"),
    (385, 626, "Nestlé SA"), (430, 626, "F"),          # note d'impact séparée : ignorée
    (471, 642, "Starbucks Corporation  F"),
    (471, 12, "The arrows indicate the change"),         # note de bas de page : hors cadre
])


def test_columns_continuations_and_marks():
    entries = bbfaw.parse_figure(PAGE)
    assert [(e.company, e.tier) for e in entries] == [
        ("Greggs PLC", 2), ("Groupe Danone SA", 3),
        ("2 Sisters Food Group (Boparan Holdings Ltd)", 5), ("Nestlé SA", 5),
        ("Starbucks Corporation", 6)]
    assert bbfaw.parse_counts(PAGE) == {2: 1, 3: 1, 5: 2, 6: 1}
    assert bbfaw.check(entries, {"Nestlé SA": 5}, bbfaw.parse_counts(PAGE)) == []


def test_check_reports_mismatch():
    entries = bbfaw.parse_figure(PAGE)
    issues = bbfaw.check(entries, {"Nestlé SA": 4}, {2: 1, 3: 1, 5: 3, 6: 1})
    assert any("Nestlé SA" in i for i in issues) and any("tier 5" in i for i in issues)


def test_moves_table():
    text = "No. Companies Rising +1 Tier 2025 Tier 2024 Tier\n1 Hilton Food Group 3 4\n5 Unilever NV 5 4\n"
    assert bbfaw.parse_moves(text) == {"Hilton Food Group": 3, "Unilever NV": 5}


def test_match_and_row():
    groups = [{"slug": "danone", "display_name": "Danone", "legal_name": "Danone SA"},
              {"slug": "yum-brands", "display_name": "Yum! Brands", "legal_name": "Yum! Brands, Inc."}]
    assert match_group("Groupe Danone SA", groups)["slug"] == "danone"
    assert match_group("Yum China Holdings", groups) is None
    r = build_row("danone", bbfaw.BbfawEntry("Groupe Danone SA", 3))
    assert r.value_text == "Tier 3" and r.normalized_value == 0.64 and "Tier 3 sur 6" in r.excerpt
