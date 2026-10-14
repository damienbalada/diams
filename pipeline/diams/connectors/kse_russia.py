"""KSE Institute « Leave Russia » — statut des entreprises étrangères en Russie.

La base de la Kyiv School of Economics (leave-russia.org) suit plus de 4 000
entreprises présentes en Russie en 2022. La liste complète est servie par la
page elle-même (requête `?event=ajax&action=ArticleList.displayCache.1079&all=1`,
celle qu'utilise le site pour afficher toutes les fiches) : une carte par
entreprise, avec son statut, la date et la source de sa dernière décision.

Liste complète : une entreprise absente n'était pas présente en Russie, ou n'a
pas été suivie — ce n'est pas une donnée manquante (indicateur complémentaire).

Barème (statuts KSE → valeur, publié dans la méthodologie) :
  Exit Completed       1.0   sortie effective
  Withdrawal           0.85  sortie annoncée, en cours
  Suspension           0.7   activité suspendue
  Scaling Back         0.4   activité réduite
  Pausing Investments  0.2   investissements gelés, activité maintenue
  Continue Operations  0.0   activité poursuivie
"""
from __future__ import annotations

import html as htmllib
import re
from dataclasses import dataclass

LIST_URL = "https://leave-russia.org/?event=ajax&action=ArticleList.displayCache.1079&all=1"
SITE_URL = "https://leave-russia.org/"

STATUS_VALUE = {
    "Exit Completed": 1.0,
    "Withdrawal": 0.85,
    "Suspension": 0.7,
    "Scaling Back": 0.4,
    "Pausing Investments": 0.2,
    "Continue Operations": 0.0,
}
STATUS_FR = {
    "Exit Completed": "sortie effective",
    "Withdrawal": "sortie annoncée, en cours",
    "Suspension": "activité suspendue",
    "Scaling Back": "activité réduite",
    "Pausing Investments": "investissements gelés, activité maintenue",
    "Continue Operations": "activité poursuivie en Russie",
}

_CARD = re.compile(r'class="card [a-z ]+"><div class="cstatus"><div class="label status [a-z ]*"><a[^>]*>'
                   r'<span>[^<]*</span>([^<]+)</a>')
_SLUG = re.compile(r'<a href="//leave-russia\.org/([a-z0-9][a-z0-9-]*)">Show Company Details</a>')
_NAME = re.compile(r'<div class="annotation"><div><div>([^<]+)</div>')
_COUNTRY = re.compile(r'<div class="label country ([a-z]{2}) ')
_DECISION = re.compile(r'<div class="decision"><div class="date">([^<]+)<span>&nbsp;</span>'
                       r'(?:<a href="([^"]+)"[^>]*>Statement</a>)?</div><p>(.*?)</p>', re.S)


@dataclass
class KseCompany:
    slug: str
    name: str
    status: str
    country: str | None
    decision_date: str | None
    statement_url: str | None
    statement: str | None

    @property
    def value(self) -> float:
        return STATUS_VALUE[self.status]


def _clean(s: str) -> str:
    s = htmllib.unescape(re.sub(r"<[^>]+>", " ", s)).replace("\\'", "'").replace('\\"', '"')
    return re.sub(r"\s+", " ", s).strip()


def parse_list(page: str) -> list[KseCompany]:
    """Toutes les cartes de la liste ; statut inconnu : carte ignorée (pas de devinette)."""
    out: list[KseCompany] = []
    starts = [m.start() for m in _CARD.finditer(page)]
    for i, start in enumerate(starts):
        block = page[start: starts[i + 1] if i + 1 < len(starts) else len(page)]
        status = _CARD.match(block).group(1).strip()
        slug, name = _SLUG.search(block), _NAME.search(block)
        if status not in STATUS_VALUE or not slug or not name:
            continue
        country = _COUNTRY.search(block)
        dec = _DECISION.search(block)
        out.append(KseCompany(
            slug=slug.group(1), name=_clean(name.group(1)), status=status,
            country=country.group(1).upper() if country else None,
            decision_date=_clean(dec.group(1)) if dec else None,
            statement_url=htmllib.unescape(dec.group(2)) if dec and dec.group(2) else None,
            statement=_clean(dec.group(3)) if dec else None,
        ))
    return out
