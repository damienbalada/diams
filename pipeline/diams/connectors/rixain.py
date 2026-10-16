"""Connecteur loi Rixain — représentation équilibrée des femmes et des hommes parmi les cadres
dirigeants et les membres des instances dirigeantes (export public du site Égapro, ministère du
Travail).

Une ligne par déclaration : année au titre de laquelle les écarts sont calculés, SIREN, raison
sociale, part de femmes parmi les cadres dirigeants et parmi les membres des instances
dirigeantes (« NC » quand l'écart n'est pas calculable). Rapprochement par SIREN uniquement.
"""
from __future__ import annotations

import io
from dataclasses import dataclass

import httpx

EXPORT_URL = "https://egapro.travail.gouv.fr/dgt-export-representation.xlsx"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}


@dataclass
class RixainRecord:
    year: int
    siren: str
    name: str
    cadres_f: float | None
    membres_f: float | None


def _pct(v) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None  # « NC » : écart non calculable


def parse_xlsx(content: bytes) -> list[RixainRecord]:
    import openpyxl
    ws = openpyxl.load_workbook(io.BytesIO(content), read_only=True).worksheets[0]
    rows = ws.iter_rows(values_only=True)
    head = [str(h) for h in next(rows)]
    ix = {h: head.index(h) for h in ("Annee_ecarts", "SIREN", "Nom_Entreprise",
                                      "Cadres_pourcentage_femmes", "Membres_pourcentage_femmes")}
    out = []
    for r in rows:
        if not r[ix["SIREN"]] or not r[ix["Annee_ecarts"]]:
            continue
        out.append(RixainRecord(int(r[ix["Annee_ecarts"]]), str(r[ix["SIREN"]]).strip().zfill(9),
                                str(r[ix["Nom_Entreprise"]] or "").strip(),
                                _pct(r[ix["Cadres_pourcentage_femmes"]]), _pct(r[ix["Membres_pourcentage_femmes"]])))
    return out


def fetch(client: httpx.Client | None = None) -> list[RixainRecord]:
    c = client or httpx.Client(timeout=300)
    r = c.get(EXPORT_URL, headers=HEADERS, follow_redirects=True)
    r.raise_for_status()
    return parse_xlsx(r.content)


def latest_by_siren(records: list[RixainRecord]) -> dict[str, RixainRecord]:
    """Dernière déclaration dont la part de femmes dans les instances dirigeantes est calculée."""
    best: dict[str, RixainRecord] = {}
    for rec in records:
        if rec.membres_f is None:
            continue
        if rec.siren not in best or rec.year > best[rec.siren].year:
            best[rec.siren] = rec
    return best
