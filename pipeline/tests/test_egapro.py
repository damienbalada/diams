from diams.connectors.egapro import (
    EgaproRecord,
    latest_by_siren,
    parse_csv,
    parse_records,
)
from diams.import_egapro import build_rows

PAYLOAD = {
    "results": [
        {"siren": "552075020", "raison_sociale": "KERING", "annee": "2023", "note_index": 91},
        {"siren": "552075020", "raison_sociale": "KERING", "annee": "2024", "note_index": 94},
        {"siren": "999999999", "raison_sociale": "SANS NOTE", "annee": "2024"},
        {"siren": "", "annee": "2024", "note_index": 80},
    ]
}


def test_parse_records_skips_incomplete():
    recs = parse_records(PAYLOAD)
    assert len(recs) == 2
    assert all(r.siren == "552075020" for r in recs)


def test_latest_by_siren_keeps_most_recent():
    recs = parse_records(PAYLOAD)
    best = latest_by_siren(recs)
    assert best["552075020"].year == "2024"
    assert best["552075020"].note == 94.0


def test_build_rows_normalizes_over_100():
    by_siren = {"552075020": EgaproRecord(siren="552075020", raison_sociale="KERING", year="2024", note=94)}
    entities = [
        {"slug": "kering", "siren": "552075020"},
        {"slug": "hermes", "siren": "572012051"},
        {"slug": "chanel", "siren": None},
    ]
    rows = build_rows(entities, by_siren)
    assert len(rows) == 1
    r = rows[0]
    assert r.entity_slug == "kering"
    assert r.normalized_value == 0.94
    # index calculé au titre de 2024, publié au plus tard le 1er mars 2025
    assert r.observed_on == "2025-03-01"


def test_parse_csv_offline_fallback(tmp_path):
    p = tmp_path / "egapro.csv"
    p.write_text(
        "siren,raison_sociale,annee,note\n"
        "552075020,KERING,2024,94\n"
        "000000000,SANS NOTE,2024,\n"
        ",VIDE,2024,50\n",
        encoding="utf-8",
    )
    recs = parse_csv(str(p))
    assert [r.siren for r in recs] == ["552075020"]
    assert recs[0].note == 94.0
    assert recs[0].year == "2024"


def test_parse_csv_official_export_headers(tmp_path):
    # En-tetes reels de l'export data.gouv.fr : "Note Index" (espace), "Annee",
    # "Raison Sociale" - casse et libelles du fichier officiel.
    p = tmp_path / "egapro.csv"
    p.write_text(
        "Annee,SIREN,Raison Sociale,Note Ecart remuneration,Note Index\n"
        "2024,552075020,KERING,38,94\n",
        encoding="utf-8-sig",
    )
    recs = parse_csv(str(p))
    assert len(recs) == 1
    assert recs[0].siren == "552075020"
    assert recs[0].note == 94.0
    assert recs[0].year == "2024"


def test_parse_csv_french_decimal(tmp_path):
    p = tmp_path / "egapro.csv"
    p.write_text('siren,note\n552075020,"88,5"\n', encoding="utf-8")
    recs = parse_csv(str(p))
    assert recs[0].note == 88.5


def test_index_ues_attribue_aux_societes_membres():
    from diams.connectors.egapro import EgaproRecord, latest_by_member, latest_by_siren
    from diams.import_egapro import build_rows
    recs = [
        EgaproRecord(siren="111111111", raison_sociale="Société A", year="2020", note=80.0),
        EgaproRecord(siren="999999999", raison_sociale="Tête d'UES", year="2025", note=91.0,
                     ues_name="UES Exemple", members=("111111111", "222222222")),
    ]
    rows = build_rows([{"slug": "a", "siren": "111111111"}, {"slug": "b", "siren": "222222222"}],
                      latest_by_siren(recs), latest_by_member(recs))
    by = {r.entity_slug: r for r in rows}
    # L'index 2025 de l'UES l'emporte sur la déclaration propre de 2020.
    assert by["a"].value_numeric == 91.0 and "UES Exemple" in by["a"].excerpt
    assert by["b"].observed_on == "2026-03-01"
