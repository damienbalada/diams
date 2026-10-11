"""Registre de transparence de l'UE — export ouvert complet (XML).

La Commission publie chaque jour l'export de tous les inscrits
(https://transparency-register.europa.eu/odplastorganisationxml_en, jeu de
données « Transparency Register » de data.europa.eu). Pour chaque inscrit :
numéro, nom, catégorie, site, date de mise à jour et, pour le dernier exercice
clos, la fourchette des coûts de représentation d'intérêts déclarés.

Lecture en flux (fichier de plus de 100 Mo), catégorie « Companies & groups »
seulement : une fédération ou un cabinet n'est pas l'entreprise.
"""
from __future__ import annotations

import io
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass

EXPORT_URL = "https://transparency-register.europa.eu/odplastorganisationxml_en"
COMPANIES = "Companies & groups"


@dataclass
class Registrant:
    code: str
    name: str
    category: str
    website: str | None
    last_update: str | None
    year_start: str | None
    year_end: str | None
    cost_min: float | None
    cost_max: float | None
    fte: float | None

    @property
    def cost_mid(self) -> float | None:
        if self.cost_min is None or self.cost_max is None:
            return None
        return (self.cost_min + self.cost_max) / 2


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _find(el: ET.Element, *path: str) -> ET.Element | None:
    cur: ET.Element | None = el
    for name in path:
        if cur is None:
            return None
        cur = next((c for c in cur if _local(c.tag) == name), None)
    return cur


def _text(el: ET.Element, *path: str) -> str | None:
    node = _find(el, *path)
    return node.text.strip() if node is not None and node.text and node.text.strip() else None


def _num(s: str | None) -> float | None:
    try:
        return float(s) if s is not None else None
    except ValueError:
        return None


# L'export est déclaré en XML 1.1, qui autorise des références à des caractères
# de contrôle (« &#1; ») que les analyseurs XML 1.0 refusent : on les remplace
# par une espace (elles n'apparaissent que dans des textes libres).
_CTRL_REF = re.compile(rb"&#(?:x0*(?:[0-8bBcCeEfF]|1[0-9a-fA-F])|0*(?:[0-8]|1[124-9]|2[0-9]|3[01]));")


def sanitize(raw: bytes) -> bytes:
    raw = raw.replace(b"<?xml version='1.1'", b"<?xml version='1.0'", 1)
    return _CTRL_REF.sub(b" ", raw)


def parse_export(raw: bytes) -> tuple[str | None, list[Registrant]]:
    """(date d'export, inscrits de la catégorie entreprises) depuis l'export brut."""
    export_date: str | None = None
    out: list[Registrant] = []
    for _event, el in ET.iterparse(io.BytesIO(sanitize(raw)), events=("end",)):
        tag = _local(el.tag)
        if tag == "exportDate" and el.text:
            export_date = el.text.strip()[:10]
        if tag != "interestRepresentative":
            continue
        category = _text(el, "registrationCategory") or ""
        if category == COMPANIES:
            closed = _find(el, "financialData", "closedYear")
            cmin = cmax = None
            if closed is not None:
                cmin = _num(_text(closed, "costs", "range", "min"))
                cmax = _num(_text(closed, "costs", "range", "max"))
                absolute = _num(_text(closed, "costs", "absoluteCost"))
                if absolute is not None and cmin is None:
                    cmin = cmax = absolute
            out.append(Registrant(
                code=_text(el, "identificationCode") or "",
                name=_text(el, "name", "originalName") or "",
                category=category,
                website=_text(el, "webSiteURL"),
                last_update=(_text(el, "lastUpdateDate") or "")[:10] or None,
                year_start=_text(closed, "startDate") if closed is not None else None,
                year_end=_text(closed, "endDate") if closed is not None else None,
                cost_min=cmin, cost_max=cmax,
                fte=_num(_text(el, "members", "membersFTE")),
            ))
        el.clear()
    return export_date, out
