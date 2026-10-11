"""Clean Clothes Campaign — « Living Wages Paid Score » (Fashion Checker), liste complète.

Le collectif Clean Clothes Campaign note chaque année les grandes marques de
vêtements sur le salaire vital réellement versé dans leurs usines fournisseurs,
à partir de ce que publie la marque (Fashion Checker, données ouvertes Wikirate) :

  A  la marque affirme que 100 % de ses usines fournisseurs versent un salaire
     vital, nomme la référence utilisée et publie les salaires usine par usine ;
  B  plus de 50 % ; C plus de 26 % ; D entre 1 et 25 % (mêmes exigences) ;
  E  la marque ne verse (ni ne prétend verser) de salaire vital à aucun de ses
     travailleurs.

On l'écrit sur SUP_LIVING_WAGE (salaire décent chez les fournisseurs) : A 1,0 /
B 0,75 / C 0,5 / D 0,25 / E 0 ; source CCC (ONG auditée), publication
automatique. Indicateur de groupe : la note d'un groupe (H&M, Inditex, Fast
Retailing) vaut pour ses marques ; une maison notée seule (Gucci, Louis
Vuitton) l'est à son nom. Liste fermée (environ 110 marques) : une marque
absente n'a pas été évaluée (indicateur complémentaire).

Usage :
    python -m paris_memoire.import_fashion_checker [--file reponses.json] [--apply]
"""
from __future__ import annotations

import argparse
import json

import httpx

from . import config, supabase_client
from .load import EvidenceRow, insert_evidence

METRIC = "Clean_Clothes_Campaign+Living_Wages_Paid_Score"
API_URL = f"https://wikirate.org/{METRIC}+Answer.json"
UA = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)"}
PAGE_URL = "https://fashionchecker.org/"
SCALE = {"A": 1.0, "B": 0.75, "C": 0.5, "D": 0.25, "E": 0.0}
MEANING = {
    "A": "affirme que 100 % de ses usines fournisseurs versent un salaire vital, avec la référence et les salaires usine par usine",
    "B": "affirme que plus de la moitié de ses usines fournisseurs versent un salaire vital",
    "C": "affirme que plus de 26 % de ses usines fournisseurs versent un salaire vital",
    "D": "affirme qu'entre 1 et 25 % de ses usines fournisseurs versent un salaire vital",
    "E": "ne verse (ni ne prétend verser) de salaire vital à aucun de ses travailleurs",
}

# Nom exact dans la liste -> slug DIAMS (vérifié à la main ; jamais d'inclusion).
ALIASES = {
    "Adidas AG": "adidas",
    "Amazon.com, Inc.": "amazon",
    "Balenciaga": "balenciaga",
    "Bottega Veneta": "bottega-veneta",
    "Chanel SA": "chanel",
    "Chloe": "chloe",
    "Decathlon Group": "decathlon",
    "Fast Retailing": "fast-retailing",
    "Gucci": "gucci",
    "H&M": "hm-group",
    "Hermes International": "hermes",
    "Inditex": "inditex",
    "Louis Vuitton Malletier SA (LVMH)": "louis-vuitton",
    "Nike Inc.": "nike",
    "Saint Laurent": "saint-laurent",
    "Shein": "shein",
}


def parse_answers(payload: dict, year: int) -> dict[str, dict]:
    """Nom de la marque -> réponse (lettre A à E) pour l'année demandée."""
    return {i["company"]: i for i in payload.get("items", [])
            if i.get("year") == year and i.get("value") in SCALE}


def build_row(slug: str, name: str, answer: dict, observed_on: str) -> EvidenceRow:
    grade = answer["value"]
    return EvidenceRow(
        entity_slug=slug, indicator_code="SUP_LIVING_WAGE", source_code="CCC", nature="result",
        observed_on=observed_on, value_type="category", value_text=grade,
        normalized_value=SCALE[grade], confidence=0.85, source_url=PAGE_URL,
        excerpt=(f"Clean Clothes Campaign, Fashion Checker {answer['year']} (salaire vital réellement versé "
                 f"chez les fournisseurs ; données ouvertes Wikirate) : « {name} » — note {grade} : la marque "
                 f"{MEANING[grade]}."),
        reviewer="import_fashion_checker",
    )


def _rest(c: httpx.Client, method: str, table: str, **kw) -> httpx.Response:
    r = c.request(method, f"{config.SUPABASE_URL}/rest/v1/{table}",
                  headers={**supabase_client._headers(), **kw.pop("headers", {})}, **kw)
    r.raise_for_status()
    return r


def main() -> None:
    ap = argparse.ArgumentParser(description="Clean Clothes Campaign : salaire vital versé chez les fournisseurs.")
    ap.add_argument("--year", type=int, default=2026)
    ap.add_argument("--file", help="réponses Wikirate déjà téléchargées (sinon téléchargées)")
    ap.add_argument("--apply", action="store_true", help="écrit en base (sinon dry-run)")
    args = ap.parse_args()
    config.require_supabase()
    with httpx.Client(timeout=120) as c:
        if args.file:
            payload = json.load(open(args.file, encoding="utf-8"))
        else:
            r = c.get(API_URL, params={"filter[year]": args.year, "limit": 1000}, headers=UA)
            r.raise_for_status()
            payload = r.json()
        answers = parse_answers(payload, args.year)
        print(f"{len(answers)} marques notées en {args.year}")
        if len(answers) < 100:
            raise SystemExit("Liste incomplète : rien n'est écrit.")
        slugs = {e["slug"] for e in _rest(c, "GET", "entities", params={"select": "slug"}).json()}
        rows = []
        for name, slug in ALIASES.items():
            if name not in answers or slug not in slugs:
                print(f"  ✘ {name} → {slug} : absent de la liste ou de la base")
                continue
            a = answers[name]
            # Date de publication de la note (fiche de la réponse sur Wikirate).
            detail = c.get(a.get("url") or f"https://wikirate.org/{METRIC}+{name}+{args.year}.json", headers=UA)
            observed = (detail.json().get("created_at") or f"{args.year}-01-01")[:10] if detail.is_success \
                else f"{args.year}-01-01"
            rows.append(build_row(slug, name, a, observed))
            print(f"  ✔ {slug:<16} {a['value']}  ({name}, {observed})")
        print(f"{len(rows)} notes à écrire")
        if not args.apply:
            print("(dry-run : rien n'a été écrit. Relancer avec --apply.)")
            return
        print(insert_evidence(rows, c))


if __name__ == "__main__":
    main()
