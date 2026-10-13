"""Fur Free Retailer (Fur Free Alliance) — marques et enseignes membres.

Le programme publie sur sa page d'accueil la liste complète de ses membres (une
carte par enseigne : nom, logo, fiche). Être membre, c'est s'être engagé, de
façon vérifiée par l'alliance, à ne vendre aucune fourrure animale. On l'écrit
sur ANI_FUR_FREE (un label : présent, il compte ; absent, il ne dit rien),
source FUR_FREE (ONG auditée) : publication automatique.

Rapprochement : nom exact (normalisé, au moins 3 caractères) ou table
explicite ; l'entité nommée seulement (une marque membre ne rend pas son groupe
membre). Les lignes saisies à la main avant le connecteur (`curation-v1`) sont
retirées (`remplace:import_fur_free`).

Usage :
    python -m paris_memoire.import_fur_free [--file accueil.html] [--apply]
"""
from __future__ import annotations

import argparse
import datetime as dt
import html as htmllib
import re

import httpx

from . import config, supabase_client
from .load import EvidenceRow, insert_evidence
from .normalize.names import normalize_name

LIST_URL = "https://furfreeretailer.com/"
_ITEM = re.compile(r'<a href="(https://furfreeretailer\.com/blog/retailers/[^"]+/)" class="retailer-overview__grid__item'
                   r'[^"]*">.*?alt="([^"]+)"', re.S)

# Slug DIAMS -> nom exact du membre (vérifié à la main).
ALIASES = {"h-et-m": "H&M"}
GENERIC = {"group", "groupe", "holding", "holdings", "international", "company", "corporation"}


def parse_members(page: str) -> dict[str, str]:
    """Nom du membre -> fiche du membre sur le site du programme."""
    out: dict[str, str] = {}
    for url, alt in _ITEM.findall(page):
        out.setdefault(htmllib.unescape(alt).strip(), url)
    return out


def match(entity: dict, members: dict[str, str], by_norm: dict[str, list[str]]) -> str | None:
    if entity["slug"] in ALIASES:
        return ALIASES[entity["slug"]] if ALIASES[entity["slug"]] in members else None
    found = set()
    for k in ("display_name", "legal_name"):
        key = normalize_name(entity.get(k) or "")
        if len(key) < 3 or key in GENERIC:
            continue
        found.update(by_norm.get(key, []))
    return found.pop() if len(found) == 1 else None


def build_row(slug: str, name: str, url: str, today: str) -> EvidenceRow:
    return EvidenceRow(
        entity_slug=slug, indicator_code="ANI_FUR_FREE", source_code="FUR_FREE", nature="result",
        observed_on=today, value_type="boolean", value_boolean=True, normalized_value=1.0,
        confidence=0.85, source_url=url,
        excerpt=(f"Fur Free Retailer (Fur Free Alliance), liste des membres consultée le "
                 f"{today[8:10]}/{today[5:7]}/{today[:4]} : « {name} » — engagement vérifié à ne vendre "
                 f"aucune fourrure animale."),
        reviewer="import_fur_free",
    )


def _rest(c: httpx.Client, method: str, table: str, **kw) -> httpx.Response:
    r = c.request(method, f"{config.SUPABASE_URL}/rest/v1/{table}",
                  headers={**supabase_client._headers(), **kw.pop("headers", {})}, **kw)
    r.raise_for_status()
    return r


def main() -> None:
    ap = argparse.ArgumentParser(description="Fur Free Retailer : marques membres.")
    ap.add_argument("--file", help="page d'accueil déjà téléchargée (sinon téléchargée)")
    ap.add_argument("--apply", action="store_true", help="écrit en base (sinon dry-run)")
    args = ap.parse_args()
    config.require_supabase()
    today = dt.date.today().isoformat()
    with httpx.Client(timeout=120, follow_redirects=True) as c:
        if args.file:
            page = open(args.file, encoding="utf-8").read()
        else:
            r = c.get(LIST_URL, headers={"User-Agent": "Mozilla/5.0 (compatible; DIAMS)"})
            r.raise_for_status()
            page = r.text
        members = parse_members(page)
        print(f"{len(members)} membres du programme")
        if len(members) < 300:
            raise SystemExit("Liste incomplète : rien n'est écrit.")
        by_norm: dict[str, list[str]] = {}
        for n in members:
            by_norm.setdefault(normalize_name(n), []).append(n)
        ents = supabase_client.get_all(c, "entities", {"select": "slug,legal_name,display_name"})
        rows = []
        for e in ents:
            name = match(e, members, by_norm)
            if name:
                rows.append(build_row(e["slug"], name, members[name], today))
                print(f"  ✔ {e['slug']:<18} ({name})")
        ind = _rest(c, "GET", "indicators", params={"select": "id", "code": "eq.ANI_FUR_FREE"}).json()[0]["id"]
        old = _rest(c, "GET", "evidence", params={
            "select": "id", "indicator_id": f"eq.{ind}",
            "reviewer": "eq.curation-v1", "review_status": "eq.approved"}).json()
        print(f"{len(rows)} membres suivis, {len(old)} ligne(s) curation-v1 à retirer")
        if not args.apply:
            print("(dry-run : rien n'a été écrit. Relancer avec --apply.)")
            return
        print(insert_evidence(rows, c))
        if old:
            _rest(c, "PATCH", "evidence", params={"id": f"in.({','.join(o['id'] for o in old)})"},
                  headers={"Prefer": "return=minimal"},
                  json={"review_status": "rejected", "reviewer": "remplace:import_fur_free"})
            print(f"{len(old)} ligne(s) curation-v1 retirées")


if __name__ == "__main__":
    main()
