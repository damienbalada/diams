"""Import ESEF : taux effectif d'imposition et déclaration pays par pays.

Connecteur DÉTERMINISTE (source tier regulatory) : il lit des valeurs balisées
et cite le texte officiel, sans interprétation → publication automatique
(`auto:import_esef`), conformément à REVIEW_MODEL.md.

  TAX_EFFECTIVE_RATE  impôt / résultat avant impôt de l'exercice clos (en %),
                      seulement si « avant impôt − impôt = net » est vérifié.
  TAX_CBCR_PUBLISHED  vrai si le rapport cite l'art. L511-45 CMF (implantations
                      par pays) ; seulement pour les entités soumises au régime
                      EU_CRD_CBCR.

Usage :
    python -m paris_memoire.import_esef                         # dry-run, toutes les entités avec LEI
    python -m paris_memoire.import_esef --only bnp-paribas,bpce --apply
"""
from __future__ import annotations

import argparse

import httpx

from . import config
from .connectors import esef
from .load import EvidenceRow, insert_evidence


_SYMBOL = {"EUR": "M€", "USD": "M$", "GBP": "M£"}


def _fmt_m(x: float, currency: str = "EUR") -> str:
    return f"{x / 1e6:,.0f}".replace(",", " ") + " " + _SYMBOL.get(currency, f"M {currency}")


def tax_rate_row(slug: str, f: esef.Filing, tr: esef.TaxRate, currency: str = "EUR") -> EvidenceRow:
    year = f.period_end[:4]
    pct = f"{tr.rate_pct:.1f}".replace(".", ",")
    return EvidenceRow(
        entity_slug=slug, indicator_code="TAX_EFFECTIVE_RATE", source_code="ESEF", nature="result",
        observed_on=f.date_added, value_type="numeric", value_numeric=tr.rate_pct, confidence=0.95,
        source_url=f.viewer_url or f.json_url, reviewer="import_esef",
        excerpt=(f"Rapport financier annuel {year} (ESEF, faits IFRS balisés) : résultat net "
                 f"{_fmt_m(tr.net, currency)} + impôt sur les bénéfices {_fmt_m(tr.tax, currency)} = résultat avant "
                 f"impôt {_fmt_m(tr.pbt, currency)} (sous-total non balisé par l'émetteur, reconstitué) → taux "
                 f"effectif {pct} %.")
        if tr.derived else
                (f"Rapport financier annuel {year} (ESEF, faits IFRS balisés) : résultat avant impôt "
                 f"{_fmt_m(tr.pbt, currency)}, impôt sur les bénéfices {_fmt_m(tr.tax, currency)} → taux effectif "
                 f"{pct} %. Contrôle : résultat net {_fmt_m(tr.net, currency)} = avant impôt − impôt."),
    )


def cbcr_row(slug: str, f: esef.Filing, quote: str) -> EvidenceRow:
    return EvidenceRow(
        entity_slug=slug, indicator_code="TAX_CBCR_PUBLISHED", source_code="ESEF", nature="result",
        observed_on=f.date_added, value_type="boolean", value_boolean=True, normalized_value=1.0, confidence=0.95,
        source_url=f.viewer_url or f.report_url, reviewer="import_esef",
        excerpt=f"Rapport financier annuel {f.period_end[:4]} (ESEF) : « {quote[:400]} »",
    )


def _get(client: httpx.Client, path: str, params: dict) -> list[dict]:
    h = {"apikey": config.SUPABASE_SERVICE_ROLE_KEY, "Authorization": f"Bearer {config.SUPABASE_SERVICE_ROLE_KEY}"}
    r = client.get(f"{config.SUPABASE_URL}/rest/v1/{path}", params=params, headers=h)
    r.raise_for_status()
    return r.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Import ESEF (taux effectif, CbCR bancaire).")
    parser.add_argument("--only", help="slugs séparés par des virgules (défaut : toutes les entités avec LEI)")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    config.require_supabase()

    rows: list[EvidenceRow] = []
    with httpx.Client(timeout=120) as db, httpx.Client(timeout=300) as web:
        from .supabase_client import get_all
        ents = get_all(db, "entities", {"select": "id,slug,lei,country", "lei": "not.is.null"})
        if args.only:
            keep = set(args.only.split(","))
            ents = [e for e in ents if e["slug"] in keep]
        crd = {r["entity_id"] for r in _get(db, "entity_regimes", {"select": "entity_id,disclosure_regimes!inner(code)",
                                                                    "disclosure_regimes.code": "eq.EU_CRD_CBCR"})}
        for e in sorted(ents, key=lambda x: x["slug"]):
            f = esef.latest_filing(e["lei"], web, prefer_country=e.get("country"))
            if f is None:
                continue
            xbrl = web.get(f.json_url).json()
            facts = esef.annual_facts(xbrl, f.period_end)
            tr = esef.effective_tax_rate(facts)
            cur = esef.annual_currency(xbrl, f.period_end)
            if tr and cur:
                rows.append(tax_rate_row(e["slug"], f, tr, cur))
                print(f"✔ {e['slug']:24} {f.period_end}  taux effectif {tr.rate_pct:5.1f} %  (avant impôt {_fmt_m(tr.pbt, cur)})")
            elif tr:
                print(f"· {e['slug']:24} {f.period_end}  devise du résultat non balisée : aucune preuve créée")
            else:
                print(f"· {e['slug']:24} {f.period_end}  triplet IFRS absent ou incohérent : {facts}")
            if e["id"] in crd and f.report_url:
                q = esef.cbcr_quote(esef.report_text(f.report_url, web))
                if q:
                    rows.append(cbcr_row(e["slug"], f, q))
                    print(f"  ↳ déclaration pays par pays : « {q[:110]}… »")
                else:
                    print("  ↳ déclaration pays par pays NON TROUVÉE dans le rapport (aucune preuve créée)")

    print(f"\n{len(rows)} preuve(s) (source ESEF, tier regulatory → publication automatique)")
    if args.apply:
        stats = insert_evidence(rows)
        print(f"Insérées : {stats['inserted']} · ignorées : {stats['skipped']}")
    else:
        print("(dry-run : relancer avec --apply)")


if __name__ == "__main__":
    main()
