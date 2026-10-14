"""Import de preuves CURÉES (recherche documentaire assistée) — toujours en revue.

Une ligne = une preuve : entité, indicateur, source, date, valeur, URL, extrait.
Le CSV est versionné dans `pipeline/curated/` : c'est la piste d'audit (qui a
affirmé quoi, d'après quel document). Chaque ligne est écrite en `pending` avec
un reviewer `ai:<modèle>` : une recherche assistée par IA n'est pas déterministe,
un humain valide chaque preuve dans /admin/revue avant qu'elle compte.

Usage :
    python -m diams.import_curated --file curated/banques_2026-10.csv          # contrôle
    python -m diams.import_curated --file curated/banques_2026-10.csv --apply  # écrit (pending)

Colonnes : entity_slug, indicator_code, source_code, nature, observed_on,
value_type, value_numeric, value_boolean, value_text, normalized_value,
confidence, source_url, excerpt. Le contrôle est strict : une seule ligne
invalide bloque l'import (rien n'est écrit à moitié).
"""
from __future__ import annotations

import argparse
import csv
import re
from datetime import date

from .load import AI_REVIEWER_PREFIX, EvidenceRow, insert_evidence

NATURES = {"result", "commitment", "policy", "controversy"}
VALUE_TYPES = {"numeric", "boolean", "ordinal", "category"}
DEFAULT_REVIEWER = f"{AI_REVIEWER_PREFIX}claude-opus-5-5"
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _num(v: str | None) -> float | None:
    if v is None or str(v).strip() == "":
        return None
    return float(str(v).replace(",", "."))


def _bool(v: str | None) -> bool | None:
    if v is None or str(v).strip() == "":
        return None
    s = str(v).strip().lower()
    if s in {"true", "1", "oui", "yes"}:
        return True
    if s in {"false", "0", "non", "no"}:
        return False
    raise ValueError(f"booléen illisible : {v!r}")


def parse_row(row: dict[str, str], reviewer: str = DEFAULT_REVIEWER) -> EvidenceRow:
    """Valide une ligne et la convertit ; lève ValueError avec un message clair."""
    get = lambda k: (row.get(k) or "").strip()  # noqa: E731
    for k in ("entity_slug", "indicator_code", "source_code", "nature", "observed_on",
              "value_type", "source_url", "excerpt"):
        if not get(k):
            raise ValueError(f"colonne obligatoire vide : {k}")
    if get("nature") not in NATURES:
        raise ValueError(f"nature inconnue : {get('nature')}")
    if get("value_type") not in VALUE_TYPES:
        raise ValueError(f"value_type inconnu : {get('value_type')}")
    if not _ISO.match(get("observed_on")):
        raise ValueError(f"observed_on doit être AAAA-MM-JJ : {get('observed_on')}")
    if date.fromisoformat(get("observed_on")) > date.today():
        raise ValueError(f"observed_on dans le futur : {get('observed_on')}")
    if not re.match(r"^https?://\S+$", get("source_url")):
        raise ValueError(f"source_url invalide : {get('source_url')}")
    if not reviewer.startswith(AI_REVIEWER_PREFIX):
        raise ValueError("une preuve curée doit porter un reviewer « ai:… » (revue humaine obligatoire)")

    value_numeric = _num(row.get("value_numeric"))
    value_boolean = _bool(row.get("value_boolean"))
    value_text = get("value_text") or None
    normalized = _num(row.get("normalized_value"))
    if value_numeric is None and value_boolean is None and value_text is None and normalized is None:
        raise ValueError("aucune valeur (numeric / boolean / text / normalized)")
    if normalized is not None and not 0.0 <= normalized <= 1.0:
        raise ValueError(f"normalized_value hors [0,1] : {normalized}")
    confidence = _num(row.get("confidence"))
    confidence = 0.7 if confidence is None else confidence
    if not 0.0 < confidence <= 1.0:
        raise ValueError(f"confidence hors ]0,1] : {confidence}")

    return EvidenceRow(
        entity_slug=get("entity_slug"), indicator_code=get("indicator_code"),
        source_code=get("source_code"), nature=get("nature"), observed_on=get("observed_on"),
        value_type=get("value_type"), value_numeric=value_numeric, value_boolean=value_boolean,
        value_text=value_text, normalized_value=normalized, confidence=confidence,
        source_url=get("source_url"), excerpt=get("excerpt"), reviewer=reviewer,
    )


def parse_file(path: str, reviewer: str = DEFAULT_REVIEWER) -> tuple[list[EvidenceRow], list[str]]:
    rows: list[EvidenceRow] = []
    errors: list[str] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for i, raw in enumerate(csv.DictReader(f), start=2):  # ligne 1 = en-têtes
            try:
                rows.append(parse_row(raw, reviewer))
            except ValueError as e:
                errors.append(f"ligne {i} : {e}")
    return rows, errors


def update_pending(rows: list[EvidenceRow]) -> int:
    """Corrige des preuves ENCORE EN ATTENTE (même clé) ; une preuve revue n'est jamais touchée."""
    import httpx

    from . import config
    from .load import _headers, _lookup_ids
    n = 0
    with httpx.Client(timeout=60) as c:
        ents, inds, srcs = _lookup_ids(c)
        for r in rows:
            resp = c.patch(
                f"{config.SUPABASE_URL}/rest/v1/evidence",
                params={"entity_id": f"eq.{ents[r.entity_slug]}", "indicator_id": f"eq.{inds[r.indicator_code]}",
                        "source_id": f"eq.{srcs[r.source_code][0]}", "observed_on": f"eq.{r.observed_on}",
                        "review_status": "eq.pending"},
                headers={**_headers(), "Prefer": "return=representation"},
                json={"value_numeric": r.value_numeric, "value_boolean": r.value_boolean, "value_text": r.value_text,
                      "normalized_value": r.normalized_value, "confidence": r.confidence,
                      "source_url": r.source_url, "excerpt": r.excerpt},
            )
            resp.raise_for_status()
            n += len(resp.json())
    return n


def main() -> None:
    parser = argparse.ArgumentParser(description="Import de preuves curées (toujours en revue).")
    parser.add_argument("--file", required=True)
    parser.add_argument("--reviewer", default=DEFAULT_REVIEWER, help="préfixe ai: obligatoire")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--update-pending", action="store_true",
                        help="corrige les preuves déjà importées mais encore en attente (jamais celles déjà revues)")
    args = parser.parse_args()

    rows, errors = parse_file(args.file, args.reviewer)
    for e in errors:
        print(f"✖ {e}")
    if errors:
        raise SystemExit(f"{len(errors)} ligne(s) invalide(s) : rien n'est écrit.")
    for r in rows:
        v = r.value_numeric if r.value_numeric is not None else (r.value_boolean if r.value_boolean is not None else r.value_text)
        print(f"• {r.entity_slug:32} {r.indicator_code:22} {r.source_code:16} {r.observed_on}  {v}")
    print(f"\n{len(rows)} preuve(s) valide(s) — statut : pending (revue humaine)")

    # Références inconnues en base : on refuse plutôt que d'ignorer en silence.
    import httpx

    from . import config
    from .load import _lookup_ids
    if config.SUPABASE_URL and config.SUPABASE_SERVICE_ROLE_KEY:
        with httpx.Client(timeout=60) as c:
            ents, inds, srcs = _lookup_ids(c)
        unknown = sorted({f"entité {r.entity_slug}" for r in rows if r.entity_slug not in ents}
                         | {f"indicateur {r.indicator_code}" for r in rows if r.indicator_code not in inds}
                         | {f"source {r.source_code}" for r in rows if r.source_code not in srcs})
        if unknown:
            raise SystemExit("Références inconnues en base : " + ", ".join(unknown))
    if args.apply:
        stats = insert_evidence(rows)
        print(f"Insérées : {stats['inserted']} · ignorées : {stats['skipped']} (doublon ou code inconnu)")
        if args.update_pending:
            print(f"Preuves en attente mises à jour : {update_pending(rows)}")
    else:
        print("(contrôle seulement : relancer avec --apply pour écrire)")


if __name__ == "__main__":
    main()
