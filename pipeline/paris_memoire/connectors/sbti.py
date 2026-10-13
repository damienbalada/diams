"""Connecteur SBTi — Science Based Targets initiative.

Données : export « Companies taking action » téléchargeable sur
https://sciencebasedtargets.org/companies-taking-action (XLSX ou CSV).

Produit ENV_SBTI_VALIDATED (objectif de court terme, « near term »). Le cœur
anti-greenwashing du pilier ENV :
  * « Validated Targets » (ex-« Targets Set ») + 1.5°C -> 1.0, nature=commitment
  * « Validated Targets » (autre classification)       -> 0.6, nature=commitment
  * « Commitment to Set Targets » (ex-« Committed »)   -> 0.5, nature=commitment
  * « Commitment Removed » (engagement retiré)         -> 0.0, nature=result
Un objectif, même validé, reste une promesse sur l'avenir (décision de l'éditeur,
v0.7.1) : le moteur lui applique le multiplicateur des engagements (x0.4) et
son plafond (0.5). La preuve est la baisse réelle des émissions (ENV_GHG_TREND).

Rapprochement : LEI d'abord (identifiant légal, colonne `lei` de l'export), puis
égalité exacte des noms normalisés, résultat unique exigé. Jamais d'inclusion :
« H&M Group » ne doit pas désigner une autre société dont le nom le contient.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass

from ..normalize.names import normalize_name

SBTI_SOURCE_URL = "https://sciencebasedtargets.org/companies-taking-action"

# En-tetes normalises (underscores et tirets ramenes a des espaces) : l'export
# SBTi a change de convention au fil du temps (Company Name, puis
# Near term - Target Status, puis aujourd'hui company_name, near_term_status).
# On tolere les trois formes plutot que de casser a chaque refonte de la source.
NAME_COLS = ("company name", "company", "name")
STATUS_COLS = ("near term status", "near term target status", "target status", "status")
CLASSIF_COLS = ("near term target classification", "target classification", "classification")


def _norm_key(k: str) -> str:
    """Cle d'en-tete comparable : minuscule, _/- -> espace, espaces compactes."""
    k = k.lower().strip().replace("_", " ").replace("-", " ")
    return " ".join(k.split())


@dataclass
class SbtiRow:
    company: str
    normalized_value: float
    nature: str
    label: str
    lei: str | None = None
    classification: str | None = None


def _interpret(status: str, classification: str) -> tuple[float, str] | None:
    """(normalized_value, nature) selon statut + classification. None si inconnu."""
    s = status.strip().lower()
    c = classification.strip().lower()
    if "targets set" in s or s == "set" or "validated" in s:
        return (1.0, "commitment") if c.startswith("1.5") else (0.6, "commitment")
    if "committed" in s or "commitment to set" in s:
        return (0.5, "commitment")
    if "removed" in s:
        return (0.0, "result")
    return None


def parse_csv(path: str) -> list[SbtiRow]:
    """Parse l'export SBTi (CSV, colonnes tolerantes a la casse)."""
    rows: list[SbtiRow] = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = {_norm_key(k): k for k in (reader.fieldnames or [])}
        name_col = next((fields[k] for k in NAME_COLS if k in fields), None)
        status_col = next((fields[k] for k in STATUS_COLS if k in fields), None)
        classif_col = next((fields[k] for k in CLASSIF_COLS if k in fields), None)
        if not name_col or not status_col:
            raise ValueError(
                f"Colonnes introuvables (vues: {reader.fieldnames}). "
                "Attendu: Company Name + Target Status. "
                "Si le fichier est en .xlsx, l'exporter/convertir en CSV.")
        for r in reader:
            company = (r.get(name_col) or "").strip()
            if not company:
                continue
            interp = _interpret(r.get(status_col) or "", (r.get(classif_col) or "") if classif_col else "")
            if interp is None:
                continue
            value, nature = interp
            lei_col = fields.get("lei")
            rows.append(SbtiRow(company=company, normalized_value=value, nature=nature,
                                label=(r.get(status_col) or "").strip(),
                                lei=((r.get(lei_col) or "").strip().upper() or None) if lei_col else None,
                                classification=((r.get(classif_col) or "").strip() or None) if classif_col else None))
    return rows


GENERIC = {"group", "groupe", "holding", "holdings", "international", "company", "corporation"}

# Slug DIAMS -> nom exact dans l'export SBTi, quand le LEI manque côté DIAMS et que
# le nom diffère (vérifié à la main dans l'export).
ALIASES = {
    "bmw": "BMW Group",
    "google": "Alphabet Inc.",
    "bonduelle": "Bonduelle Group",
    "axa": "AXA Group",
    "schwarz-gruppe": "Schwarz Gruppe (Lidl, Kaufland, Schwarz Produktion, PreZero, Schwarz Digits)",
    "shein": "ROADGET BUSINESS PTE. LTD. (owner of the SHEIN brand)",
    "delonghi": "De' Longhi Group",
    "lego": "The LEGO Group",
    # Ecotone (Bjorg, Clipper, Alter Eco…) : seule entrée « ECOTONE », située en France.
    "ecotone-france": "ECOTONE",
    "alsace-lait": "Alsace Lait",
    "laiterie-de-saint-denis-de-l-hotel": "LSDH LAITERIE DE SAINT-DENIS DE L'HOTEL",
    "expanscience": "Expanscience",
    # Nutrition & Santé, filiale opérationnelle dont Nardobel est la société mère directe (GLEIF).
    "nardobel": "Nutrition&Santé",
}


def match_company(entity: dict, rows: list[SbtiRow]) -> SbtiRow | None:
    """LEI exact, sinon nom normalisé identique ; plusieurs candidats : on s'abstient."""
    if entity.get("slug") in ALIASES:
        want = " ".join(ALIASES[entity["slug"]].split())
        hits = [r for r in rows if " ".join(r.company.split()) == want]
        return hits[0] if len(hits) == 1 else None
    lei = (entity.get("lei") or "").strip().upper()
    if lei:
        by_lei = [r for r in rows if r.lei == lei]
        if len(by_lei) == 1:
            return by_lei[0]
    keys = {normalize_name(entity.get(k) or "") for k in ("legal_name", "display_name")}
    keys = {k for k in keys if len(k) >= 3 and k not in GENERIC}
    hits = [r for r in rows if normalize_name(r.company) in keys]
    return hits[0] if len(hits) == 1 else None
