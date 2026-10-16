"""Import loi Rixain : part de femmes parmi les membres des instances dirigeantes → GOV_EXEC_GENDER.

Connecteur déterministe (source RIXAIN, niveau réglementaire) : rapprochement par SIREN, dernière
déclaration calculée. Indicateur distinct de la mixité du conseil (GOV_BOARD_GENDER).

Usage :
    python -m diams.import_rixain [--apply]
"""
from __future__ import annotations

import argparse

import httpx

from . import supabase_client
from .connectors import rixain
from .load import EvidenceRow, insert_evidence


def _fr(v: float) -> str:
    return (f"{v:.2f}".rstrip("0").rstrip(".")).replace(".", ",")


def build_rows(entities: list[dict], by_siren: dict[str, rixain.RixainRecord]) -> list[EvidenceRow]:
    rows = []
    for e in entities:
        rec = by_siren.get(str(e.get("siren") or ""))
        if rec is None:
            continue
        cadres = f"{_fr(rec.cadres_f)} %" if rec.cadres_f is not None else "non calculable (NC)"
        rows.append(EvidenceRow(
            entity_slug=e["slug"], indicator_code="GOV_EXEC_GENDER", source_code="RIXAIN", nature="result",
            # Écarts de l'année N publiés au plus tard le 1er mars de l'année N + 1.
            observed_on=f"{rec.year + 1}-03-01", value_type="numeric", value_numeric=rec.membres_f,
            normalized_value=max(0.0, min(1.0, rec.membres_f / 50)), confidence=0.95,
            source_url=rixain.EXPORT_URL, reviewer="import_rixain",
            excerpt=(f"Représentation équilibrée femmes-hommes (loi Rixain), déclaration au titre de {rec.year}, "
                     f"export public du site Égapro du ministère du Travail : {rec.name} (SIREN {rec.siren}) — "
                     f"{_fr(rec.membres_f)} % de femmes parmi les membres des instances dirigeantes ; "
                     f"{cadres} parmi les cadres dirigeants."),
        ))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Import loi Rixain (instances dirigeantes).")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    records = rixain.fetch(httpx.Client(timeout=300))
    by_siren = rixain.latest_by_siren(records)
    print(f"{len(records)} déclarations lues, {len(by_siren)} sociétés avec une part calculée")
    rows = build_rows(supabase_client.list_entities(), by_siren)
    for r in rows:
        print(f"✔ {r.entity_slug:32} {r.value_numeric} % ({r.observed_on})")
    print(f"\n{len(rows)} preuve(s)")
    if args.apply:
        stats = insert_evidence(rows)
        print(f"Insérées : {stats['inserted']} · ignorées : {stats['skipped']}")
    else:
        print("(dry-run : relancer avec --apply)")


if __name__ == "__main__":
    main()
