"""Connecteur SEC (EDGAR) — dépôts officiels des sociétés cotées américaines.

Identifiant : CIK (Central Index Key) de la SEC, retrouvé par le ticker dans la
table officielle de la SEC, puis contrôlé : la dénomination déposée doit
correspondre au nom légal de l'entité (GLEIF). En cas de doute : on saute.

Ce que l'on lit, sans interprétation :
- faits XBRL us-gaap du dernier rapport annuel 10-K : taux effectif d'impôt
  balisé (EffectiveIncomeTaxRateContinuingOperations), contrôlé par
  impôt / résultat avant impôt (à 0,6 point près ; résultat avant impôt
  reconstitué en résultat net + impôt quand l'émetteur ne le balise pas) ;
- faits XBRL ifrs-full du dernier rapport annuel 20-F (émetteurs étrangers en
  IFRS) : impôt sur le résultat / résultat avant impôt, dans la devise déposée ;
- les adresses du dernier 10-K et de la dernière circulaire de procuration
  (DEF 14A), où figurent le ratio de rémunération (Reg. S-K Item 402(u)) et
  l'indépendance des administrateurs (Item 407(a)).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

import httpx

# La SEC demande un User-Agent identifiant l'application ; aucune donnée personnelle.
UA = {"User-Agent": "DIAMS research pipeline (https://awareness-score.vercel.app)"}

#: Entité DIAMS → ticker. Le CIK est lu dans la table de la SEC, jamais saisi.
TICKERS: dict[str, str] = {
    "apple": "AAPL", "google": "GOOGL", "meta": "META", "microsoft": "MSFT", "netflix": "NFLX",
    "amazon": "AMZN", "tesla": "TSLA", "nike": "NKE",
    "coca-cola": "KO", "pepsico": "PEP", "procter-gamble": "PG", "mondelez": "MDLZ", "kraft-heinz": "KHC",
    "colgate-palmolive": "CL", "kenvue": "KVUE",
    "general-mills": "GIS", "mccormick": "MKC", "kimberly-clark": "KMB", "coty": "COTY", "keurig-dr-pepper": "KDP",
    "monster-beverage": "MNST", "brown-forman": "BF-B", "edgewell": "EPC", "energizer": "ENR", "mattel": "MAT",
    "hasbro": "HAS", "3m": "MMM", "newell-brands": "NWL", "stanley-black-decker": "SWK", "post-holdings": "POST",
    "spectrum-brands": "SPB", "kontoor": "KTB", "wd-40": "WDFC", "church-dwight": "CHD", "nomad-foods": "NOMD",
    "mcdonalds": "MCD", "starbucks": "SBUX", "yum-brands": "YUM", "rbi": "QSR",
    # Émetteurs étrangers (rapport annuel 20-F en IFRS)
    "unilever": "UL", "toyota": "TM", "sony": "SONY", "stellantis": "STLA",
}

_SUFFIX = {"inc", "incorporated", "corp", "corporation", "company", "co", "the", "plc", "ltd", "limited", "sa"}


def norm(name: str) -> str:
    """Nom comparable : minuscules, sans ponctuation ni forme juridique."""
    s = re.sub(r"['’]", "", name.lower().replace("&", " and "))  # McDonald's = MCDONALDS
    words = re.sub(r"[^a-z0-9 ]+", " ", s).split()
    return " ".join(w for w in words if w not in _SUFFIX)


def company_index(client: httpx.Client) -> dict[str, tuple[int, str]]:
    r = client.get("https://www.sec.gov/files/company_tickers.json", headers=UA)
    r.raise_for_status()
    return {v["ticker"]: (int(v["cik_str"]), v["title"]) for v in r.json().values()}


def submissions(cik: int, client: httpx.Client) -> dict:
    r = client.get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json", headers=UA)
    r.raise_for_status()
    return r.json()


@dataclass
class Filing:
    form: str
    filed: str
    accession: str
    url: str


def latest_form(sub: dict, form: str, cik: int) -> Filing | None:
    rec = sub.get("filings", {}).get("recent", {})
    for i, f in enumerate(rec.get("form", [])):
        if f == form:
            acc = rec["accessionNumber"][i]
            url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{rec['primaryDocument'][i]}"
            return Filing(form=f, filed=rec["filingDate"][i], accession=acc, url=url)
    return None


def company_facts(cik: int, client: httpx.Client) -> dict:
    r = client.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json", headers=UA, timeout=300)
    r.raise_for_status()
    return r.json()


PBT_CONCEPTS = (
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
)


def _annual(facts: dict, concept: str, unit: str, taxonomy: str = "us-gaap",
            form: str = "10-K") -> dict[str, dict]:
    """Faits annuels (≈ 1 an) déposés dans un rapport annuel, par date de clôture."""
    out: dict[str, dict] = {}
    for x in facts.get("facts", {}).get(taxonomy, {}).get(concept, {}).get("units", {}).get(unit, []):
        if x.get("form") != form or not x.get("start"):
            continue
        days = (date.fromisoformat(x["end"]) - date.fromisoformat(x["start"])).days
        if 350 <= days <= 380:
            prev = out.get(x["end"])
            if prev is None or x.get("filed", "") > prev.get("filed", ""):
                out[x["end"]] = x
    return out


@dataclass
class TaxRate:
    rate_pct: float
    tax: float
    pbt: float
    fy_end: str
    filed: str
    accession: str
    currency: str = "USD"
    #: "tagged" : taux balisé (10-K) ; "pbt_derived" : taux balisé, résultat avant
    #: impôt reconstitué ; "ifrs" : impôt / résultat avant impôt d'un 20-F.
    method: str = "tagged"


def effective_tax_rate(facts: dict, tolerance_pt: float = 0.6) -> TaxRate | None:
    """Dernier exercice : taux balisé, contrôlé par impôt / résultat avant impôt."""
    rates = _annual(facts, "EffectiveIncomeTaxRateContinuingOperations", "pure")
    taxes = _annual(facts, "IncomeTaxExpenseBenefit", "USD")
    pbts: dict[str, dict] = {}
    for c in PBT_CONCEPTS:
        for end, x in _annual(facts, c, "USD").items():
            pbts.setdefault(end, x)
    method = "tagged"
    if not set(rates) & set(taxes) & set(pbts):
        # Résultat avant impôt non balisé : résultat net (part du groupe et
        # minoritaires) + impôt, retenu seulement s'il recoupe le taux balisé.
        for concept in ("ProfitLoss", "NetIncomeLoss"):
            nets = _annual(facts, concept, "USD")
            pbts = {e: {**nets[e], "val": nets[e]["val"] + taxes[e]["val"]} for e in set(nets) & set(taxes)}
            if set(rates) & set(pbts):
                method = "pbt_derived"
                break
    common = sorted(set(rates) & set(taxes) & set(pbts))
    if not common:
        return None
    end = common[-1]
    rate, tax, pbt = rates[end]["val"] * 100, taxes[end]["val"], pbts[end]["val"]
    if pbt <= 0 or abs(100 * tax / pbt - rate) > tolerance_pt:
        return None
    return TaxRate(rate_pct=round(rate, 1), tax=tax, pbt=pbt, fy_end=end, filed=rates[end].get("filed", ""),
                   accession=rates[end].get("accn", ""), method=method)


def effective_tax_rate_ifrs(facts: dict) -> TaxRate | None:
    """Dernier 20-F en IFRS : impôt sur le résultat / résultat avant impôt.

    Exercice en perte, ou taux hors de [0 ; 60 %] (année atypique) : pas de taux.
    """
    units = facts.get("facts", {}).get("ifrs-full", {}).get("ProfitLossBeforeTax", {}).get("units", {})
    for cur in units:
        pbts = _annual(facts, "ProfitLossBeforeTax", cur, "ifrs-full", "20-F")
        taxes = _annual(facts, "IncomeTaxExpenseContinuingOperations", cur, "ifrs-full", "20-F")
        common = sorted(set(pbts) & set(taxes))
        if not common:
            continue
        end = common[-1]
        pbt, tax = pbts[end]["val"], taxes[end]["val"]
        if pbt <= 0:
            return None
        rate = 100 * tax / pbt
        if not 0 <= rate <= 60:
            return None
        return TaxRate(rate_pct=round(rate, 1), tax=tax, pbt=pbt, fy_end=end, filed=pbts[end].get("filed", ""),
                       accession=pbts[end].get("accn", ""), currency=cur, method="ifrs")
    return None
