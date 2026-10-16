"""Présence dans les juridictions du top 10 de l'indice des paradis fiscaux pour les entreprises
(Corporate Tax Haven Index du Tax Justice Network, édition du 2 décembre 2025), d'après la liste des
filiales que le groupe publie lui-même : annexe 21 (« Subsidiaries of the Registrant ») de son
rapport annuel 10-K déposé à la SEC.

Règles (décision de l'éditeur, 16/10/2026) :
  - on compte les lignes du tableau des filiales dont la colonne « juridiction » est l'une des dix ;
  - le pays du siège du groupe n'est pas compté (une filiale suisse d'un groupe suisse n'est pas un
    détour) ;
  - l'annexe 21 peut ne lister que les filiales importantes : la valeur est un minimum, l'extrait le dit.

Usage :
    python -m diams.import_paradis_fiscaux            # contrôle
    python -m diams.import_paradis_fiscaux --apply    # écrit (document réglementaire : publié)
"""
from __future__ import annotations

import argparse
import html
import re
import time

import httpx

from . import config, supabase_client
from .connectors.sec import UA
from .load import EvidenceRow, insert_evidence

REVIEWER = "auto:paradis_fiscaux"
TJN = "https://cthi.taxjustice.net/countries/{}"
# Rang, code pays ISO, nom français, motif de la colonne « juridiction » (sans « New Jersey »).
TOP10 = [
    (1, "VG", "Îles Vierges britanniques", r"British Virgin Islands|Virgin Islands,? British|\bB\.?V\.?I\.?$"),
    (2, "KY", "Îles Caïmans", r"Cayman"),
    (3, "CH", "Suisse", r"Switzerland|Swiss Confederation"),
    (4, "BM", "Bermudes", r"Bermuda"),
    (5, "SG", "Singapour", r"Singapore"),
    (6, "HK", "Hong Kong", r"Hong Kong"),
    (7, "NL", "Pays-Bas", r"Netherlands(?! Antilles)|The Netherlands|Holland"),
    (8, "JE", "Jersey", r"(?<!New )\bJersey\b(?!,? (?:USA|United States))"),
    (9, "IE", "Irlande", r"(?<!Northern )\bIreland\b|Republic of Ireland"),
    (10, "LU", "Luxembourg", r"Luxembourg"),
]


def rows_of(page_html: str) -> list[list[str]]:
    """Lignes des tableaux de l'annexe : cellules textuelles non vides."""
    out = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page_html, flags=re.S | re.I):
        cells = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", td))).strip()
                 for td in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, flags=re.S | re.I)]
        cells = [c for c in cells if c and c not in ("​",)]
        if len(cells) >= 2:
            out.append(cells)
    return out


def count(rows: list[list[str]], home: str | None) -> tuple[dict[str, int], dict[str, str]]:
    """Nombre de filiales par juridiction du top 10 (colonne juridiction = dernière cellule)."""
    n: dict[str, int] = {}
    ex: dict[str, str] = {}
    pct = re.compile(r"^[\d.,]*\s*%?$|^%$|^\(?\d+(?:\.\d+)?\)?$")
    for cells in rows:
        # Colonne juridiction : dernière cellule qui n'est pas un pourcentage de détention
        # (« 100% », « 100 » puis « % » chez Amazon, Edgewell).
        rest = [x for x in cells[1:] if not pct.match(x)]
        if not rest:
            continue
        jur = rest[-1]
        for _, cc, nom, pat in TOP10:
            if cc == home:
                continue
            if re.search(pat, jur, re.I) and len(jur) < 60:
                n[nom] = n.get(nom, 0) + 1
                ex.setdefault(nom, f"{cells[0]} {jur}")
                break
    return n, ex


def main() -> None:
    ap = argparse.ArgumentParser(description="Filiales dans le top 10 des paradis fiscaux (annexe 21, SEC).")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    config.require_supabase()
    c = httpx.Client(timeout=120)
    ents = supabase_client.get_all(c, "entities", {"select": "id,slug,country,is_brand,parent_id"})
    roots = {e["slug"]: e for e in ents if not e["is_brand"] and not e["parent_id"]}
    # CIK des groupes : tiré des documents SEC déjà cités dans leurs preuves.
    ev = supabase_client.get_all(c, "evidence", {"select": "entity_id,source_url", "source_url": "like.*sec.gov/Archives/edgar/data/*"})
    by_id = {e["id"]: e["slug"] for e in ents}
    cik: dict[str, str] = {}
    for r in ev:
        m = re.search(r"edgar/data/(\d+)/", r["source_url"] or "")
        s = by_id.get(r["entity_id"])
        if m and s in roots:
            cik.setdefault(s, m.group(1))
    sec = httpx.Client(headers=UA, timeout=120, follow_redirects=True)
    rows_out: list[EvidenceRow] = []
    for slug, k in sorted(cik.items()):
        try:
            sub = sec.get(f"https://data.sec.gov/submissions/CIK{int(k):010d}.json").json()
            rec = sub["filings"]["recent"]
            i = next(j for j, f in enumerate(rec["form"]) if f == "10-K")
            acc = rec["accessionNumber"][i].replace("-", "")
            date = rec["filingDate"][i]
            idx = sec.get(f"https://www.sec.gov/Archives/edgar/data/{int(k)}/{acc}/index.json").json()
            exn = [x["name"] for x in idx["directory"]["item"] if re.search(r"ex-?21|exhibit21|ex21", x["name"], re.I)]
            if not exn:
                print(f"  {slug} : pas d'annexe 21")
                continue
            url = f"https://www.sec.gov/Archives/edgar/data/{int(k)}/{acc}/{exn[0]}"
            page = sec.get(url).text
        except (httpx.HTTPError, StopIteration, KeyError, ValueError) as err:
            print(f"  {slug} : illisible ({type(err).__name__})")
            continue
        time.sleep(0.3)
        rows = rows_of(page)
        if len(rows) < 3:
            print(f"  {slug} : annexe sans tableau lisible ({len(rows)} lignes)")
            continue
        home = roots[slug].get("country")
        n, ex = count(rows, home)
        total = sum(n.values())
        detail = " ; ".join(f"{nom} {v}" for nom, v in sorted(n.items(), key=lambda x: -x[1]))
        exemples = " ; ".join(f"« {e} »" for e in list(ex.values())[:3])
        excerpt = (f"Annexe 21 (liste des filiales) du rapport annuel 10-K déposé à la SEC le "
                   f"{'/'.join(reversed(date.split('-')))}, {len(rows)} lignes lues : {total} filiales dans les juridictions du "
                   f"top 10 de l'indice des paradis fiscaux pour les entreprises du Tax Justice Network (édition du 2 décembre 2025)"
                   + (f", hors pays du siège ({home})" if home and any(cc == home for _, cc, _, _ in TOP10) else "")
                   + (f" : {detail} ; exemples : {exemples}" if total else "")
                   + ". L'annexe peut ne lister que les filiales importantes : le nombre est un minimum.")
        rows_out.append(EvidenceRow(entity_slug=slug, indicator_code="TAX_HAVEN_PRESENCE", source_code="SEC_FILING",
                                    nature="result", observed_on=date, value_type="numeric", value_numeric=float(total),
                                    confidence=0.85, source_url=url, excerpt=excerpt, reviewer=REVIEWER))
        print(f"✔ {slug} : {total} ({detail or 'aucune'}) sur {len(rows)} lignes")
    print(f"\n{len(rows_out)} groupes lus")
    if args.apply and rows_out:
        stats = insert_evidence(rows_out)
        print(f"Insérées: {stats['inserted']} · ignorées: {stats['skipped']}")


if __name__ == "__main__":
    main()
