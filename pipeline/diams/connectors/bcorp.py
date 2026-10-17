"""Connecteur B Corp — annuaire officiel de B Lab.

Deux temps, parce qu'un nom ne suffit pas (la fiche « Alpine » est celle d'un
fabricant de protections auditives, pas de la marque automobile) :

1. DÉCOUVERTE (`discover`) : pour chaque entité, on consulte les seules fiches
   dont l'adresse découle de son nom ; une fiche certifiée au nom identique est
   un CANDIDAT, affiché avec son site et son activité. Rien n'est écrit.
2. IMPORT : seules les paires déclarées dans `VERIFIED` (entité ↔ fiche B Lab,
   avec le domaine du site attendu) sont importées, et seulement si la fiche est
   toujours certifiée et pointe vers ce site. Déclarer une paire = une décision
   humaine versionnée.

Fiche absente = aucune preuve : l'absence de certification n'est pas un fait
négatif.
"""
from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import dataclass

import httpx

PAGE = "https://www.bcorporation.net/en-us/find-a-b-corp/company/{}/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}

# Paires vérifiées (revue humaine) : slug DIAMS → (slug de la fiche B Lab, domaine du site attendu).
VERIFIED: dict[str, tuple[str, str]] = {
    "boursobank": ("boursorama", "boursobank"),        # BoursoBank, filiale de Société Générale
    "innocent": ("innocent-drinks", "innocentdrinks"),  # innocent Drinks, marque de Coca-Cola
    "isigny-sainte-mere": ("isigny-sainte-mere", "isigny-ste-mere"),  # coopérative laitière normande
    # Découverte du 16/10/2026, relue : domaine du site de la fiche B Lab et propriétaire connu.
    "isigny-sainte-mere-marque": ("isigny-sainte-mere", "isigny-ste-mere"),  # marque de la coopérative
    "edgard-cooper": ("edgard-cooper", "edgardcooper"),   # aliments pour animaux, General Mills
    "la-marzocco": ("la-marzocco", "lamarzocco"),         # machines à café, De'Longhi
    "modibodi": ("modibodi", "modibodi"),                 # sous-vêtements menstruels, Essity
    "nxtfood": ("nxtfood", "nxtfood"),                    # groupe français (marque Accro)
    "ponthier": ("ponthier", "ponthier"),                 # purées de fruits, Corrèze
    "ponthier-marque": ("ponthier", "ponthier"),
    "rogue-creamery": ("rogue-creamery", "roguecreamery"),  # fromagerie de l'Oregon, Savencia
    "sipsmith": ("sipsmith", "sipsmith"),                 # gin, Suntory Global Spirits
    "valrhona": ("valrhona", "valrhona"),                 # chocolat, Savencia
    # Fiches retrouvées le 17/10/2026 (adresse de la fiche distincte du nom de l'entité), relues.
    "ben-jerrys": ("ben-and-jerrys", "benjerry"),         # Ben & Jerry's Homemade, Inc.
    "weleda": ("weleda-a-g-group", "weleda"),             # Weleda AG Group (25 sociétés)
    "weleda-marque": ("weleda-a-g-group", "weleda"),
    "aesop": ("aesop", "aesop"),                          # Emeis Cosmetics (Aesop), L'Oréal
    "nespresso": ("nespresso-global", "nespresso"),       # Nespresso Global, Nestlé
    "expanscience": ("laboratoires-expanscience", "expanscience"),  # Laboratoires Expanscience (Mustela)
    "ecotone-france": ("wessanen", "ecotone"),            # ecotone (ex-Wessanen), fiche de groupe opérant en France
}


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"&", " and ", s)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def norm_name(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


@dataclass
class BCorp:
    name: str
    url: str
    certified_since: str | None
    score: float | None
    operates_in: str | None
    website: str | None = None
    industry: str | None = None


def parse_page(page_html: str, url: str) -> BCorp | None:
    title = re.search(r"<title>(.*?)</title>", page_html, re.S)
    if not title or "Certified B Corporation" not in title.group(1):
        return None
    name = html.unescape(title.group(1).split(" - Certified B Corporation")[0]).strip()
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", page_html, flags=re.S)))
    since = re.search(r"Certified Since ([A-Z][a-z]+ \d{4})", text)
    # Fiches au référentiel 2.2 (2026) : l'année précède le libellé (« Nespresso 2022 Certified since »).
    since = since or re.search(r"\b((?:19|20)\d{2}) Certified since", text)
    score = re.search(r"earned an overall score of (\d+(?:\.\d+)?)", text)
    operates = re.search(r"Operates In (.+?) (?:Website|Sector|Industry|$)", text)
    website = re.search(r"Website (\S+)", text)
    industry = re.search(r"Industry (.+?) Sector", text)
    return BCorp(name=name, url=url, certified_since=since.group(1) if since else None,
                 score=float(score.group(1)) if score else None,
                 operates_in=operates.group(1).strip() if operates else None,
                 website=website.group(1) if website else None,
                 industry=industry.group(1).strip() if industry else None)


def candidates(entity: dict) -> list[tuple[str, set[str]]]:
    """(slug B Lab à essayer, noms acceptés) pour une entité — découverte seulement."""
    names = {n for n in (entity.get("display_name"), entity.get("legal_name")) if n}
    accepted = {norm_name(n) for n in names}
    slugs = []
    for s in [entity["slug"], *(slugify(n) for n in names)]:
        if s and s not in slugs:
            slugs.append(s)
    return [(s, accepted) for s in slugs]


def fetch(bslug: str, client: httpx.Client) -> BCorp | None:
    url = PAGE.format(bslug)
    r = client.get(url, headers=HEADERS, follow_redirects=True)
    return parse_page(r.text, url) if r.status_code == 200 else None


def verified(slug: str, client: httpx.Client) -> BCorp | None:
    """Fiche d'une paire vérifiée, si toujours certifiée et pointant vers le site attendu."""
    if slug not in VERIFIED:
        return None
    bslug, domain = VERIFIED[slug]
    b = fetch(bslug, client)
    return b if b and b.website and domain in b.website.lower() else None


def discover(entity: dict, client: httpx.Client) -> BCorp | None:
    """Candidat (nom identique), à confirmer par un humain avant d'entrer dans VERIFIED."""
    for bslug, accepted in candidates(entity):
        url = PAGE.format(bslug)
        r = client.get(url, headers=HEADERS, follow_redirects=True)
        if r.status_code != 200:
            continue
        b = parse_page(r.text, url)
        if b and norm_name(b.name) in accepted:
            return b
    return None
