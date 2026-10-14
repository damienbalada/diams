from diams.connectors import cdp_scores as cs
from diams.connectors import kse_russia as kse
from diams.import_cdp_scores import match as cdp_match
from diams.import_cdp_scores import rows_for
from diams.import_kse import build_row, fr_date, match_group
from diams.normalize.names import normalize_name

CARD = (
    '<div class="card {cls}"><div class="cstatus"><div class="label status {cls} ">'
    '<a class="" href="#"><span>{grp} </span>{status}</a></div>'
    '<div class="ddmenu "><div><div><a href="//leave-russia.org/{slug}">Show Company Details</a></div></div></div>'
    '<div class="annotation"><div><div>{name}</div></div></div>'
    '<div class="label country {cc} "><a href="#">X</a></div>'
    '<div class="decision"><div class="date">{date}<span>&nbsp;</span><a href="https://ex.org/s" target="_blank">Statement</a></div>'
    '<p>{text}</p></div></div>'
)


def test_kse_cards_status_and_unknown_skipped():
    page = "".join([
        CARD.format(cls="transfer exited", grp="Exited", status="Exit Completed", slug="danone", name="Danone",
                    cc="fr", date="May 17, 2024", text="Transfer of the <b>dairy</b> business."),
        CARD.format(cls="continue stay", grp="Stay", status="Continue Operations", slug="loreal", name="L\\'Oreal",
                    cc="fr", date="October 05, 2023", text="Still operating."),
        CARD.format(cls="odd", grp="?", status="Something New", slug="x", name="X", cc="us", date="", text=""),
    ])
    rows = kse.parse_list(page)
    assert [(r.slug, r.status, r.value) for r in rows] == [("danone", "Exit Completed", 1.0), ("loreal", "Continue Operations", 0.0)]
    assert rows[1].name == "L'Oreal" and rows[0].statement == "Transfer of the dairy business."
    assert fr_date(rows[0].decision_date) == "17/05/2024"
    r = build_row("danone", rows[0], "2026-10-11")
    assert r.normalized_value == 1.0 and "sortie effective" in r.excerpt and "17/05/2024" in r.excerpt


def test_kse_matching_exact_only():
    groups = [{"slug": "hm-group", "display_name": "H&M Group", "legal_name": "H & M Hennes & Mauritz AB"},
              {"slug": "danone", "display_name": "Danone", "legal_name": "Danone SA"}]
    tt = kse.KseCompany("t-and-t-group", "T&T Group", "Continue Operations", None, None, None, None)
    hm = kse.KseCompany("h-m", "H&M (Hennes and Mauritz)", "Exit Completed", None, None, None, None)
    da = kse.KseCompany("danone", "Danone", "Exit Completed", None, None, None, None)
    assert match_group(tt, groups) is None              # « group » seul ne suffit pas
    assert match_group(hm, groups)["slug"] == "hm-group"  # alias explicite
    assert match_group(da, groups)["slug"] == "danone"


def test_cdp_grades_from_icons():
    icon = "https://cdn.cdp.net/x/{}-Icon-grey-text.svg"
    assert cs.grade(icon.format("Climate-A")) == "A"
    assert cs.grade(icon.format("Water-B-Minus")) == "B-"
    assert cs.grade(icon.format("Climate-D-minus")) == "D-"
    assert cs.grade("Did not disclose") == "F"
    assert cs.grade("Not Scored") is None and cs.grade("See disclosing organisation") is None and cs.grade("") is None


def test_cdp_matching_and_rows():
    s = [cs.CdpScore("Danone S.A.", "France", "A", "A"), cs.CdpScore("Procter & Gamble", "Canada", "F", None),
         cs.CdpScore("Procter & Gamble Company", "United States of America", "A-", "B"),
         cs.CdpScore("Shell PLC", "United Kingdom", "F", "F")]
    by_name, by_norm = {}, {}
    for x in s:
        by_name.setdefault(x.company, []).append(x)
        by_norm.setdefault(normalize_name(x.company), []).append(x)
    assert cdp_match("danone", ["Danone", "Danone SA"], by_name, by_norm).company == "Danone S.A."
    assert cdp_match("procter-gamble", ["Procter & Gamble"], by_name, by_norm).country == "United States of America"
    assert cdp_match("ab-inbev", ["AB InBev"], by_name, by_norm) is None
    rows = rows_for("shell", s[3])
    assert [r.indicator_code for r in rows] == ["ENV_CDP_CLIMATE", "WAT_CDP"]
    assert rows[0].normalized_value == 0.0 and "n'a pas répondu" in rows[0].excerpt
