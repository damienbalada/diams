"""Portefeuilles de marques : rattachement marque → groupe, preuve citée à l'appui.

Une marque n'entre dans DIAMS (ou n'y est rattachée) que si son nom figure, mot pour
mot, dans le document officiel de son propriétaire : rapport annuel, document
d'enregistrement universel, rapport 10-K, ou page « nos marques » du groupe.
Le contrôle est DÉTERMINISTE :

  1. la citation figure dans le document (espaces de mise en page ignorés) ;
  2. le nom de la marque figure dans la citation (casse et accents ignorés,
     mot entier) ;
  3. le groupe existe dans DIAMS et n'est pas lui-même une marque ;
  4. une marque déjà rattachée à un AUTRE groupe n'est jamais déplacée ici
     (conflit signalé, à trancher par une migration motivée).

Écritures : création de la marque (entities, is_brand) si elle n'existe pas, et
preuve d'appartenance (entity_ownership_sources). Rapport légal → reviewer
`auto:verify_ownership` ; page web de l'entreprise → délégation de l'éditeur.

Usage :
    python -m paris_memoire.import_brand_portfolio --file curated/marques_X.csv           # contrôle
    python -m paris_memoire.import_brand_portfolio --file curated/marques_X.csv --apply   # écriture
CSV : brand_slug, brand_name, group_slug, sector_code, source_kind (legal|website),
      source_url, doc, quote, observed_on, animal_free (vide|true)
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from typing import Any

import httpx

from . import config
from .verify_curated import DELEGATED_REVIEWER, _canon, document_text

REVIEWER_LEGAL = "auto:verify_ownership"


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.replace("’", "'"))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().lower()


def name_in_quote(name: str, quote: str) -> bool:
    """Le nom de la marque figure dans la citation, en mot entier (casse et accents
    ignorés ; « & » et « and », tirets et espaces équivalents)."""
    n, q = _fold(name), _fold(quote)
    variants = {n, n.replace("&", "and"), n.replace("-", " "), n.replace(" ", "-"), n.replace("'", "’")}
    return any(re.search(rf"(?<![\w]){re.escape(v)}(?![\w])", q) for v in variants if v)


def quote_in_document(quote: str, text: str) -> bool:
    q, t = _canon(quote), _canon(text)
    return q in t or re.sub(r"\s", "", q) in re.sub(r"\s", "", t)


def _h() -> dict[str, str]:
    return {"apikey": config.SUPABASE_SERVICE_ROLE_KEY, "Authorization": f"Bearer {config.SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json"}


def check_rows(rows: list[dict[str, str]], ents: dict[str, dict[str, Any]], sectors: dict[str, str],
               fetch) -> list[tuple[dict[str, str], str, list[str]]]:
    """Contrôle chaque ligne ; renvoie (ligne, statut, détails). Statuts : OK, ÉCART,
    CONFLIT (marque rattachée à un autre groupe), DÉJÀ (déjà rattachée et sourcée)."""
    out = []
    for r in rows:
        det: list[str] = []
        g = ents.get(r["group_slug"])
        if not g or g["is_brand"]:
            out.append((r, "ÉCART", [f"groupe « {r['group_slug']} » absent ou marque"]))
            continue
        if r["sector_code"] not in sectors:
            out.append((r, "ÉCART", [f"secteur « {r['sector_code']} » inconnu"]))
            continue
        text = fetch(r["source_url"])
        found = text is not None and quote_in_document(r["quote"], text)
        det.append(f"citation retrouvée dans le document {'✓' if found else '✗'}")
        named = name_in_quote(r["brand_name"], r["quote"])
        det.append(f"marque « {r['brand_name']} » nommée dans la citation {'✓' if named else '✗'}")
        existing = ents.get(r["brand_slug"])
        if existing and existing["parent_id"] and existing["parent_id"] != g["id"]:
            out.append((r, "CONFLIT", det + ["marque déjà rattachée à un autre groupe : migration motivée requise"]))
            continue
        if existing and not existing["is_brand"]:
            out.append((r, "CONFLIT", det + ["l'identifiant désigne un groupe, pas une marque"]))
            continue
        out.append((r, "OK" if found and named else "ÉCART", det))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Rattachement marque → groupe, preuve citée.")
    ap.add_argument("--file", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    config.require_supabase()
    rows = list(csv.DictReader(open(args.file, encoding="utf-8")))
    with httpx.Client(timeout=120) as db, httpx.Client(timeout=300) as web:
        ents = {e["slug"]: e for e in db.get(f"{config.SUPABASE_URL}/rest/v1/entities", headers=_h(),
                                             params={"select": "id,slug,is_brand,parent_id,country"}).json()}
        sectors = {s["code"]: s["id"] for s in db.get(f"{config.SUPABASE_URL}/rest/v1/sectors", headers=_h(),
                                                      params={"select": "id,code"}).json()}
        cache: dict[str, str | None] = {}

        def fetch(url: str) -> str | None:
            if url not in cache:
                try:
                    cache[url] = document_text(url, web)
                except Exception as e:  # noqa: BLE001
                    print(f"  ! document illisible ({url}) : {e}")
                    cache[url] = None
            return cache[url]

        results = check_rows(rows, ents, sectors, fetch)
        stats: dict[str, int] = {}
        for r, status, det in results:
            stats[status] = stats.get(status, 0) + 1
            if status != "OK":
                print(f"[{status}] {r['brand_name']} → {r['group_slug']}")
                for d in det:
                    print(f"    {d}")
        print(f"\nBilan : " + ", ".join(f"{k} {v}" for k, v in sorted(stats.items())))
        if not args.apply:
            print("(contrôle seulement : --apply écrit les seules lignes OK)")
            return
        created = linked = 0
        for r, status, _ in results:
            if status != "OK":
                continue
            g = ents[r["group_slug"]]
            b = ents.get(r["brand_slug"])
            if b is None:
                resp = db.post(f"{config.SUPABASE_URL}/rest/v1/entities",
                               headers={**_h(), "Prefer": "return=representation"},
                               json={"slug": r["brand_slug"], "legal_name": r["brand_name"], "display_name": r["brand_name"],
                                     "parent_id": g["id"], "ownership_pct": 100, "country": g.get("country"),
                                     "sector_id": sectors[r["sector_code"]], "is_brand": True,
                                     "animal_free": (r.get("animal_free") or "").strip().lower() == "true"})
                resp.raise_for_status()
                b = resp.json()[0]
                ents[r["brand_slug"]] = b
                created += 1
            elif not b["parent_id"]:
                db.patch(f"{config.SUPABASE_URL}/rest/v1/entities", params={"id": f"eq.{b['id']}"},
                         headers={**_h(), "Prefer": "return=minimal"},
                         json={"parent_id": g["id"], "ownership_pct": 100}).raise_for_status()
            reviewer = REVIEWER_LEGAL if r["source_kind"] == "legal" else DELEGATED_REVIEWER
            resp = db.post(f"{config.SUPABASE_URL}/rest/v1/entity_ownership_sources",
                           params={"on_conflict": "entity_id,owner_id,source_url"},
                           headers={**_h(), "Prefer": "resolution=ignore-duplicates,return=minimal"},
                           json={"entity_id": b["id"], "owner_id": g["id"], "source_url": r["source_url"],
                                 "excerpt": f"{r['doc']} : « {r['quote']} »", "observed_on": r["observed_on"],
                                 "reviewer": reviewer})
            resp.raise_for_status()
            linked += 1
        print(f"Marques créées : {created} · preuves d'appartenance écrites : {linked}")


if __name__ == "__main__":
    main()
