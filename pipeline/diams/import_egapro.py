"""Import Égapro : index d'égalité professionnelle F/H par SIREN.

Prérequis : les SIREN doivent être renseignés (via enrich_entities).

Usage :
    python -m diams.import_egapro                       # dry-run (API ODS live)
    python -m diams.import_egapro --apply               # écrit (pending)
    python -m diams.import_egapro --file egapro.csv     # fallback hors-ligne

Le fallback CSV attend au moins : siren + note (+ annee, raison_sociale). Utile
quand l'API ODS n'est pas joignable (politique réseau) ou pour rejouer un export.
"""
from __future__ import annotations

import argparse

from . import supabase_client
from .connectors import egapro
from .load import EvidenceRow, insert_evidence


def build_rows(entities: list[dict], by_siren: dict[str, egapro.EgaproRecord],
               by_member: dict[str, egapro.EgaproRecord] | None = None) -> list[EvidenceRow]:
    rows: list[EvidenceRow] = []
    for e in entities:
        siren = e.get("siren")
        if not siren:
            continue
        rec = by_siren.get(str(siren))
        # Société membre d'une UES : l'index de l'UES couvre ses salariés. Il est retenu s'il
        # est plus récent que la dernière déclaration propre de la société (relecture du 15/10).
        via = (by_member or {}).get(str(siren))
        if via is not None and (rec is None or via.year > rec.year):
            rec = via
        if rec is None:
            continue
        # « Année » = année de CALCUL de l'index ; publication obligatoire au plus
        # tard le 1er mars de l'année suivante (C. trav. D1142-4). Les premières
        # déclarations (2018) ont été publiées en mars 2019.
        observed_on = f"{int(rec.year) + 1}-03-01" if rec.year.isdigit() else "1970-01-01"
        rows.append(EvidenceRow(
            entity_slug=e["slug"], indicator_code="LAB_EGAPRO_INDEX", source_code="EGAPRO",
            nature="result", observed_on=observed_on, value_type="numeric",
            value_numeric=rec.note, normalized_value=max(0.0, min(1.0, rec.note / 100.0)),
            confidence=0.95, source_url=egapro.EGAPRO_SOURCE_URL,
            excerpt=(f"Index Égapro {rec.year} : {rec.note:.0f}/100 ({rec.raison_sociale or siren})"
                     if rec.siren == str(siren) else
                     f"Index Égapro {rec.year} de l'UES « {rec.ues_name or rec.raison_sociale} » : {rec.note:.0f}/100 "
                     f"(déclaration de {rec.raison_sociale}, SIREN {rec.siren} ; la société, SIREN {siren}, "
                     f"est membre de l'UES)"),
        ))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Égapro (index égalité F/H).")
    parser.add_argument("--apply", action="store_true", help="écrit en base (sinon dry-run)")
    parser.add_argument("--file", help="CSV Égapro (fallback hors-ligne : siren + note)")
    args = parser.parse_args()

    entities = supabase_client.list_entities()

    if args.file:
        records = egapro.parse_csv(args.file)
        print(f"{len(records)} lignes Égapro lues depuis {args.file}")
    else:
        records = egapro.fetch_export()
        print(f"{len(records)} déclarations lues dans l'export public du site Égapro")
    by_siren = egapro.latest_by_siren(records)
    print(f"{len(by_siren)} index Égapro trouvés")

    rows = build_rows(entities, by_siren, egapro.latest_by_member(records))
    for r in rows:
        print(f"✔ {r.entity_slug}: LAB_EGAPRO_INDEX = {r.value_numeric}/100")
    print(f"\n{len(rows)} evidence à insérer (statut selon le tier de la source)")

    if args.apply:
        stats = insert_evidence(rows)
        print(f"Insérées: {stats['inserted']} · ignorées: {stats['skipped']}")
    else:
        print("(dry-run : rien n'a été écrit. Relancer avec --apply.)")


if __name__ == "__main__":
    main()
