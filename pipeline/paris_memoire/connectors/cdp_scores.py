"""CDP — notes publiques 2025 de toutes les entreprises évaluées (climat, eau).

CDP publie, sur sa page « Scores and A Lists », la liste complète des notes
publiques de l'année (plus de 30 000 entreprises) dans une visualisation
Flourish. Chaque note est une icône dont le nom porte la lettre
(« Climate-B-minus-Icon… » = B-). On la lit telle quelle.

Valeurs hors lettre :
  « Did not disclose »            → F : sollicitée par CDP, l'entreprise n'a pas
                                     répondu (c'est la note F de la méthode CDP) ;
  « See disclosing organisation »  → ignorée : c'est une autre entité (la société
                                     mère) qui répond ;
  « Not Scored » ou vide           → ignorée (pas de note).

Barème : celui de connectors/cdp.py (A = 1,00 … D- = 0,13, F = 0).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from . import flourish
from .cdp import GRADE_MAP

SCORES_VIS = 28119771          # « Public corp scores 2025 » (page cdp.net/en/data/scores)
SCORES_YEAR = 2025
SCORES_PAGE = "https://www.cdp.net/en/data/scores"

_ICON = re.compile(r"/(Climate|Water|Forests)-([A-D])(-minus)?-Icon", re.I)


@dataclass
class CdpScore:
    company: str
    country: str
    climate: str | None   # lettre (A, A-, …, F) ou None
    water: str | None


def grade(cell: str | None) -> str | None:
    """Cellule de la visualisation → lettre CDP, ou None (pas de note)."""
    if not cell:
        return None
    if cell.strip() == "Did not disclose":
        return "F"
    m = _ICON.search(cell)
    if not m:
        return None
    letter = m.group(2).upper() + ("-" if m.group(3) else "")
    return letter if letter in GRADE_MAP else None


def parse_scores(html: str) -> list[CdpScore]:
    out = []
    for r in flourish.table_rows(html):
        name = (r.get("Company name") or "").strip()
        if not name:
            continue
        out.append(CdpScore(name, (r.get("Country / Area") or "").strip(),
                            grade(r.get("Climate")), grade(r.get("Water"))))
    return out
