"""Connecteur Égapro — index d'égalité professionnelle F/H (France).

Source : export public du site Égapro du ministère du Travail (index-egalite-fh.xlsx), une ligne
par déclaration. L'ancien jeu « index-egalite-professionnelle-f-h » de data.economie.gouv.fr a
disparu (erreur 404, constatée le 16/10/2026) ; son API ne servait de toute façon que 100 lignes
par requête.

Produit LAB_EGAPRO_INDEX (note /100, nature=result, tier regulatory).
Matching par SIREN exact uniquement : la donnée est indexée par SIREN, on ne
tente pas de matching par nom (trop ambigu sur les raisons sociales).
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from typing import Any

import httpx

EGAPRO_API = (
    "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/"
    "index-egalite-professionnelle-f-h/records"
)
EGAPRO_SOURCE_URL = "https://egapro.travail.gouv.fr/index-egapro/recherche"
EGAPRO_EXPORT_URL = "https://egapro.travail.gouv.fr/index-egalite-fh.xlsx"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}


@dataclass
class EgaproRecord:
    siren: str
    raison_sociale: str
    year: str
    note: float          # index /100
    # Déclaration d'une UES (unité économique et sociale) : son nom et les SIREN de ses
    # sociétés membres, dont l'index couvre aussi les salariés.
    ues_name: str | None = None
    members: tuple[str, ...] = ()


def parse_records(payload: dict[str, Any]) -> list[EgaproRecord]:
    """Parse tolérant de la réponse ODS explore v2 (champs sujets à variations)."""
    out: list[EgaproRecord] = []
    for rec in payload.get("results", []):
        if not isinstance(rec, dict):
            continue
        siren = str(rec.get("siren") or "").strip()
        note = rec.get("note_index")
        if note is None:
            note = rec.get("note")
        year = str(rec.get("annee") or rec.get("année") or "").strip()
        if not siren or note is None:
            continue
        try:
            note_f = float(note)
        except (TypeError, ValueError):
            continue
        out.append(EgaproRecord(
            siren=siren,
            raison_sociale=str(rec.get("raison_sociale") or ""),
            year=year,
            note=note_f,
        ))
    return out


SIREN_COLS = ("siren",)
NOTE_COLS = ("note index", "note_index", "note", "index")
YEAR_COLS = ("annee", "année", "year")
NAME_COLS = ("raison_sociale", "raison sociale", "entreprise", "nom")
UES_NAME_COLS = ("nom ues", "nom_ues")
UES_MEMBERS_COLS = ("entreprises ues (siren)", "entreprises_ues")


def _pick(row: dict, cols: tuple[str, ...]) -> str | None:
    lower = {k.lower().strip(): v for k, v in row.items()}
    for c in cols:
        if c in lower and lower[c] not in (None, ""):
            return lower[c]
    return None


def _records_from_rows(rows) -> list[EgaproRecord]:
    out: list[EgaproRecord] = []
    for row in rows:
        siren = (str(_pick(row, SIREN_COLS) or "")).strip()
        note = _pick(row, NOTE_COLS)
        if not siren or note is None:
            continue
        try:
            note_f = float(str(note).replace(",", "."))
        except (TypeError, ValueError):
            continue   # « NC » : index non calculable
        members = tuple(re.findall(r"\((\d{9})\)", str(_pick(row, UES_MEMBERS_COLS) or "")))
        out.append(EgaproRecord(
            siren=siren.zfill(9),
            raison_sociale=str(_pick(row, NAME_COLS) or ""),
            year=(str(_pick(row, YEAR_COLS) or "")).strip(),
            note=note_f,
            ues_name=(str(_pick(row, UES_NAME_COLS) or "").strip() or None) if members else None,
            members=members,
        ))
    return out


def parse_xlsx(content: bytes) -> list[EgaproRecord]:
    """Export public du site Égapro (une feuille, en-têtes « Année », « SIREN », « Note Index »…)."""
    import io
    import openpyxl
    ws = openpyxl.load_workbook(io.BytesIO(content), read_only=True).worksheets[0]
    it = ws.iter_rows(values_only=True)
    head = [str(h or "") for h in next(it)]
    return _records_from_rows(dict(zip(head, r)) for r in it)


def fetch_export(client: httpx.Client | None = None) -> list[EgaproRecord]:
    c = client or httpx.Client(timeout=300)
    r = c.get(EGAPRO_EXPORT_URL, headers=HEADERS, follow_redirects=True)
    r.raise_for_status()
    return parse_xlsx(r.content)


def parse_csv(path: str) -> list[EgaproRecord]:
    """Fallback hors-ligne : CSV avec siren + note (+ annee, raison_sociale).

    Même contrat que parse_records : on saute toute ligne sans SIREN ou sans note
    exploitable. Note attendue sur /100.
    """
    out: list[EgaproRecord] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            siren = (str(_pick(row, SIREN_COLS) or "")).strip()
            note = _pick(row, NOTE_COLS)
            if not siren or note is None:
                continue
            try:
                note_f = float(str(note).replace(",", "."))
            except (TypeError, ValueError):
                continue
            members = tuple(re.findall(r"\((\d{9})\)", str(_pick(row, UES_MEMBERS_COLS) or "")))
            out.append(EgaproRecord(
                siren=siren,
                raison_sociale=str(_pick(row, NAME_COLS) or ""),
                year=(str(_pick(row, YEAR_COLS) or "")).strip(),
                note=note_f,
                ues_name=(str(_pick(row, UES_NAME_COLS) or "").strip() or None) if members else None,
                members=members,
            ))
    return out


def latest_by_siren(records: list[EgaproRecord]) -> dict[str, EgaproRecord]:
    """Garde, par SIREN, l'enregistrement de l'année la plus récente."""
    best: dict[str, EgaproRecord] = {}
    for r in records:
        cur = best.get(r.siren)
        if cur is None or r.year > cur.year:
            best[r.siren] = r
    return best


def latest_by_member(records: list[EgaproRecord]) -> dict[str, EgaproRecord]:
    """Par SIREN de société membre d'une UES, la déclaration d'UES la plus récente."""
    best: dict[str, EgaproRecord] = {}
    for r in records:
        for m in r.members:
            cur = best.get(m)
            if cur is None or r.year > cur.year:
                best[m] = r
    return best


def fetch_for_sirens(sirens: list[str], client: httpx.Client | None = None) -> list[EgaproRecord]:
    """Interroge l'API ODS pour une liste de SIREN."""
    if not sirens:
        return []
    c = client or httpx.Client(timeout=30)
    try:
        quoted = ",".join(f'"{s}"' for s in sirens)
        r = c.get(EGAPRO_API, params={"where": f"siren in ({quoted})", "limit": 100})
        r.raise_for_status()
        return parse_records(r.json())
    finally:
        if client is None:
            c.close()
