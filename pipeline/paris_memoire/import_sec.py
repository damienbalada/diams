"""Import SEC : taux effectif d'imposition des sociétés cotées américaines.

Connecteur DÉTERMINISTE (source tier regulatory) : il lit le taux balisé du
dernier 10-K et le contrôle par impôt / résultat avant impôt → publication
automatique (`auto:import_sec`). Il affiche aussi la dernière circulaire de
procuration (DEF 14A), où le ratio de rémunération et l'indépendance des
administrateurs sont lus pour `curated/` (citations vérifiées par verify_curated).

Usage :
    python -m paris_memoire.import_sec                    # dry-run, toutes les entités de connectors.sec.TICKERS
    python -m paris_memoire.import_sec --only apple,meta --apply
"""
from __future__ import annotations

import argparse

import httpx

from . import config
from .connectors import sec
from .load import EvidenceRow, insert_evidence

#: Nom déposé à la SEC quand il diffère du nom d'usage de l'entité (contrôlé à la main).
NAME_ALIASES = {"google": "Alphabet Inc."}


_CUR = {"USD": "M$", "EUR": "M€", "GBP": "M£", "JPY": "M¥"}


def _fmt(x: float, currency: str = "USD") -> str:
    return f"{x / 1e6:,.0f}".replace(",", " ") + " " + _CUR.get(currency, f"M {currency}")


def tax_rate_row(slug: str, cik: int, tr: sec.TaxRate) -> EvidenceRow:
    pct = f"{tr.rate_pct:.1f}".replace(".", ",")
    folder = f"https://www.sec.gov/Archives/edgar/data/{cik}/{tr.accession.replace('-', '')}/"
    tax, pbt = _fmt(tr.tax, tr.currency), _fmt(tr.pbt, tr.currency)
    if tr.method == "ifrs":
        excerpt = (f"Rapport annuel 20-F, exercice clos le {tr.fy_end} (SEC, faits XBRL ifrs-full) : impôt sur le "
                   f"résultat {tax} / résultat avant impôt {pbt} → taux effectif {pct} %.")
    else:
        derived = " (résultat net + impôt, sous-total non balisé par l'émetteur)" if tr.method == "pbt_derived" else ""
        excerpt = (f"Rapport annuel 10-K, exercice clos le {tr.fy_end} (SEC, faits XBRL us-gaap) : taux effectif "
                   f"d'impôt balisé {pct} %. Contrôle : impôt sur les bénéfices {tax} / résultat avant impôt "
                   f"{pbt}{derived}.")
    return EvidenceRow(
        entity_slug=slug, indicator_code="TAX_EFFECTIVE_RATE", source_code="SEC_FILING", nature="result",
        observed_on=tr.filed, value_type="numeric", value_numeric=tr.rate_pct, confidence=0.95,
        source_url=folder, reviewer="import_sec", excerpt=excerpt,
    )


def same_company(slug: str, sec_name: str, legal_names: list[str]) -> bool:
    wanted = [sec.norm(n) for n in legal_names + ([NAME_ALIASES[slug]] if slug in NAME_ALIASES else [])]
    return sec.norm(sec_name) in wanted


def main() -> None:
    parser = argparse.ArgumentParser(description="Import SEC (taux effectif, adresses des dépôts).")
    parser.add_argument("--only", help="slugs séparés par des virgules")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    config.require_supabase()
    h = {"apikey": config.SUPABASE_SERVICE_ROLE_KEY, "Authorization": f"Bearer {config.SUPABASE_SERVICE_ROLE_KEY}"}

    slugs = args.only.split(",") if args.only else list(sec.TICKERS)
    rows: list[EvidenceRow] = []
    with httpx.Client(timeout=120) as c:
        ents = {e["slug"]: e for e in c.get(f"{config.SUPABASE_URL}/rest/v1/entities",
                                             params={"select": "slug,legal_name,lei"}, headers=h).json()}
        index = sec.company_index(c)
        for slug in slugs:
            e, ticker = ents.get(slug), sec.TICKERS.get(slug)
            if not e or not ticker or ticker not in index:
                print(f"· {slug:18} ticker inconnu ou entité absente")
                continue
            cik, title = index[ticker]
            names = [e["legal_name"]]
            if e.get("lei"):
                g = c.get(f"https://api.gleif.org/api/v1/lei-records/{e['lei']}")
                if g.status_code == 200:
                    names.append(g.json()["data"]["attributes"]["entity"]["legalName"]["name"])
            sub = sec.submissions(cik, c)
            if not same_company(slug, sub.get("name") or title, names):
                print(f"✗ {slug:18} CIK {cik} « {sub.get('name')} » ≠ {names} : ignoré")
                continue
            proxy = sec.latest_form(sub, "DEF 14A", cik)
            facts = sec.company_facts(cik, c)
            tr = sec.effective_tax_rate(facts) or sec.effective_tax_rate_ifrs(facts)
            if tr:
                rows.append(tax_rate_row(slug, cik, tr))
                print(f"✔ {slug:18} CIK {cik:<8} {tr.fy_end}  taux effectif {tr.rate_pct:5.1f} %")
            else:
                print(f"· {slug:18} CIK {cik:<8} taux balisé absent ou incohérent avec impôt / avant impôt")
            print(f"  ↳ DEF 14A {proxy.filed if proxy else '—'} {proxy.url if proxy else ''}")

    print(f"\n{len(rows)} preuve(s) (source SEC_FILING, tier regulatory → publication automatique)")
    if args.apply:
        stats = insert_evidence(rows)
        print(f"Insérées : {stats['inserted']} · ignorées : {stats['skipped']}")
    else:
        print("(dry-run : relancer avec --apply)")


if __name__ == "__main__":
    main()
