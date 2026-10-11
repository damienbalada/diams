"""BBFAW (Business Benchmark on Farm Animal Welfare) — figure des tiers du rapport.

Le rapport annuel publie la liste COMPLÈTE des entreprises évaluées dans une
figure (« Company Tier Rankings and Impact Ratings ») : une colonne par tier.
Le texte seul ne dit pas dans quelle colonne se trouve un nom : on lit la
position horizontale de chaque ligne sur la page (déterministe), puis on vérifie
le résultat contre le tableau des mouvements de tier publié page suivante. Les
lettres de note d'impact (A à F) et les flèches sont placées de façon
irrégulière dans le PDF : elles sont ignorées (seul le tier compte dans la note).

Module pur (lecture d'un PDF local) ; l'accès réseau et base est dans
import_bbfaw.py.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

REPORT_URL = "https://bbfaw.com/media/2209/bbfaw-benchmark-2025.pdf"
REPORT_YEAR = 2025
FIGURE_PAGE = 21          # page (1-indexée) de la figure 1.1 dans le rapport 2025
MOVES_PAGE = 22           # tableau 1.2 (mouvements de tier) pour contrôle

# Bornes horizontales des colonnes (milieux entre les en-têtes « Tier n »,
# relevés à x = 45, 131, 217, 302, 388, 473 dans le rapport 2025).
_COLUMN_EDGES = (88, 174, 260, 345, 430)
_Y_MIN, _Y_MAX = 40, 648   # sous les en-têtes et effectifs de colonnes, au-dessus des notes

# Une ligne à moins de 8 points de la précédente prolonge le même nom (les
# entreprises sont espacées d'environ 9,6 points, les suites de nom de 6).
_CONTINUATION_GAP = 8
_MARK = r"(?:[A-F]|↑|↓|�)"
_LONE_MARK = re.compile(rf"^{_MARK}(?:\s*{_MARK})*$")
_EDGE_MARKS = re.compile(rf"^(?:{_MARK}\s+)+|(?:\s+{_MARK})+\s*$")


@dataclass
class BbfawEntry:
    company: str
    tier: int


def column(x: float) -> int:
    for i, edge in enumerate(_COLUMN_EDGES):
        if x < edge:
            return i + 1
    return 6


def clean(name: str) -> str:
    name = _EDGE_MARKS.sub("", name.replace("�", "’").strip())
    return re.sub(r"\s+", " ", name).strip()


def _lines(page) -> dict[int, list[tuple[float, str]]]:
    """Lignes de texte par colonne : [(y, texte)], de haut en bas."""
    items: list[tuple[float, float, str]] = []

    def visit(text, cm, tm, font, size):
        t = text.replace("\n", " ").strip()
        if t and not _LONE_MARK.match(t):      # note d'impact ou flèche seule
            items.append((tm[4], tm[5], t))

    page.extract_text(visitor_text=visit)
    cols: dict[int, dict[int, list[tuple[float, str]]]] = {}
    for x, y, t in items:
        if _Y_MIN <= y <= _Y_MAX:
            cols.setdefault(column(x), {}).setdefault(round(y), []).append((x, t))
    return {
        col: [(y, " ".join(t for _x, t in sorted(parts)))
              for y, parts in sorted(rows.items(), key=lambda kv: -kv[0])]
        for col, rows in cols.items()
    }


def parse_figure(page) -> list[BbfawEntry]:
    """Entreprises de la figure des tiers, avec leur tier (colonne).

    Une ligne très proche de la précédente dans la même colonne prolonge son nom
    (« 2 Sisters Food Group » / « (Boparan Holdings Ltd) »).
    """
    out: list[BbfawEntry] = []
    for tier, lines in sorted(_lines(page).items()):
        current: BbfawEntry | None = None
        prev_y: float | None = None
        for y, text in lines:
            name = clean(text)
            if not name:
                continue
            if current is not None and prev_y is not None and prev_y - y < _CONTINUATION_GAP:
                current.company = clean(f"{current.company} {name}")
            else:
                current = BbfawEntry(name, tier)
                out.append(current)
            prev_y = y
    return out


_MOVE = re.compile(r"^\d+\s+(.+?)\s+([1-6])\s+([1-6])\s*$")


def parse_moves(text: str) -> dict[str, int]:
    """Tableau des mouvements : entreprise -> tier de l'année du rapport."""
    out: dict[str, int] = {}
    for line in text.splitlines():
        m = _MOVE.match(line.strip())
        if m:
            out[clean(m.group(1))] = int(m.group(2))
    return out


def parse_counts(page) -> dict[int, int]:
    """Effectif imprimé en tête de chaque colonne (tier -> nombre d'entreprises)."""
    counts: dict[int, int] = {}

    def visit(text, cm, tm, font, size):
        t = text.strip()
        if t.isdigit() and _Y_MAX < tm[5] < _Y_MAX + 15:
            counts[column(tm[4])] = int(t)

    page.extract_text(visitor_text=visit)
    return counts


def read_report(path: str) -> tuple[list[BbfawEntry], dict[str, int], dict[int, int]]:
    from pypdf import PdfReader

    reader = PdfReader(path)
    page = reader.pages[FIGURE_PAGE - 1]
    moves = parse_moves(reader.pages[MOVES_PAGE - 1].extract_text() or "")
    return parse_figure(page), moves, parse_counts(page)


def check(entries: list[BbfawEntry], moves: dict[str, int], counts: dict[int, int]) -> list[str]:
    """Écarts avec le tableau des mouvements et les effectifs par tier (doit être vide)."""
    tiers = {e.company: e.tier for e in entries}
    issues = [f"{name} : figure {tiers.get(name)} / tableau {t}"
              for name, t in moves.items() if tiers.get(name) != t]
    for tier in range(1, 7):
        n = sum(1 for e in entries if e.tier == tier)
        if counts.get(tier, 0) != n:
            issues.append(f"tier {tier} : {n} lus pour {counts.get(tier, 0)} annoncés")
    return issues
