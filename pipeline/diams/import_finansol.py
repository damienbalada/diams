"""Import Finansol : épargne solidaire labellisée → INV_SOLIDARITY_LABEL.

Connecteur DÉTERMINISTE (source audited_ngo) : il lit la liste officielle FAIR
et ne rattache un produit qu'au distributeur dont le nom est exactement celui de
l'établissement (connectors/finansol.py). Publication automatique
(`auto:import_finansol`). Seules les entités qui distribuent au moins un produit
labellisé reçoivent une preuve : l'absence n'est jamais un fait négatif.

Usage :
    python -m diams.import_finansol            # dry-run
    python -m diams.import_finansol --apply
"""
from __future__ import annotations

import argparse
from datetime import date

import httpx

from .connectors import finansol
from .load import EvidenceRow, insert_evidence


def build_rows(grouped: dict[str, list[finansol.Product]], today: str) -> list[EvidenceRow]:
    rows: list[EvidenceRow] = []
    for slug, prods in sorted(grouped.items()):
        names = " ; ".join(f"« {p.title} »" for p in prods[:4]) + (" ; …" if len(prods) > 4 else "")
        rows.append(EvidenceRow(
            entity_slug=slug, indicator_code="INV_SOLIDARITY_LABEL", source_code="FINANSOL", nature="result",
            observed_on=today, value_type="boolean", value_boolean=True, normalized_value=1.0, confidence=0.9,
            source_url=prods[0].url, reviewer="import_finansol",
            excerpt=(f"Liste officielle FAIR des produits labellisés Finansol (consultée le {today}) : "
                     f"{len(prods)} produit(s) distribué(s) par « {prods[0].distributor} » — {names}."),
        ))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Finansol (épargne solidaire labellisée).")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    with httpx.Client(timeout=60) as c:
        products = finansol.fetch_all(c)
    grouped = finansol.by_entity(products)
    print(f"{len(products)} produits labellisés lus ; {len(grouped)} établissement(s) rattaché(s)")
    rows = build_rows(grouped, date.today().isoformat())
    for r in rows:
        print(f"✔ {r.entity_slug:32} {r.excerpt[:110]}…")
    if args.apply:
        stats = insert_evidence(rows)
        print(f"Insérées : {stats['inserted']} · ignorées : {stats['skipped']}")
    else:
        print("(dry-run : relancer avec --apply)")


if __name__ == "__main__":
    main()
