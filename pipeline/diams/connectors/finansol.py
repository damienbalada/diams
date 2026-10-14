"""Connecteur Finansol — produits d'épargne labellisés (FAIR).

Source : liste officielle publiée par FAIR (association issue de Finansol), qui
attribue et contrôle chaque année le label Finansol (règlement du label :
financement effectif d'activités à utilité sociale ou environnementale,
transparence ; exclusions sectorielles dont les énergies fossiles depuis 2025).

Rattachement CONSERVATEUR : un produit n'est rattaché à une entité que si le
champ « Distribué par » est exactement le nom commercial de l'établissement
(table explicite ci-dessous). Une société de gestion filiale (Amundi, Mirova…)
n'est jamais rattachée d'office à son groupe : ce serait une attribution, pas
un fait.
"""
from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import dataclass

import httpx

LIST_URL = "https://www.finance-fair.org/fr/quels-sont-les-placements-labellises-finansol"
BASE = "https://www.finance-fair.org"

# Nom commercial exact (normalisé) du distributeur → slug(s) DIAMS. Volontairement
# absents : sociétés de gestion filiales (Amundi, Mirova, BNP Paribas AM, Natixis
# Interépargne, Arkéa AM…) et fédérations régionales (Crédit Mutuel de Bretagne…),
# dont le rattachement à un groupe serait une attribution, pas un fait.
DISTRIBUTORS: dict[str, tuple[str, ...]] = {
    "la nef": ("la-nef",),
    "credit cooperatif": ("credit-cooperatif",),
    "la banque postale": ("la-banque-postale",),
    "bnp paribas": ("bnp-paribas",),
    "societe generale": ("societe-generale",),
    "credit agricole": ("credit-agricole",),
    "lcl": ("lcl",),
    "cic": ("cic",),
    "credit mutuel alliance federale": ("credit-mutuel-alliance-federale",),
    "credit mutuel / cic": ("credit-mutuel-alliance-federale", "cic"),
    "boursobank": ("boursobank",),
    "fortuneo": ("fortuneo",),
    "monabanq": ("monabanq",),
    "credit mutuel arkea": ("credit-mutuel-arkea",),
    "caisse d'epargne": ("caisse-epargne",),
    "banque populaire": ("banque-populaire",),
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = s.replace("’", "'")
    return re.sub(r"\s+", " ", s).strip()


@dataclass
class Product:
    title: str
    url: str
    distributor: str
    manager: str
    kind: str


_ITEM = re.compile(r'<li\s+class="entity-list-item products-item">(.*?)</li>', re.S)


def _field(block: str, cls: str) -> str:
    m = re.search(rf'class="[^"]*{cls}[^"]*"[^>]*>(.*?)</p>', block, re.S)
    if not m:
        return ""
    inner = re.search(r'item-card-text-highlight">(.*?)</span>', m.group(1), re.S)
    raw = inner.group(1) if inner else m.group(1)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))).strip()


def parse_page(page_html: str) -> list[Product]:
    out: list[Product] = []
    for block in _ITEM.findall(page_html):
        t = re.search(r'field--name-title[^>]*>(.*?)</span>', block, re.S)
        u = re.search(r'<a href="(/fr/produits/[^"]+)"', block)
        if not (t and u):
            continue
        out.append(Product(
            title=re.sub(r"\s+", " ", html.unescape(t.group(1))).strip(),
            url=BASE + u.group(1),
            distributor=_field(block, "item-card-product-distributor"),
            manager=_field(block, "item-card-product-manager"),
            kind=_field(block, "item-card-type"),
        ))
    return out


def fetch_all(client: httpx.Client, max_pages: int = 40) -> list[Product]:
    products: list[Product] = []
    for page in range(max_pages):
        r = client.get(LIST_URL, params={"page": page} if page else None, follow_redirects=True)
        r.raise_for_status()
        items = parse_page(r.text)
        if not items:
            break
        products.extend(items)
    return products


def by_entity(products: list[Product]) -> dict[str, list[Product]]:
    out: dict[str, list[Product]] = {}
    for p in products:
        for slug in DISTRIBUTORS.get(norm(p.distributor), ()):
            out.setdefault(slug, []).append(p)
    return out
