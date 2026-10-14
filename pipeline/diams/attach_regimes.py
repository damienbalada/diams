"""Rattache des entités à des régimes d'obligation de publication (Règle 1).

Être soumis à un régime est un FAIT sourcé et daté (table `entity_regimes`) :
il rend obligatoires certains indicateurs, dont l'absence compte alors 0.

Deux voies :
  --egapro FICHIER   déterministe : toute entité dont le SIREN figure dans les
                     déclarations Égapro officielles est soumise à FR_EGAPRO
                     (obligation dès 50 salariés). Reviewer `auto:attach_regimes`.
  --file CSV         rattachements curés : entity_slug, regime_code, basis,
                     source_url, observed_on. Reviewer `ai:<modèle>` ; le CSV est
                     versionné dans pipeline/curated/ (piste d'audit).

Usage :
    python -m diams.attach_regimes --egapro egapro.csv [--apply]
    python -m diams.attach_regimes --file curated/regimes_banques.csv [--apply]
"""
from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from datetime import date

import httpx

from . import config, supabase_client
from .connectors import egapro

EGAPRO_SEARCH_URL = "https://egapro.travail.gouv.fr/index-egapro/recherche"


@dataclass
class RegimeLink:
    entity_slug: str
    regime_code: str
    basis: str
    source_url: str
    observed_on: str
    reviewer: str


def egapro_links(entities: list[dict], by_siren: dict[str, egapro.EgaproRecord], today: str) -> list[RegimeLink]:
    """Une entité déclarante est soumise à l'obligation Égapro (SIREN exact)."""
    out: list[RegimeLink] = []
    for e in entities:
        siren = str(e.get("siren") or "")
        rec = by_siren.get(siren) if siren else None
        # Déclaration récente exigée : une entreprise passée sous 50 salariés
        # (ou disparue) cesse de déclarer, l'obligation ne se présume pas.
        if rec is None or not rec.year.isdigit() or int(rec.year) < int(today[:4]) - 3:
            continue
        out.append(RegimeLink(
            entity_slug=e["slug"], regime_code="FR_EGAPRO",
            basis=f"SIREN {siren} présent dans les déclarations Égapro (index {rec.year}) : entreprise d'au moins 50 salariés",
            source_url=EGAPRO_SEARCH_URL, observed_on=today, reviewer="auto:attach_regimes",
        ))
    return out


def parse_file(path: str, reviewer: str) -> tuple[list[RegimeLink], list[str]]:
    links: list[RegimeLink] = []
    errors: list[str] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            g = {k: (row.get(k) or "").strip() for k in ("entity_slug", "regime_code", "basis", "source_url", "observed_on")}
            missing = [k for k, v in g.items() if not v]
            if missing:
                errors.append(f"ligne {i} : colonnes vides {missing}")
                continue
            if not re.match(r"^https?://\S+$", g["source_url"]):
                errors.append(f"ligne {i} : source_url invalide")
                continue
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", g["observed_on"]):
                errors.append(f"ligne {i} : observed_on doit être AAAA-MM-JJ")
                continue
            links.append(RegimeLink(reviewer=reviewer, **g))
    return links, errors


def upsert(links: list[RegimeLink]) -> int:
    config.require_supabase()
    h = {"apikey": config.SUPABASE_SERVICE_ROLE_KEY, "Authorization": f"Bearer {config.SUPABASE_SERVICE_ROLE_KEY}",
         "Content-Type": "application/json"}
    base = f"{config.SUPABASE_URL}/rest/v1"
    with httpx.Client(timeout=60) as c:
        # Toutes les entités, page par page : l'API n'en renvoie que 1 000 par appel (avant le
        # 15/10/2026, les rattachements au-delà échouaient en « références inconnues »).
        ents = {e["slug"]: e["id"] for e in supabase_client.get_all(c, "entities", {"select": "id,slug"}, headers=h)}
        regs = {r["code"]: r["id"] for r in c.get(f"{base}/disclosure_regimes", params={"select": "id,code"}, headers=h).json()}
        unknown = sorted({l.entity_slug for l in links if l.entity_slug not in ents} | {l.regime_code for l in links if l.regime_code not in regs})
        if unknown:
            raise SystemExit("Références inconnues : " + ", ".join(unknown))
        payload = [{"entity_id": ents[l.entity_slug], "regime_id": regs[l.regime_code], "basis": l.basis,
                    "source_url": l.source_url, "observed_on": l.observed_on, "reviewer": l.reviewer} for l in links]
        if not payload:
            return 0
        r = c.post(f"{base}/entity_regimes", params={"on_conflict": "entity_id,regime_id"},
                   headers={**h, "Prefer": "resolution=merge-duplicates,return=representation"}, json=payload)
        r.raise_for_status()
        return len(r.json())


def main() -> None:
    parser = argparse.ArgumentParser(description="Rattache des entités aux régimes d'obligation (Règle 1).")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--egapro", help="CSV Égapro officiel (voie déterministe)")
    src.add_argument("--file", help="CSV de rattachements curés")
    parser.add_argument("--reviewer", default="ai:claude-opus-5-5")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if args.egapro:
        by_siren = egapro.latest_by_siren(egapro.parse_csv(args.egapro))
        links = egapro_links(supabase_client.list_entities(), by_siren, date.today().isoformat())
    else:
        links, errors = parse_file(args.file, args.reviewer)
        for e in errors:
            print(f"✖ {e}")
        if errors:
            raise SystemExit(f"{len(errors)} ligne(s) invalide(s) : rien n'est écrit.")
    for l in links:
        print(f"• {l.entity_slug:32} → {l.regime_code:20} {l.basis[:70]}")
    print(f"\n{len(links)} rattachement(s)")
    if args.apply:
        print(f"Écrits : {upsert(links)}")
    else:
        print("(contrôle seulement : relancer avec --apply pour écrire)")


if __name__ == "__main__":
    main()
