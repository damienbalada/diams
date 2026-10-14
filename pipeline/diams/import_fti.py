"""Fashion Transparency Index (Fashion Revolution) — édition 2023, liste complète.

Le dernier indice consacré à la transparence de la chaîne d'approvisionnement
(250 marques ; l'édition 2025 porte sur le climat et l'énergie) est publié en
données ouvertes par Wikirate, partenaire de Fashion Revolution. Le score y est
ramené sur 10 (7,11 = 71,1 % des points). On l'écrit sur SUP_FTI_SCORE, au
niveau de l'entité nommée par l'indice (marque, ou groupe quand l'indice note
le groupe), source FTI (ONG auditée) : publication automatique.

Liste complète : une marque absente n'a pas été évaluée (indicateur
complémentaire). Les lignes saisies à la main avant le connecteur
(`curation-v1`) sont retirées (`remplace:import_fti`).

Usage :
    python -m diams.import_fti [--file reponses.json] [--apply]
"""
from __future__ import annotations

import argparse
import json

import httpx

from . import config, supabase_client
from .load import EvidenceRow, insert_evidence
from .normalize.names import normalize_name

API_URL = ("https://wikirate.org/Fashion_Revolution+Fashion_Transparency_Index+Answer.json"
           "?filter%5Byear%5D=2023&limit=1000")
YEAR = 2023
REPORT_URL = "https://www.fashionrevolution.org/about/transparency/"

# Slug DIAMS -> nom exact dans l'indice (vérifié à la main).
ALIASES = {
    "h-et-m": "H&M",
    "dior": "Christian Dior",
    "louis-vuitton": "Louis Vuitton Malletier SA (LVMH)",
    "decathlon": "Decathlon Group",
}
GENERIC = {"group", "groupe", "holding", "holdings", "international", "company", "corporation"}


def parse_answers(payload: dict) -> dict[str, float]:
    """Nom de la marque -> score sur 10 (édition YEAR seulement)."""
    return {i["company"]: float(i["value"]) for i in payload.get("items", [])
            if i.get("year") == YEAR and i.get("value") not in (None, "")}


def match(entity: dict, scores: dict[str, float], by_norm: dict[str, list[str]]) -> str | None:
    if entity["slug"] in ALIASES:
        name = ALIASES[entity["slug"]]
        return name if name in scores else None
    found = set()
    for k in ("display_name", "legal_name"):
        key = normalize_name(entity.get(k) or "")
        # Nom trop court une fois normalisé (« H&M » → « ») : jamais de rapprochement.
        if len(key) < 3 or key in GENERIC:
            continue
        found.update(by_norm.get(key, []))
    return found.pop() if len(found) == 1 else None


def build_row(slug: str, name: str, score10: float) -> EvidenceRow:
    pct = round(score10 * 10, 1)
    return EvidenceRow(
        entity_slug=slug, indicator_code="SUP_FTI_SCORE", source_code="FTI", nature="result",
        observed_on=f"{YEAR}-07-13", value_type="numeric", value_numeric=pct,
        normalized_value=round(score10 / 10, 4), confidence=0.85, source_url=REPORT_URL,
        excerpt=(f"Fashion Transparency Index {YEAR} (Fashion Revolution, 250 grandes marques ; données "
                 f"ouvertes Wikirate) : « {name} » — {str(pct).replace('.', ',')} % des points sur la "
                 f"transparence de la chaîne d'approvisionnement."),
        reviewer="import_fti",
    )


def _rest(c: httpx.Client, method: str, table: str, **kw) -> httpx.Response:
    r = c.request(method, f"{config.SUPABASE_URL}/rest/v1/{table}",
                  headers={**supabase_client._headers(), **kw.pop("headers", {})}, **kw)
    r.raise_for_status()
    return r


def main() -> None:
    ap = argparse.ArgumentParser(description="Fashion Transparency Index 2023 : score des marques suivies.")
    ap.add_argument("--file", help="réponses Wikirate déjà téléchargées (sinon téléchargées)")
    ap.add_argument("--apply", action="store_true", help="écrit en base (sinon dry-run)")
    args = ap.parse_args()
    config.require_supabase()
    with httpx.Client(timeout=120) as c:
        if args.file:
            payload = json.load(open(args.file, encoding="utf-8"))
        else:
            r = c.get(API_URL, headers={"User-Agent": "Mozilla/5.0 (compatible; DIAMS)"})
            r.raise_for_status()
            payload = r.json()
        scores = parse_answers(payload)
        print(f"{len(scores)} marques notées dans le FTI {YEAR}")
        if len(scores) < 200:
            raise SystemExit("Liste incomplète : rien n'est écrit.")
        by_norm: dict[str, list[str]] = {}
        for n in scores:
            by_norm.setdefault(normalize_name(n), []).append(n)
        ents = supabase_client.get_all(c, "entities", {"select": "slug,legal_name,display_name"})
        rows = []
        for e in ents:
            name = match(e, scores, by_norm)
            if name:
                rows.append(build_row(e["slug"], name, scores[name]))
                print(f"  ✔ {e['slug']:<18} {scores[name] * 10:5.1f} %  ({name})")
        ind = _rest(c, "GET", "indicators", params={"select": "id", "code": "eq.SUP_FTI_SCORE"}).json()[0]["id"]
        old = _rest(c, "GET", "evidence", params={
            "select": "id", "indicator_id": f"eq.{ind}",
            "reviewer": "eq.curation-v1", "review_status": "eq.approved"}).json()
        print(f"{len(rows)} scores à écrire, {len(old)} ligne(s) curation-v1 à retirer")
        if not args.apply:
            print("(dry-run : rien n'a été écrit. Relancer avec --apply.)")
            return
        print(insert_evidence(rows, c))
        if old:
            _rest(c, "PATCH", "evidence", params={"id": f"in.({','.join(o['id'] for o in old)})"},
                  headers={"Prefer": "return=minimal"},
                  json={"review_status": "rejected", "reviewer": "remplace:import_fti"})
            print(f"{len(old)} ligne(s) curation-v1 retirées")


if __name__ == "__main__":
    main()
