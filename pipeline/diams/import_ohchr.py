"""Import de la base du HCDH (entreprises liées aux colonies) → GEO_CONFLICT_TIES.

Base mandatée par le Conseil des droits de l'homme (rés. 31/36, 53/25) : liste
officielle des entreprises impliquées dans les activités détaillées au §96 du
rapport de la mission d'établissement des faits (mises à jour 2020, 2023, 2025,
2026 — A/HRC/63/20). Connecteur DÉTERMINISTE (source audited_ngo) : lecture de
l'annexe du rapport (PDF officiel passé en --file) et correspondance EXACTE des
noms (formes juridiques retirées). Aucun nom approché n'est retenu.

Controverse non contestée (base consensus de l'ONU, Règle 4) : elle compte.
Ne pas figurer dans la base n'est jamais une preuve.

Usage :
    python -m diams.import_ohchr --file a-hrc-63-20.pdf --symbol A/HRC/63/20 --date 2026-09-25 [--apply]
"""
from __future__ import annotations

import argparse
import re
import unicodedata

from . import supabase_client
from .load import EvidenceRow, insert_evidence

SOURCE_URL = "https://www.ohchr.org/en/documents/thematic-reports/ahrc6320-database-all-business-enterprises-involved-activities-detailed"
_ROW = re.compile(r"(?:^|\s)(\d{1,3}) ([A-Z][^()]{1,90}?) \(([a-j])\)((?:, \([a-j]\))*) ([A-Z][A-Za-z ]{3,60}?)(?= \d{1,3} [A-Z]|$)")
_FORMS = r"\b(inc|ltd|s\.?a|b\.?v|plc|ag|se|n\.?v|corp|corporation|group|holdings?|company|co|sab de cv|s\.m\.e)\b\.?"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(_FORMS, " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def parse_annex(text: str) -> list[tuple[str, str]]:
    """(entreprise, État d'origine) depuis le texte de l'annexe I."""
    start = text.find("Annex I")
    body = text[start:] if start >= 0 else text
    end = body.find("Annex II")
    body = body[:end] if end > 0 else body
    flat = re.sub(r"\s+", " ", body)
    return [(m.group(2).strip(), m.group(5).strip()) for m in _ROW.finditer(flat)]


def match(listed: list[tuple[str, str]], entities: list[dict]) -> list[tuple[dict, str, str]]:
    idx: dict[str, dict] = {}
    for e in entities:
        for n in (e.get("display_name"), e.get("legal_name")):
            if n and len(norm(n)) > 3:
                idx[norm(n)] = e
    return [(idx[norm(name)], name, state) for name, state in listed if norm(name) in idx]


def main() -> None:
    parser = argparse.ArgumentParser(description="Import de la base du HCDH (colonies).")
    parser.add_argument("--file", required=True, help="PDF officiel du rapport (annexe I)")
    parser.add_argument("--symbol", required=True, help="cote du rapport, ex. A/HRC/63/20")
    parser.add_argument("--date", required=True, help="date de publication AAAA-MM-JJ")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    import pypdf
    text = "\n".join(p.extract_text() or "" for p in pypdf.PdfReader(args.file).pages)
    listed = parse_annex(text)
    hits = match(listed, supabase_client.list_entities())
    print(f"{len(listed)} entreprises lues dans l'annexe ; {len(hits)} correspondance(s) exacte(s) avec DIAMS")
    rows = [EvidenceRow(
        entity_slug=e["slug"], indicator_code="GEO_CONFLICT_TIES", source_code="UN_OHCHR_DB", nature="controversy",
        observed_on=args.date, value_type="category", value_text="listed", normalized_value=0.7, confidence=0.85,
        source_url=SOURCE_URL, reviewer="import_ohchr",
        excerpt=f"Base de données du HCDH ({args.symbol}) : « {name} » ({state}) figure parmi les entreprises impliquées "
                f"dans des activités liées aux colonies israéliennes dans le Territoire palestinien occupé.",
    ) for e, name, state in hits]
    for r in rows:
        print(f"✔ {r.entity_slug}")
    if args.apply and rows:
        stats = insert_evidence(rows)
        print(f"Insérées : {stats['inserted']} · ignorées : {stats['skipped']}")


if __name__ == "__main__":
    main()
