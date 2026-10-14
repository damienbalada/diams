"""Exploitation animale lue dans l'activité principale officielle (code APE) d'une société.

Règle de l'éditeur (14/10/2026) : une société dont l'activité principale est de
transformer ou de commercialiser des produits animaux (viande, volaille, charcuterie,
poisson, lait, beurre, fromage) ou d'élever ou pêcher des animaux exploite des animaux ;
ses marques aussi, sauf celles déclarées sans intrant animal (`animal_free`).

Source : avis de situation au répertoire Sirene de l'Insee (PDF officiel du siège),
dont la ligne « Activité Principale Exercée (APE) » est relue mot pour mot ; le code est
d'abord repéré dans l'annuaire officiel des entreprises. Seules les entités qui n'ont
encore aucune preuve d'exploitation animale reçoivent une ligne.

Usage :
    python -m diams.import_ani_ape            # contrôle
    python -m diams.import_ani_ape --apply    # écrit (source réglementaire : publiée)
"""
from __future__ import annotations

import argparse
import re
import time
from datetime import date

import httpx

from . import config, supabase_client
from .load import EvidenceRow, insert_evidence
from .verify_curated import document_text

AVIS_URL = "https://api-avis-situation-sirene.insee.fr/identification/pdf/{siret}"
SEARCH_URL = "https://recherche-entreprises.api.gouv.fr/search"
REVIEWER = "auto:ani_ape"

# Codes APE (NAF rév. 2) dont l'activité est, par définition, l'exploitation d'animaux.
# Exclus à dessein : glaces et sorbets (10.52Z, des sorbets sont végétaux), commerce de
# gros de produits laitiers, œufs ET huiles (46.33Z, mélange), plats préparés (10.85Z).
ANIMAL_APE = re.compile(
    r"^(01\.4[1-7]Z|01\.49Z|01\.50Z|03\.(11|12|21|22)Z|10\.1[1-3][A-Z]|10\.20Z|10\.51[A-D]|46\.23Z"
    r"|46\.32[A-C]|46\.38A|47\.2[23]Z)$")
_APE_LINE = re.compile(r"Activit[ée] Principale Exerc[ée]e \(APE\)\s*(\d{2}\.\d{2}[A-Z])\s*-\s*(.+?)(?=\s+Appartenance|\s+Description|$)")


def ape_is_animal(code: str | None) -> bool:
    return bool(code) and bool(ANIMAL_APE.match(code.strip()))


def parse_avis(text: str) -> tuple[str, str] | None:
    """(code, libellé) de la ligne APE d'un avis de situation Sirene, ou None."""
    m = _APE_LINE.search(re.sub(r"\s+", " ", text or ""))
    return (m.group(1), m.group(2).strip()) if m else None


def build_rows(companies: list[dict], brands_by_parent: dict[str, list[dict]], avis: dict[str, tuple[str, str, str]],
               documented: set[str], today: str) -> list[EvidenceRow]:
    """avis : SIREN -> (code, libellé, url de l'avis). Une ligne par société et par
    marque directe non documentée, hors marques sans intrant animal."""
    rows: list[EvidenceRow] = []
    for co in companies:
        rec = avis.get(str(co.get("siren") or ""))
        if not rec or not ape_is_animal(rec[0]):
            continue
        code, label, url = rec
        quote = f"« Activité Principale Exercée (APE) {code} - {label} »"
        name = co.get("legal_name") or co["slug"]
        targets = [(co, f"Avis de situation au répertoire Sirene (Insee) de {name} (SIREN {co['siren']}) : {quote}")]
        for b in brands_by_parent.get(co["id"], []):
            if b.get("animal_free"):
                continue
            targets.append((b, f"Avis de situation au répertoire Sirene (Insee) de {name} (SIREN {co['siren']}), "
                               f"propriétaire de la marque : {quote}"))
        for ent, excerpt in targets:
            if ent["slug"] in documented:
                continue
            rows.append(EvidenceRow(
                entity_slug=ent["slug"], indicator_code="ANI_EXPLOITATION", source_code="INPI_SIRENE",
                nature="result", observed_on=today, value_type="category", value_text=label.lower(),
                normalized_value=0.0, confidence=0.9 if ent is co else 0.85, source_url=url,
                excerpt=f"{excerpt} — recours à l'exploitation animale (activité principale officielle).",
                reviewer=REVIEWER,
            ))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Exploitation animale d'après le code APE officiel.")
    parser.add_argument("--apply", action="store_true", help="écrit en base (sinon contrôle)")
    parser.add_argument("--cache", default="ani_ape_cache.json",
                        help="fichier JSON des réponses déjà lues (annuaire et avis), pour ne pas les redemander")
    args = parser.parse_args()
    import json
    import os
    cache: dict[str, dict] = json.load(open(args.cache, encoding="utf-8")) if os.path.exists(args.cache) else {}
    config.require_supabase()
    c = httpx.Client(timeout=60)
    ents = supabase_client.get_all(c, "entities", {"select": "id,slug,legal_name,siren,is_brand,parent_id,animal_free"})
    ind = supabase_client.get_all(c, "indicators", {"select": "id,code", "code": "eq.ANI_EXPLOITATION"})[0]["id"]
    ev = supabase_client.get_all(c, "evidence", {"select": "entity_id", "indicator_id": f"eq.{ind}",
                                                  "review_status": "in.(approved,pending)"})
    slug_by_id = {e["id"]: e["slug"] for e in ents}
    documented = {slug_by_id[r["entity_id"]] for r in ev if r["entity_id"] in slug_by_id}
    companies = [e for e in ents if not e["is_brand"] and e.get("siren")]
    brands_by_parent: dict[str, list[dict]] = {}
    for e in ents:
        if e["is_brand"] and e.get("parent_id"):
            brands_by_parent.setdefault(e["parent_id"], []).append(e)
    print(f"{len(companies)} sociétés avec SIREN ; {len(documented)} entités déjà documentées")

    avis: dict[str, tuple[str, str, str]] = {}
    quota = False
    with httpx.Client(timeout=60, follow_redirects=True) as w:
        for co in companies:
            siren = str(co["siren"])
            ent = cache.setdefault(siren, {})
            if "ape" not in ent:
                try:
                    r = w.get(SEARCH_URL, params={"q": siren, "per_page": 3})
                    hit = next((x for x in r.json().get("results", []) if x.get("siren") == siren), None)
                except (httpx.HTTPError, ValueError):
                    continue
                time.sleep(0.25)
                ent.update(ape=(hit or {}).get("activite_principale"), etat=(hit or {}).get("etat_administratif"),
                           siret=((hit or {}).get("siege") or {}).get("siret"))
            if ent.get("etat") != "A" or not ape_is_animal(ent.get("ape")) or not ent.get("siret"):
                continue
            url = AVIS_URL.format(siret=ent["siret"])
            if "avis" not in ent:
                if quota:
                    continue
                try:
                    ent["avis"] = parse_avis(document_text(url, w))
                except httpx.HTTPStatusError as err:
                    if err.response.status_code == 429:
                        # Quota de l'Insee atteint : on s'arrête, sans réessayer ; relancer plus tard.
                        print("  quota de l'Insee atteint : avis restants à lire lors d'une prochaine exécution")
                        quota = True
                    else:
                        print(f"  avis illisible ({err.response.status_code}) : {co['slug']}")
                    continue
                except httpx.HTTPError as err:
                    print(f"  avis illisible ({type(err).__name__}) : {co['slug']}")
                    continue
                time.sleep(1.5)
            parsed = ent.get("avis")
            if not parsed or parsed[0] != ent["ape"]:
                print(f"  avis discordant : {co['slug']} ({ent.get('ape')} / {parsed})")
                continue
            avis[siren] = (parsed[0], parsed[1], url)
            print(f"✔ {co['slug']} : {parsed[0]} - {parsed[1]}")
    json.dump(cache, open(args.cache, "w", encoding="utf-8"), ensure_ascii=False)

    rows = build_rows(companies, brands_by_parent, avis, documented, date.today().isoformat())
    print(f"\n{len(avis)} sociétés à activité animale ; {len(rows)} preuves (sociétés et marques)")
    if args.apply:
        stats = insert_evidence(rows)
        print(f"Insérées: {stats['inserted']} · ignorées: {stats['skipped']}")
    else:
        for r in rows[:40]:
            print("  ", r.entity_slug, "|", r.value_text)
        print("(contrôle : rien n'a été écrit. Relancer avec --apply.)")


if __name__ == "__main__":
    main()
