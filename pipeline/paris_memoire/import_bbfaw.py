"""BBFAW (bien-être des animaux d'élevage) — connecteur sur le rapport annuel.

Télécharge le rapport, lit la figure des tiers (liste complète des entreprises
évaluées, voir connectors/bbfaw.py), contrôle la lecture (tableau des mouvements
de tier et effectifs par colonne : aucun écart toléré) et attache chaque tier au
GROUPE suivi correspondant. Une entreprise absente de la liste n'a pas été
évaluée par le BBFAW.

Les lignes compilées à la main avant le connecteur (`curation-v1`) sur cet
indicateur sont retirées (`rejected`, reviewer `remplace:import_bbfaw`) : elles
dataient de 2023-2024 et l'une d'elles (Coca-Cola, absente du BBFAW) décrivait
en réalité une controverse.

Usage :
    python -m paris_memoire.import_bbfaw            # dry-run
    python -m paris_memoire.import_bbfaw --apply
"""
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import httpx

from . import config, supabase_client
from .connectors import bbfaw
from .connectors.benchmarks import norm_bbfaw_tier
from .load import EvidenceRow, insert_evidence
from .normalize.names import is_strong_match

# Nom BBFAW -> slug (rapprochements non triviaux, vérifiés à la main).
ALIASES = {
    "Groupe Danone SA": "danone",
    "McDonald’s Corporation": "mcdonalds",
    "Restaurant Brands International": "rbi",
    "Yum! Brands Inc": "yum-brands",
    "Starbucks Corporation": "starbucks",
    "Nestlé SA": "nestle",
    "Kraft Heinz Company": "kraft-heinz",
    "Unilever NV": "unilever",
    "Mars Inc": "mars",
    "Mondelēz International": "mondelez",
    "Ferrero Group": "ferrero",
    "Barilla SpA": "barilla",
    "Groupe Lactalis": "lactalis",
    "Carrefour SA": "carrefour",
    "Schwarz Gruppe": "schwarz-gruppe",
    "IKEA (Inter IKEA Group)": "ikea",
}
# Noms à ne jamais rapprocher automatiquement (homonymes partiels).
NEVER = {"Yum China Holdings", "Coop Italia", "Metro Inc", "Amazon/Whole Foods Market"}

TIER_LABEL = {
    1: "leadership", 2: "intégré à la stratégie", 3: "démarche établie, à mettre en œuvre",
    4: "mise en œuvre en cours", 5: "à l'agenda, peu de preuves de mise en œuvre",
    6: "aucune preuve à l'agenda",
}


def match_group(name: str, groups: list[dict]) -> dict | None:
    if name in NEVER:
        return None
    by_slug = {g["slug"]: g for g in groups}
    if name in ALIASES:
        return by_slug.get(ALIASES[name])
    for g in groups:
        for key in ("display_name", "legal_name"):
            if g.get(key) and is_strong_match(name, g[key]):
                return g
    return None


def build_row(slug: str, e: bbfaw.BbfawEntry) -> EvidenceRow:
    return EvidenceRow(
        entity_slug=slug, indicator_code="ANI_BBFAW_TIER", source_code="BBFAW",
        nature="result", observed_on=f"{bbfaw.REPORT_YEAR}-12-31", value_type="ordinal",
        value_numeric=e.tier, value_text=f"Tier {e.tier}",
        normalized_value=norm_bbfaw_tier(e.tier), confidence=0.85,
        source_url=bbfaw.REPORT_URL,
        excerpt=(f"BBFAW {bbfaw.REPORT_YEAR} (bien-être des animaux d'élevage, 149 entreprises "
                 f"évaluées) : « {e.company} » Tier {e.tier} sur 6 — {TIER_LABEL[e.tier]}."),
        reviewer="import_bbfaw",
    )


def _rest(c: httpx.Client, method: str, table: str, **kw) -> httpx.Response:
    r = c.request(method, f"{config.SUPABASE_URL}/rest/v1/{table}",
                  headers={**supabase_client._headers(), **kw.pop("headers", {})}, **kw)
    r.raise_for_status()
    return r


def main() -> None:
    ap = argparse.ArgumentParser(description="BBFAW : tier de chaque groupe suivi (rapport annuel).")
    ap.add_argument("--apply", action="store_true", help="écrit en base (sinon dry-run)")
    ap.add_argument("--pdf", help="rapport déjà téléchargé (sinon téléchargé)")
    args = ap.parse_args()
    config.require_supabase()
    with httpx.Client(timeout=120, follow_redirects=True) as c:
        path = args.pdf
        if not path:
            tmp = Path(tempfile.mkdtemp()) / "bbfaw.pdf"
            r = c.get(bbfaw.REPORT_URL, headers={"User-Agent": "Mozilla/5.0 (DIAMS)"})
            r.raise_for_status()
            tmp.write_bytes(r.content)
            path = str(tmp)
        entries, moves, counts = bbfaw.read_report(path)
        issues = bbfaw.check(entries, moves, counts)
        print(f"{len(entries)} entreprises lues, effectifs {counts}, {len(moves)} mouvements contrôlés")
        if issues:
            raise SystemExit("Lecture non conforme, rien n'est écrit :\n  " + "\n  ".join(issues))
        ents = _rest(c, "GET", "entities", params={"select": "id,slug,legal_name,display_name,parent_id"}).json()
        groups = [e for e in ents if not e.get("parent_id")]
        rows = []
        for e in entries:
            g = match_group(e.company, groups)
            if g:
                rows.append(build_row(g["slug"], e))
                print(f"  ✔ {g['slug']:<16} Tier {e.tier}  ({e.company})")
        print(f"{len(rows)} groupes suivis évalués par le BBFAW")
        ind = _rest(c, "GET", "indicators", params={"select": "id", "code": "eq.ANI_BBFAW_TIER"}).json()[0]["id"]
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
                  json={"review_status": "rejected", "reviewer": "remplace:import_bbfaw"})
            print(f"{len(old)} ligne(s) curation-v1 retirées")


if __name__ == "__main__":
    main()
