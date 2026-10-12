"""Import SBTi : statut des objectifs climat (validé / engagé / retiré).

Usage :
    # 1) Télécharger l'export « Companies taking action » (CSV) :
    #    https://sciencebasedtargets.org/companies-taking-action
    # 2) Dry-run :
    python -m paris_memoire.import_sbti --file sbti.csv
    # 3) Écrire (source SBTi, ONG auditée : publication automatique) :
    python -m paris_memoire.import_sbti --file sbti.csv --apply

Les lignes plus anciennes de l'indicateur (saisie manuelle `curation-v1`, ou
import précédent au rapprochement par inclusion de noms) que cette exécution ne
confirme pas sont retirées (`remplace:import_sbti`) : la liste SBTi est complète,
une entreprise absente n'a pas d'objectif enregistré.
"""
from __future__ import annotations

import argparse
import datetime as dt

from . import supabase_client
from .connectors import sbti
from .load import EvidenceRow, insert_evidence


def _label_fr(label: str) -> str:
    """Statut SBTi en français (le statut d'origine reste dans value_text)."""
    low = label.lower()
    if "removed" in low:
        return " : engagement retiré"
    if "commit" in low:
        return " : engagement à en fixer un"
    if "validated" in low or "targets set" in low:
        return " validé"
    return f" : {label}"


def _classif_fr(c: str) -> str:
    return c.replace("Well-below 2°C", "bien en dessous de 2 °C").replace("1.5°C", "1,5 °C").replace("2°C", "2 °C")


def build_rows(entities: list[dict], sbti_rows: list[sbti.SbtiRow], observed_on: str) -> list[EvidenceRow]:
    rows: list[EvidenceRow] = []
    for e in entities:
        if e.get("is_brand"):
            continue  # objectifs climat portés par le groupe, hérités par les marques
        m = sbti.match_company(e, sbti_rows)
        if m is None:
            continue
        rows.append(EvidenceRow(
            entity_slug=e["slug"], indicator_code="ENV_SBTI_VALIDATED", source_code="SBTI",
            nature=m.nature, observed_on=observed_on, value_type="category",
            value_text=m.label, normalized_value=m.normalized_value, confidence=0.85,
            source_url=sbti.SBTI_SOURCE_URL,
            excerpt=(f"SBTi, export « Companies taking action » (consulté le {observed_on[8:10]}/{observed_on[5:7]}/{observed_on[:4]}) : "
                     f"« {m.company} » — objectif de court terme{_label_fr(m.label)}"
                     + (f" ({_classif_fr(m.classification)})" if m.classification else "")
                     + (" (engagement retiré)." if m.nature == "result"
                        else " (objectif validé par la SBTi : un engagement sur l'avenir, pas un résultat)."
                        if m.normalized_value >= 0.6 else " (engagement à fixer un objectif, non encore validé).")),
            reviewer="import_sbti",
        ))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Import SBTi (objectifs climat).")
    parser.add_argument("--file", required=True, help="CSV SBTi téléchargé")
    parser.add_argument("--apply", action="store_true", help="écrit en base (sinon dry-run)")
    args = parser.parse_args()

    sbti_rows = sbti.parse_csv(args.file)
    print(f"{len(sbti_rows)} lignes exploitables dans l'export SBTi")

    entities = supabase_client.list_entities()
    rows = build_rows(entities, sbti_rows, observed_on=dt.date.today().isoformat())
    for r in rows:
        print(f"✔ {r.entity_slug}: ENV_SBTI_VALIDATED = {r.normalized_value} [{r.nature}] ({r.value_text})")
    print(f"\n{len(rows)} evidence à insérer (pending)")

    if not args.apply:
        print("(dry-run : rien n'a été écrit. Relancer avec --apply.)")
        return
    stats = insert_evidence(rows)
    print(f"Insérées: {stats['inserted']} · ignorées: {stats['skipped']}")
    # Retrait des lignes antérieures non confirmées par cette exécution.
    import httpx
    from . import config
    h = supabase_client._headers()
    base = f"{config.SUPABASE_URL}/rest/v1"
    with httpx.Client(timeout=60) as c:
        ind = c.get(f"{base}/indicators", params={"select": "id", "code": "eq.ENV_SBTI_VALIDATED"}, headers=h).json()[0]["id"]
        old = c.get(f"{base}/evidence", params={
            "select": "id,observed_on,reviewer", "indicator_id": f"eq.{ind}", "review_status": "eq.approved",
            "reviewer": "in.(curation-v1,auto:pipeline)"}, headers=h).json()
        if old:
            r = c.patch(f"{base}/evidence", params={"id": f"in.({','.join(o['id'] for o in old)})"},
                        headers={**h, "Prefer": "return=minimal"},
                        json={"review_status": "rejected", "reviewer": "remplace:import_sbti"})
            r.raise_for_status()
        print(f"{len(old)} ligne(s) antérieure(s) retirée(s)")


if __name__ == "__main__":
    main()
