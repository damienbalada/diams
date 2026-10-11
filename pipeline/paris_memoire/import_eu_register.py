"""Registre de transparence de l'UE — inscription et budget de lobbying des groupes suivis.

Lit l'export ouvert complet (connectors/eu_register.py) et écrit, pour chaque
groupe rapproché :
  * GEO_LOBBYING_TRANSP : inscrit au registre (1,0) ;
  * GEO_LOBBYING_SPEND  : coûts de représentation déclarés pour le dernier
    exercice clos (milieu de la fourchette, en euros) — donnée de contexte,
    affichée mais jamais notée (direction `contextual`).

Rapprochement : nom exact (normalisé) de l'inscrit, catégorie « entreprises »,
ou table explicite ci-dessous quand le groupe s'inscrit sous le nom de son
entité européenne. Ambigu (plusieurs entités d'un même groupe inscrites
séparément) : on s'abstient.

Les lignes saisies à la main avant le connecteur (`curation-v1`, sources
EU_TRANSPARENCY et PRESS) sur ces deux indicateurs sont retirées
(`remplace:import_eu_register`).

Usage :
    python -m paris_memoire.import_eu_register [--file export.xml] [--apply]
"""
from __future__ import annotations

import argparse

import httpx

from . import config, supabase_client
from .connectors import eu_register as eu
from .load import EvidenceRow, insert_evidence
from .normalize.names import normalize_name

# Slug DIAMS -> nom exact de l'inscrit : entité européenne désignée du groupe (vérifiée).
ALIASES = {
    "volkswagen": "Volkswagen Aktiengesellschaft",
    "bmw": "Bayerische Motoren Werke Aktiengesellschaft",
    "carrefour": "Groupe Carrefour",
    "shein": "SHEIN Group",
    "shell": "Shell Companies",
    "schwarz-gruppe": "Schwarz Corporate Affairs International GmbH",
    "google": "Google Ireland Limited and its affiliates",
    "meta": "Meta Platforms Ireland Limited and its various subsidiaries",
    "amazon": "Amazon Europe Core SARL",
    "netflix": "Netflix International B.V.",
    "samsung": "Samsung Electronics Europe",
    "toyota": "TOYOTA MOTOR EUROPE",
    "mcdonalds": "McDonald’s Global Franchising Limited",
    "starbucks": "STARBUCKS EMEA LTD",
    "tesla": "Tesla Motors Netherlands B.V.",
    "colgate-palmolive": "Colgate-Palmolive Europe Sarl",
    "richemont": "Richemont International SA",
    "mondelez": "Mondelez Europe GmbH",
    "fast-retailing": "UNIQLO EUROPE LTD",
}
# Groupes inscrits sous plusieurs entités distinctes ou entité incertaine : on s'abstient.
SKIP = {"sony", "ikea", "credit-mutuel-arkea", "credit-mutuel-alliance-federale"}
GENERIC = {"group", "groupe", "holding", "holdings", "international", "company", "corporation"}


def fr_money(x: float) -> str:
    return f"{x:,.0f}".replace(",", " ") + " €"


def match(slug: str, names: list[str], by_name: dict[str, list[eu.Registrant]],
          by_norm: dict[str, list[eu.Registrant]]) -> eu.Registrant | None:
    if slug in SKIP:
        return None
    if slug in ALIASES:
        hits = by_name.get(ALIASES[slug], [])
        return hits[0] if len(hits) == 1 else None
    found: dict[str, eu.Registrant] = {}
    for n in names:
        key = normalize_name(n)
        if len(key) < 3 or key in GENERIC:
            continue
        for r in by_norm.get(key, []):
            found[r.code] = r
    return next(iter(found.values())) if len(found) == 1 else None


def rows_for(slug: str, r: eu.Registrant, export_date: str) -> list[EvidenceRow]:
    url = f"https://transparency-register.europa.eu/searchregister-or-update/organisation-detail_en?id={r.code}"
    head = (f"Registre de transparence de l'UE (export du {export_date[8:10]}/{export_date[5:7]}/{export_date[:4]}) : "
            f"« {r.name} », n° {r.code}, catégorie « entreprises et groupes »"
            + (f", fiche mise à jour le {r.last_update[8:10]}/{r.last_update[5:7]}/{r.last_update[:4]}" if r.last_update else ""))
    rows = [EvidenceRow(
        entity_slug=slug, indicator_code="GEO_LOBBYING_TRANSP", source_code="EU_TRANSPARENCY",
        nature="result", observed_on=export_date, value_type="boolean", value_boolean=True,
        normalized_value=1.0, confidence=0.9, source_url=url, excerpt=head + ".",
        reviewer="import_eu_register",
    )]
    if r.cost_mid is not None:
        period = f"exercice {r.year_start[:4]}" if r.year_start else "dernier exercice clos"
        span = fr_money(r.cost_min) if r.cost_min == r.cost_max else f"{fr_money(r.cost_min)} à {fr_money(r.cost_max)}"
        fte = f", {str(r.fte).rstrip('0').rstrip('.').replace('.', ',')} équivalents temps plein" if r.fte else ""
        rows.append(EvidenceRow(
            entity_slug=slug, indicator_code="GEO_LOBBYING_SPEND", source_code="EU_TRANSPARENCY",
            nature="result", observed_on=export_date, value_type="numeric", value_numeric=r.cost_mid,
            confidence=0.9, source_url=url,
            excerpt=f"{head} : coûts de représentation d'intérêts déclarés ({period}) : {span}{fte}.",
            reviewer="import_eu_register",
        ))
    return rows


def _rest(c: httpx.Client, method: str, table: str, **kw) -> httpx.Response:
    r = c.request(method, f"{config.SUPABASE_URL}/rest/v1/{table}",
                  headers={**supabase_client._headers(), **kw.pop("headers", {})}, **kw)
    r.raise_for_status()
    return r


def main() -> None:
    ap = argparse.ArgumentParser(description="Registre de transparence UE : inscription et budget de lobbying.")
    ap.add_argument("--file", help="export XML déjà téléchargé (sinon téléchargé)")
    ap.add_argument("--apply", action="store_true", help="écrit en base (sinon dry-run)")
    args = ap.parse_args()
    config.require_supabase()
    with httpx.Client(timeout=600, follow_redirects=True) as c:
        if args.file:
            raw = open(args.file, "rb").read()
        else:
            resp = c.get(eu.EXPORT_URL, headers={"User-Agent": "Mozilla/5.0 (DIAMS)"})
            resp.raise_for_status()
            raw = resp.content
        export_date, regs = eu.parse_export(raw)
        print(f"Export du {export_date} : {len(regs)} entreprises inscrites")
        if not export_date or len(regs) < 3000:
            raise SystemExit("Export incomplet : rien n'est écrit.")
        by_name: dict[str, list[eu.Registrant]] = {}
        by_norm: dict[str, list[eu.Registrant]] = {}
        for r in regs:
            by_name.setdefault(r.name, []).append(r)
            by_norm.setdefault(normalize_name(r.name), []).append(r)
        ents = _rest(c, "GET", "entities", params={"select": "slug,legal_name,display_name,parent_id"}).json()
        rows: list[EvidenceRow] = []
        for g in (e for e in ents if not e.get("parent_id")):
            r = match(g["slug"], [g[k] for k in ("display_name", "legal_name") if g.get(k)], by_name, by_norm)
            if r:
                rows += rows_for(g["slug"], r, export_date)
                cost = f"{fr_money(r.cost_mid)}" if r.cost_mid is not None else "coûts non déclarés"
                print(f"  ✔ {g['slug']:<18} {r.code:<18} {cost:<14} ({r.name})")
        print(f"{len(rows)} preuves à écrire")
        old = []
        for code in ("GEO_LOBBYING_TRANSP", "GEO_LOBBYING_SPEND"):
            ind = _rest(c, "GET", "indicators", params={"select": "id", "code": f"eq.{code}"}).json()[0]["id"]
            for src in ("EU_TRANSPARENCY", "PRESS"):
                sid = _rest(c, "GET", "sources", params={"select": "id", "code": f"eq.{src}"}).json()[0]["id"]
                old += _rest(c, "GET", "evidence", params={
                    "select": "id", "indicator_id": f"eq.{ind}", "source_id": f"eq.{sid}",
                    "reviewer": "eq.curation-v1", "review_status": "eq.approved"}).json()
        print(f"{len(old)} ligne(s) curation-v1 à retirer")
        if not args.apply:
            print("(dry-run : rien n'a été écrit. Relancer avec --apply.)")
            return
        print(insert_evidence(rows, c))
        if old:
            _rest(c, "PATCH", "evidence", params={"id": f"in.({','.join(o['id'] for o in old)})"},
                  headers={"Prefer": "return=minimal"},
                  json={"review_status": "rejected", "reviewer": "remplace:import_eu_register"})
            print(f"{len(old)} ligne(s) curation-v1 retirées")


if __name__ == "__main__":
    main()
