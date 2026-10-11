"""Import B Corp : certification en vigueur → GOV_BCORP.

Connecteur DÉTERMINISTE (source audited_ngo, annuaire B Lab) : publication
automatique (`auto:import_bcorp`) des seules paires vérifiées (connectors/bcorp.py,
`VERIFIED`), si la fiche est toujours certifiée et pointe vers le site attendu.
`--discover` liste les candidats (nom identique) à faire vérifier — rien n'est écrit.

Usage :
    python -m paris_memoire.import_bcorp [--apply]
    python -m paris_memoire.import_bcorp --discover [--only slug1,slug2]
"""
from __future__ import annotations

import argparse
import time
from datetime import date

import httpx

from . import supabase_client
from .connectors import bcorp
from .load import EvidenceRow, insert_evidence


def build_row(slug: str, b: bcorp.BCorp, today: str) -> EvidenceRow:
    score = f", score B Impact {b.score:.1f} (seuil 80)".replace(".", ",") if b.score is not None else ""
    since = f" depuis {b.certified_since}" if b.certified_since else ""
    where = f", activité : {b.operates_in}" if b.operates_in else ""
    return EvidenceRow(
        entity_slug=slug, indicator_code="GOV_BCORP", source_code="B_LAB", nature="result",
        observed_on=today, value_type="boolean", value_boolean=True, normalized_value=1.0, confidence=0.9,
        source_url=b.url, reviewer="import_bcorp",
        excerpt=f"Annuaire B Lab (consulté le {today}) : « {b.name} » certifiée B Corp{since}{score}{where}.",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Import B Corp (annuaire B Lab).")
    parser.add_argument("--only", help="slugs séparés par des virgules (découverte)")
    parser.add_argument("--discover", action="store_true", help="lister les candidats, sans rien écrire")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    today = date.today().isoformat()
    rows: list[EvidenceRow] = []
    with httpx.Client(timeout=60) as c:
        if args.discover:
            entities = supabase_client.list_entities()
            if args.only:
                keep = set(args.only.split(","))
                entities = [e for e in entities if e["slug"] in keep]
            for e in sorted(entities, key=lambda x: x["slug"]):
                b = bcorp.discover(e, c)
                time.sleep(0.3)  # politesse envers l'annuaire
                if b:
                    known = "déjà vérifiée" if e["slug"] in bcorp.VERIFIED else "À VÉRIFIER"
                    print(f"? {e['slug']:24} {b.name} · {b.website} · {b.industry} · {b.certified_since} [{known}]")
            return
        for slug in sorted(bcorp.VERIFIED):
            b = bcorp.verified(slug, c)
            if b:
                rows.append(build_row(slug, b, today))
                print(f"✔ {slug:24} {b.name} · {b.website} · {b.certified_since} · {b.score}")
            else:
                print(f"✖ {slug:24} fiche non certifiée ou site différent : aucune preuve")
    print(f"\n{len(rows)} certification(s) vérifiée(s)")
    if args.apply:
        stats = insert_evidence(rows)
        print(f"Insérées : {stats['inserted']} · ignorées : {stats['skipped']}")
    else:
        print("(dry-run : relancer avec --apply)")


if __name__ == "__main__":
    main()
