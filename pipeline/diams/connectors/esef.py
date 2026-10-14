"""Connecteur ESEF — rapports financiers annuels balisés (XBRL IFRS).

Répertoire public : https://filings.xbrl.org (XBRL International), qui collecte
les dépôts ESEF des autorités de marché européennes (AMF pour la France).
Recherche par LEI — l'identifiant vérifié de l'entité, jamais par nom.

Ce que l'on lit, sans interprétation :
- faits IFRS balisés, sans dimension, de l'exercice clos : résultat avant impôt
  (ifrs-full:ProfitLossBeforeTax), charge d'impôt
  (ifrs-full:IncomeTaxExpenseContinuingOperations), résultat net
  (ifrs-full:ProfitLoss) — contrôle d'intégrité : avant impôt − impôt = net ;
- texte intégral du rapport : présence de la déclaration pays par pays bancaire
  (Code monétaire et financier, art. L511-45), citée mot pour mot.
"""
from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import date, timedelta

import httpx

BASE = "https://filings.xbrl.org"
API = f"{BASE}/api/filings"


@dataclass
class Filing:
    lei: str
    period_end: str
    date_added: str
    json_url: str
    report_url: str | None
    viewer_url: str | None
    error_count: int


def _month_end(iso: str) -> bool:
    return (date.fromisoformat(iso[:10]) + timedelta(days=1)).day == 1


def latest_filing(lei: str, client: httpx.Client, max_age_days: int = 550,
                  prefer_country: str | None = None) -> Filing | None:
    """Dépôt le plus récent (exercice clos depuis moins de ~18 mois), sans erreur de préférence ;
    à défaut, la version déposée dans le pays de l'entité (rapport dans sa langue)."""
    r = client.get(API, params={"filter[entity.identifier]": lei, "sort": "-period_end", "page[size]": 10},
                   headers={"Accept": "application/vnd.api+json"})
    r.raise_for_status()
    cutoff = (date.today() - timedelta(days=max_age_days)).isoformat()
    # Un exercice se clôt en fin de mois : écarte les dépôts intermédiaires ou atypiques.
    cands = [x["attributes"] for x in r.json().get("data", [])
             if (x["attributes"].get("period_end") or "") >= cutoff and _month_end(x["attributes"]["period_end"])]
    if not cands:
        return None
    latest = max(a["period_end"] for a in cands)
    same = sorted((a for a in cands if a["period_end"] == latest),
                  key=lambda a: (a.get("error_count") or 0, a.get("country") != prefer_country))
    a = same[0]
    return Filing(lei=lei, period_end=a["period_end"], date_added=(a.get("date_added") or "")[:10],
                  json_url=BASE + a["json_url"], report_url=BASE + a["report_url"] if a.get("report_url") else None,
                  viewer_url=BASE + a["viewer_url"] if a.get("viewer_url") else None, error_count=a.get("error_count") or 0)


CONCEPTS = {
    "pbt": "ifrs-full:ProfitLossBeforeTax",
    "tax": "ifrs-full:IncomeTaxExpenseContinuingOperations",
    "net": "ifrs-full:ProfitLoss",
    "disc": "ifrs-full:ProfitLossFromDiscontinuedOperations",
}


def annual_facts(xbrl_json: dict, period_end: str) -> dict[str, float]:
    """Faits sans dimension de l'exercice clos le `period_end` (durée ~ 1 an)."""
    end_excl = (date.fromisoformat(period_end) + timedelta(days=1)).isoformat()
    out: dict[str, float] = {}
    for f in xbrl_json.get("facts", {}).values():
        d = f.get("dimensions", {})
        extra = [k for k in d if k not in ("concept", "entity", "period", "unit", "language")]
        if extra:
            continue
        per = str(d.get("period") or "")
        if "/" not in per:
            continue
        start, end = per.split("/")
        if not end.startswith(end_excl):
            continue
        if not 350 <= (date.fromisoformat(end[:10]) - date.fromisoformat(start[:10])).days <= 380:
            continue
        for key, concept in CONCEPTS.items():
            if d.get("concept") == concept and f.get("value") not in (None, ""):
                out.setdefault(key, float(f["value"]))
    return out


def annual_currency(xbrl_json: dict, period_end: str) -> str | None:
    """Devise (ISO 4217) du résultat de l'exercice : les montants de l'extrait
    sont libellés dans la devise de présentation, jamais supposée."""
    end_excl = (date.fromisoformat(period_end) + timedelta(days=1)).isoformat()
    for f in xbrl_json.get("facts", {}).values():
        d = f.get("dimensions", {})
        if d.get("concept") not in (CONCEPTS["pbt"], CONCEPTS["net"]):
            continue
        if not str(d.get("period") or "").split("/")[-1].startswith(end_excl):
            continue
        unit = str(d.get("unit") or "")
        if unit.startswith("iso4217:"):
            return unit.split(":", 1)[1]
    return None


@dataclass
class TaxRate:
    rate_pct: float
    pbt: float
    tax: float
    net: float
    #: résultat avant impôt reconstitué (net + impôt − activités abandonnées),
    #: quand l'émetteur ne le balise pas (présentation française courante).
    derived: bool = False


def effective_tax_rate(facts: dict[str, float], tolerance: float = 0.01) -> TaxRate | None:
    """Taux effectif = impôt / résultat avant impôt, si le triplet est cohérent.

    Le signe de la charge d'impôt varie selon les émetteurs : on retient le signe
    qui vérifie « avant impôt − impôt = net » (à `tolerance` du résultat avant impôt).
    """
    pbt, tax, net = facts.get("pbt"), facts.get("tax"), facts.get("net")
    if tax is None or net is None:
        return None
    if pbt is None:
        # Pas de sous-total « avant impôt » balisé : identité comptable sur les
        # activités poursuivies. Sans contre-contrôle possible, on n'accepte
        # qu'une charge d'impôt positive et un taux plausible.
        pbt = net + tax - facts.get("disc", 0.0)
        if tax <= 0 or pbt <= 0 or not 0 <= 100 * tax / pbt <= 60:
            return None
        return TaxRate(rate_pct=round(100 * tax / pbt, 1), pbt=pbt, tax=tax, net=net, derived=True)
    if pbt <= 0:
        return None
    for t in (tax, -tax):
        if abs(pbt - t - net) <= tolerance * abs(pbt):
            return TaxRate(rate_pct=round(100 * t / pbt, 1), pbt=pbt, tax=t, net=net)
    return None


def _stub_viewer_html(page: str) -> str | None:
    """Visionneuse « stub » de filings.xbrl.org : le rapport n'est pas dans la page mais
    dans un bloc JSON (chaînes échappées en \\uXXXX). On en extrait les fragments HTML."""
    if "ixv-stub-viewer" not in page:
        return None
    m = re.search(r'<script type="application/x\.ixbrl-viewer\+json">(.*?)</script>', page, re.S)
    if not m:
        return None
    try:
        data = json.loads(m.group(1))
    except ValueError:
        return None
    out: list[str] = []

    def walk(x) -> None:
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str) and "<" in x and len(x) > 200:
            out.append(x)

    walk(data)
    return " ".join(out) or None


def report_text(url: str, client: httpx.Client) -> str:
    r = client.get(url, timeout=300, follow_redirects=True)
    r.raise_for_status()
    page = r.text
    if "ixv-stub-viewer" in page:
        # La visionneuse « stub » ne contient que les notes balisées ; le rapport complet est
        # le document qu'elle désigne (docSetFiles), dans le même dossier.
        from urllib.parse import urljoin
        m = re.search(r'"docSetFiles"\s*:\s*\[\s*"([^"]+)"', page)
        if m:
            full = client.get(urljoin(url, m.group(1)), timeout=300, follow_redirects=True)
            if full.status_code == 200:
                page = full.text
            else:
                page = _stub_viewer_html(page) or page
        else:
            page = _stub_viewer_html(page) or page
    text = html.unescape(re.sub(r"<[^>]+>", " ", page))
    return re.sub(r"\s+", " ", text)


# Titre de la section « implantations et activités » (CMF art. L511-45 II) — les
# rédactions varient d'une banque à l'autre.
_CBCR_HEADING = re.compile(
    r"(?:\d+(?:\.\d+)*\.?\s+)?(?:Informations?\s+(?:sur|relatives?\s+aux)\s+(?:les\s+)?implantations\s+et\s+"
    r"(?:les\s+)?activit[ée]s|Implantations?\s+des\s+entit[ée]s\s+pays\s+par\s+pays)",
    re.I,
)
# Ce qui suit un vrai titre de section : la phrase de l'article, ou le tableau.
_CBCR_BODY = re.compile(
    r"Conform[ée]ment|impose|doivent\s+publier|agr[ée]g[ée]es?\s+[àa]\s+l.[ée]chelle|PAYS\s+D.IMPLANTATION|"
    r"Produit\s+net\s+bancaire|L\.\s?511-45",
    re.I,
)
# Sommaire / table de concordance : le titre est suivi d'un renvoi de pages
# (« ) 316-333 ; 898-914 ») ou aussitôt d'un autre titre numéroté.
_PAGE_REF = re.compile(r"\)\s*\d{1,4}\s*[-–]\s*\d{1,4}|\s\d{1,4}\s*[-–]\s*\d{1,4}\s*;")
_NEXT_HEADING = re.compile(r"^\s*(?:relatives?[^.]{0,60}?)?\d+\.\d+\s+[A-ZÉ]")


# Repli : la référence légale rédigée dans une phrase, sans titre de section
# (« … pris pour l'application de l'article L. 511-45 …, sont détaillées
# ci-après. Ces informations … portent sur les implantations et activités … »).
_SENTENCE_511 = re.compile(r"[^.]{0,400}L\.?\s?511-45[^.]{0,300}\.(?:[^.]{0,260}\.)?")


def cbcr_quote(text: str) -> str | None:
    """Titre + début de la section « implantations et activités », hors sommaire."""
    for m in _CBCR_HEADING.finditer(text):
        first = text[m.start()]
        if not (first.isdigit() or first.isupper()):  # « Les informations relatives aux… » : un renvoi
            continue
        after = text[m.end(): m.end() + 500]
        if _NEXT_HEADING.match(after) or _PAGE_REF.search(after[:220]) or not _CBCR_BODY.search(after):
            continue
        end = text.find(". ", m.end() + 40)
        end = m.end() + 320 if end == -1 or end - m.start() > 420 else end + 1
        return text[m.start(): end].strip()
    for m in _SENTENCE_511.finditer(text):
        s = m.group(0).strip()
        if (re.search(r"implantations\s+et\s+(?:les\s+)?activit", s, re.I)
                and not re.search(r"non\s+coop", s, re.I) and not _PAGE_REF.search(s)):
            return s[:450]
    return None
