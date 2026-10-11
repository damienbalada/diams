"""Connecteur B Corp : lecture de fiche, découverte par nom, import des seules paires vérifiées."""
from paris_memoire.connectors.bcorp import VERIFIED, candidates, norm_name, parse_page

PAGE = """<html><head><title>BoursoBank - Certified B Corporation - B Lab</title></head><body>
<p>Certified Since</p><p>February 2023</p><p>Industry</p><p>Deposit bank</p><p>Sector</p><p>Service</p>
<p>Operates In</p><p>France</p>
<p>Website</p><p>https://www.boursobank-group.com/fr/</p>
<p>Based on the B Impact assessment, BoursoBank earned an overall score of 90.9. The median…</p>
</body></html>"""

HOMONYME = PAGE.replace("BoursoBank", "Alpine").replace("boursobank-group.com/fr/", "alpinehearingprotection.com")


def test_lecture_de_fiche():
    b = parse_page(PAGE, "https://example.org")
    assert b.name == "BoursoBank" and b.certified_since == "February 2023" and b.score == 90.9
    assert b.operates_in == "France" and b.industry == "Deposit bank"
    assert "boursobank" in b.website


def test_fiche_non_certifiee_ignoree():
    assert parse_page("<title>Page not found - B Lab</title>", "u") is None


def test_paire_verifiee_coherente_avec_le_site():
    slug, domain = VERIFIED["boursobank"]
    assert slug == "boursorama" and domain in parse_page(PAGE, "u").website


def test_homonyme_jamais_importe():
    # Une fiche « Alpine » certifiée n'est qu'un candidat de découverte : sans
    # paire vérifiée, la marque automobile ne reçoit aucune preuve.
    assert "alpine" not in VERIFIED
    assert "alpinehearingprotection" in parse_page(HOMONYME, "u").website


def test_candidats_de_decouverte():
    c = candidates({"slug": "la-nef", "display_name": "La Nef", "legal_name": "Société Financière de la Nef"})
    assert [s for s, _ in c] == ["la-nef", "societe-financiere-de-la-nef"]
    assert norm_name("La Nef") in c[0][1]
