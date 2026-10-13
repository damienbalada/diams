"""KSE Institute « Leave Russia » — position de chaque groupe face à la Russie.

Charge la liste complète (connectors/kse_russia.py), rapproche chaque entreprise
d'un GROUPE suivi (table explicite, puis correspondance nette du nom ; jamais une
filiale ni une marque listée à part) et écrit le statut sur GEO_RUSSIA_EXIT
(source KSE_LEAVE_RUSSIA, ONG auditée → publication automatique). La date
d'observation est celle de la consultation : le statut est tenu à jour par KSE.

Les lignes saisies à la main avant le connecteur (`curation-v1`) sur cet
indicateur sont retirées (`remplace:import_kse`).

Usage :
    python -m paris_memoire.import_kse [--file liste.html] [--apply]
"""
from __future__ import annotations

import argparse
import datetime as dt

import httpx

from . import config, supabase_client
from .connectors import kse_russia as kse
from .load import EvidenceRow, insert_evidence
from .normalize.names import normalize_name

# Slug KSE -> slug DIAMS (vérifiés à la main sur la fiche KSE).
ALIASES = {
    "bmw-group": "bmw",
    "renault-group": "renault",
    "loreal": "loreal",
    "coca-cola": "coca-cola",
    "mondelez": "mondelez",
    "mercedes-benz-group": "mercedes-benz",
    "volkswagen-group": "volkswagen",
    "procter-gamble": "procter-gamble",
    "anheuser-busch-inbev": "ab-inbev",
    "h-m": "hm-group",
    "mercedes-benz-group": "mercedes-benz",
    "schwarz-group": "schwarz-gruppe",
    "burger-king-restaurant-brands": "rbi",
    "toyota-motor-corporation": "toyota",
    "uniqlo-fast-retailing": "fast-retailing",
    "facebook": "meta",
}
# Cartes KSE à ne jamais rapprocher d'un groupe suivi (autre société, filiale ou marque).
NEVER = {"coca-cola-hbc-ag", "mercedes-benz-mobility", "t-and-t-group", "kelloggs"}
# Noms trop génériques pour une correspondance exacte.
GENERIC = {"group", "groupe", "holding", "holdings", "international", "company", "corporation"}

_MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"], start=1)}


def fr_date(s: str | None) -> str | None:
    """« May 17, 2024 » -> « 17/05/2024 »."""
    try:
        month, day, year = s.replace(",", "").split()
        return f"{int(day):02d}/{_MONTHS[month]:02d}/{year}"
    except (AttributeError, KeyError, ValueError):
        return None


def match_group(c: kse.KseCompany, groups: list[dict]) -> dict | None:
    if c.slug in NEVER:
        return None
    by_slug = {g["slug"]: g for g in groups}
    if c.slug in ALIASES:
        return by_slug.get(ALIASES[c.slug])
    if c.slug in by_slug:
        return by_slug[c.slug]
    # Égalité exacte des noms normalisés seulement : une inclusion (« T&T Group »
    # contre « H & M … Group ») a déjà produit un faux rapprochement.
    name = normalize_name(c.name)
    if len(name) < 3 or name in GENERIC:
        return None
    for g in groups:
        for key in ("display_name", "legal_name"):
            if g.get(key) and normalize_name(g[key]) == name:
                return g
    return None


def build_row(slug: str, c: kse.KseCompany, today: str) -> EvidenceRow:
    when = fr_date(c.decision_date)
    statement = (c.statement or "").strip()
    if len(statement) > 280:
        statement = statement[:279].rsplit(" ", 1)[0] + "…"
    detail = f" ; dernière décision {('le ' + when) if when else ''} : « {statement} »" if statement else ""
    return EvidenceRow(
        entity_slug=slug, indicator_code="GEO_RUSSIA_EXIT", source_code="KSE_LEAVE_RUSSIA",
        nature="result", observed_on=today, value_type="category",
        value_text=c.status, normalized_value=kse.STATUS_VALUE[c.status], confidence=0.8,
        source_url=f"https://leave-russia.org/{c.slug}",
        excerpt=(f"KSE Institute, base « Leave Russia » (consultée le {dt.date.fromisoformat(today):%d/%m/%Y}) : "
                 f"« {c.name} » — {kse.STATUS_FR[c.status]}{detail}"),
        reviewer="import_kse",
    )


def _rest(c: httpx.Client, method: str, table: str, **kw) -> httpx.Response:
    r = c.request(method, f"{config.SUPABASE_URL}/rest/v1/{table}",
                  headers={**supabase_client._headers(), **kw.pop("headers", {})}, **kw)
    r.raise_for_status()
    return r


def main() -> None:
    ap = argparse.ArgumentParser(description="KSE Leave Russia : statut de chaque groupe suivi.")
    ap.add_argument("--file", help="liste déjà téléchargée (sinon téléchargée)")
    ap.add_argument("--apply", action="store_true", help="écrit en base (sinon dry-run)")
    args = ap.parse_args()
    config.require_supabase()
    today = dt.date.today().isoformat()
    with httpx.Client(timeout=180, follow_redirects=True) as c:
        if args.file:
            page = open(args.file, encoding="utf-8").read()
        else:
            r = c.get(kse.LIST_URL, headers={"User-Agent": "Mozilla/5.0 (DIAMS)", "X-Requested-With": "XMLHttpRequest"})
            r.raise_for_status()
            page = r.text
        companies = kse.parse_list(page)
        print(f"{len(companies)} entreprises dans la liste KSE")
        if len(companies) < 3000:
            raise SystemExit("Liste incomplète (moins de 3 000 entreprises) : rien n'est écrit.")
        ents = supabase_client.get_all(c, "entities", {"select": "id,slug,legal_name,display_name,parent_id"})
        groups = [e for e in ents if not e.get("parent_id")]
        rows, seen = [], set()
        for co in companies:
            g = match_group(co, groups)
            if g and g["slug"] not in seen:
                seen.add(g["slug"])
                rows.append(build_row(g["slug"], co, today))
                print(f"  ✔ {g['slug']:<18} {co.status:<20} ({co.name}, {co.slug})")
        print(f"{len(rows)} groupes suivis présents dans la base KSE")
        ind = _rest(c, "GET", "indicators", params={"select": "id", "code": "eq.GEO_RUSSIA_EXIT"}).json()[0]["id"]
        old = _rest(c, "GET", "evidence", params={
            "select": "id", "indicator_id": f"eq.{ind}",
            "reviewer": "eq.curation-v1", "review_status": "eq.approved"}).json()
        print(f"{len(old)} ligne(s) curation-v1 à retirer")
        if not args.apply:
            print("(dry-run : rien n'a été écrit. Relancer avec --apply.)")
            return
        print(insert_evidence(rows, c))
        if old:
            _rest(c, "PATCH", "evidence", params={"id": f"in.({','.join(o['id'] for o in old)})"},
                  headers={"Prefer": "return=minimal"},
                  json={"review_status": "rejected", "reviewer": "remplace:import_kse"})
            print(f"{len(old)} ligne(s) curation-v1 retirées")


if __name__ == "__main__":
    main()
