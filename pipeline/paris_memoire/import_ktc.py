"""KnowTheChain (travail forcé dans la chaîne d'approvisionnement) — connecteur.

Lit les données publiées des trois comparaisons KnowTheChain (alimentation &
boissons, habillement & chaussures, technologies), retient la dernière édition de
chaque entreprise et l'attache au GROUPE correspondant (KnowTheChain évalue des
sociétés, pas des marques ; une marque reprend la donnée de son groupe).

Rapprochement des noms : table explicite ci-dessous, puis correspondance nette
(normalize.names) sur les groupes uniquement. En cas de doute, on saute.

Les lignes compilées à la main avant le connecteur (`curation-v1`) sur cet
indicateur sont retirées (`rejected`, reviewer `remplace:import_ktc`) : plusieurs
contredisaient la donnée publiée (Coca-Cola « 58/100 » pour 29 publié).

Usage :
    python -m paris_memoire.import_ktc            # dry-run
    python -m paris_memoire.import_ktc --apply
"""
from __future__ import annotations

import argparse

import httpx

from . import config, supabase_client
from .connectors import benchmarks as bm
from .load import EvidenceRow, insert_evidence
from .normalize.names import is_strong_match

# Nom KnowTheChain -> slug (rapprochements non triviaux, vérifiés à la main).
ALIASES = {
    "Amazon.com": "amazon",
    "Hennes & Mauritz (H&M)": "hm-group",
    "LVMH Moët Hennessy – Louis Vuitton": "lvmh",
    "Mondelēz International": "mondelez",
    "Kellanova (formerly Kellogg)": "kellanova",
    "Samsung Electronics": "samsung",
    "Nestlé": "nestle",
    "Hermès": "hermes",
    "Coca-Cola": "coca-cola",
}


def fetch_all(client: httpx.Client) -> list[bm.KtcScore]:
    out: list[bm.KtcScore] = []
    for code, (vis, _label, _page) in bm.KTC_BENCHMARKS.items():
        r = client.get(bm.flourish_url(vis), headers={"User-Agent": "Mozilla/5.0 (DIAMS)"})
        r.raise_for_status()
        out.extend(bm.parse_ktc_flourish(r.text, code))
    return out


def match_group(name: str, groups: list[dict]) -> dict | None:
    by_slug = {g["slug"]: g for g in groups}
    if name in ALIASES:
        return by_slug.get(ALIASES[name])
    for g in groups:
        for key in ("display_name", "legal_name"):
            if g.get(key) and is_strong_match(name, g[key]):
                return g
    return None


def build_row(slug: str, s: bm.KtcScore) -> EvidenceRow:
    _vis, label, page = bm.KTC_BENCHMARKS[s.benchmark]
    rank = f", rang {s.rank} sur {s.size}" if s.rank and s.size else ""
    return EvidenceRow(
        entity_slug=slug, indicator_code="SUP_KNOWTHECHAIN", source_code="KNOWTHECHAIN",
        nature="result", observed_on=f"{s.published}-01-01", value_type="numeric",
        value_numeric=s.score, value_text=f"{s.score:g}/100",
        normalized_value=round(bm.norm_score(s.score), 4), confidence=0.85,
        source_url=page,
        excerpt=(f"KnowTheChain, benchmark {label} (édition {s.edition}) : « {s.company} » "
                 f"{s.score:g}/100{rank} — prévention du travail forcé dans la chaîne "
                 f"d'approvisionnement."),
        reviewer="import_ktc",
    )


def _rest(c: httpx.Client, method: str, table: str, **kw) -> httpx.Response:
    r = c.request(method, f"{config.SUPABASE_URL}/rest/v1/{table}",
                  headers={**supabase_client._headers(), **kw.pop("headers", {})}, **kw)
    r.raise_for_status()
    return r


def main() -> None:
    ap = argparse.ArgumentParser(description="KnowTheChain : dernière édition publiée par groupe.")
    ap.add_argument("--apply", action="store_true", help="écrit en base (sinon dry-run)")
    args = ap.parse_args()
    config.require_supabase()
    with httpx.Client(timeout=60) as c:
        scores = fetch_all(c)
        latest = bm.latest_ktc(scores)
        print(f"{len(scores)} lignes KnowTheChain, {len(latest)} entreprises (dernière édition)")
        ents = supabase_client.get_all(c, "entities", {"select": "id,slug,legal_name,display_name,parent_id"})
        groups = [e for e in ents if not e.get("parent_id")]
        rows: list[EvidenceRow] = []
        for name, s in sorted(latest.items()):
            g = match_group(name, groups)
            if g:
                rows.append(build_row(g["slug"], s))
                print(f"  ✔ {g['slug']:<16} {s.score:>4g}/100  {s.benchmark} {s.edition}  ({name})")
        print(f"{len(rows)} groupes suivis évalués par KnowTheChain")
        ind = _rest(c, "GET", "indicators", params={"select": "id", "code": "eq.SUP_KNOWTHECHAIN"}).json()[0]["id"]
        old = _rest(c, "GET", "evidence", params={
            "select": "id,value_numeric,excerpt", "indicator_id": f"eq.{ind}",
            "reviewer": "eq.curation-v1", "review_status": "eq.approved"}).json()
        print(f"{len(old)} ligne(s) curation-v1 à retirer")
        if not args.apply:
            print("(dry-run : rien n'a été écrit. Relancer avec --apply.)")
            return
        print(insert_evidence(rows, c))
        # Une ligne existante à la même date (clé d'unicité) bloque l'insertion :
        # on la remplace par la donnée publiée, plutôt que de la laisser retirée.
        by_slug = {e["slug"]: e["id"] for e in ents}
        existing = _rest(c, "GET", "evidence", params={
            "select": "id,entity_id,observed_on,reviewer", "indicator_id": f"eq.{ind}"}).json()
        key = {(x["entity_id"], x["observed_on"]): x for x in existing}
        for row in rows:
            x = key.get((by_slug[row.entity_slug], row.observed_on))
            if x and x["reviewer"] != "auto:import_ktc":
                _rest(c, "PATCH", "evidence", params={"id": f"eq.{x['id']}"},
                      headers={"Prefer": "return=minimal"},
                      json={"value_numeric": row.value_numeric, "value_text": row.value_text,
                            "normalized_value": row.normalized_value, "confidence": row.confidence,
                            "source_url": row.source_url, "excerpt": row.excerpt,
                            "review_status": "approved", "reviewer": "auto:import_ktc"})
                old = [o for o in old if o["id"] != x["id"]]
                print(f"  ↻ {row.entity_slug} : ligne du {row.observed_on} remplacée par la donnée publiée")
        if old:
            _rest(c, "PATCH", "evidence", params={"id": f"in.({','.join(o['id'] for o in old)})"},
                  headers={"Prefer": "return=minimal"},
                  json={"review_status": "rejected", "reviewer": "remplace:import_ktc"})
            print(f"{len(old)} ligne(s) curation-v1 retirées")


if __name__ == "__main__":
    main()
