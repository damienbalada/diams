"""Import de preuves curées : contrôle strict et revue humaine obligatoire."""
import pytest

from paris_memoire.attach_regimes import egapro_links
from paris_memoire.connectors.egapro import EgaproRecord
from paris_memoire.import_curated import parse_row
from paris_memoire.load import review_status_for

ROW = {
    "entity_slug": "bnp-paribas", "indicator_code": "TAX_CBCR_PUBLISHED", "source_code": "CBCR",
    "nature": "result", "observed_on": "2025-03-14", "value_type": "boolean", "value_boolean": "true",
    "normalized_value": "1", "confidence": "0.9",
    "source_url": "https://example.org/urd-2024.pdf", "excerpt": "Implantations et activités par pays (2024).",
}


def test_ligne_valide_part_en_revue():
    r = parse_row(dict(ROW))
    assert r.value_boolean is True and r.normalized_value == 1.0
    assert r.reviewer.startswith("ai:")
    # même source réglementaire : une IA ne publie pas seule
    assert review_status_for("regulatory", r.reviewer) == "pending"


@pytest.mark.parametrize("field,value,msg", [
    ("source_url", "", "obligatoire"),
    ("source_url", "pas-une-url", "source_url"),
    ("observed_on", "2025-3-14", "AAAA-MM-JJ"),
    ("observed_on", "2999-01-01", "futur"),
    ("nature", "rumeur", "nature"),
    ("normalized_value", "1.4", "hors"),
    ("excerpt", "", "obligatoire"),
])
def test_ligne_invalide_refusee(field, value, msg):
    row = dict(ROW, **{field: value})
    with pytest.raises(ValueError, match=msg):
        parse_row(row)


def test_reviewer_humain_ou_auto_refuse():
    with pytest.raises(ValueError, match="ai:"):
        parse_row(dict(ROW), reviewer="auto:pipeline")


def test_egapro_rattache_seulement_les_declarants_recents():
    by_siren = {
        "662042449": EgaproRecord(siren="662042449", raison_sociale="BNP PARIBAS", year="2025", note=86),
        "111111111": EgaproRecord(siren="111111111", raison_sociale="ANCIENNE", year="2019", note=80),
    }
    ents = [{"slug": "bnp-paribas", "siren": "662042449"}, {"slug": "ancienne", "siren": "111111111"},
            {"slug": "marque", "siren": None}]
    links = egapro_links(ents, by_siren, "2026-10-10")
    assert [l.entity_slug for l in links] == ["bnp-paribas"]
    assert links[0].regime_code == "FR_EGAPRO" and links[0].reviewer == "auto:attach_regimes"
