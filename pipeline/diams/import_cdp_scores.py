"""CDP — notes publiques 2025 (climat, eau) de chaque groupe suivi.

Lit la liste complète publiée par CDP (connectors/cdp_scores.py) et écrit
ENV_CDP_CLIMATE et WAT_CDP pour les groupes rapprochés (table explicite, puis
égalité exacte des noms normalisés, résultat unique exigé). Source CDP (ONG
auditée) : publication automatique.

  « Did not disclose » : F (sollicitée, n'a pas répondu) ;
  « Not Scored », « See disclosing organisation », vide : pas de note.

Les lignes saisies à la main avant le connecteur (`curation-v1`) sur ces deux
indicateurs sont retirées (`remplace:import_cdp_scores`) : notes 2022-2023
recopiées de communiqués d'entreprises, invérifiables dans la donnée publique.

Usage :
    python -m diams.import_cdp_scores [--file page.html] [--apply]
"""
from __future__ import annotations

import argparse

import httpx

from . import config, supabase_client
from .connectors import cdp_scores as cs
from .connectors import flourish
from .connectors.cdp import GRADE_MAP
from .load import EvidenceRow, insert_evidence
from .normalize.names import normalize_name

# Slug DIAMS -> nom exact dans la liste CDP (vérifié à la main : société mère).
ALIASES = {
    "procter-gamble": "Procter & Gamble Company",
    "edgewell": "Edgewell Personal Care",
    "laurent-perrier": "Laurent-Perrier Group",
    "thai-union": "Thai Union Group PLC",
    "pierre-fabre": "PIERRE FABRE SA",
    "mccain": "McCain Foods",
    "sofidel": "Sofidel S.p.A.",
    "hm-group": "H&M Hennes & Mauritz AB",
    "samsung": "Samsung Electronics",
    "bpce": "Groupe BPCE",
    "groupe-bel": "BEL GROUP",
    "beiersdorf": "Beiersdorf Aktiengesellschaft",
    "barilla": "Barilla Holding SpA",
    "axa": "AXA Group",
    "schwarz-gruppe": "Schwarz Group GmbH",
    # DIAMS suit le groupe Ingka (magasins IKEA) : sa société mère est Ingka Holding.
    "ikea": "Ingka Holding B.V.",
    "reckitt": "Reckitt Benckiser",
    # Carlsberg A/S répond au CDP par sa filiale opérationnelle à 100 %, qui porte
    # l'ensemble des brasseries du groupe.
    "carlsberg": "Carlsberg Breweries A/S",
    # Noms trop courts ou différents de la raison sociale (vérifiés : sociétés mères).
    "hp-inc": "HP Inc",
    "lego": "The LEGO Group",
    # Sociétés mères dont le nom diffère de la raison sociale suivie (vérifiées).
    "dr-oetker": "Dr. August Oetker KG",
    "ecotone-france": "Ecotone",
    "picard": "PICARD GROUPE SAS",
}
# Rapprochement ambigu (entité CDP incertaine) : on s'abstient.
SKIP = {
    "ab-inbev",                         # « Anheuser Busch InBev » enregistré aux États-Unis : entité incertaine
    "credit-mutuel-alliance-federale",  # BFCM, holding, pas le groupe
}
GENERIC = {"group", "groupe", "holding", "holdings", "international", "company", "corporation"}

LABEL = {"climate": "climat", "water": "sécurité de l'eau", "forests": "forêts"}


def match(slug: str, names: list[str], by_name: dict[str, list[cs.CdpScore]],
          by_norm: dict[str, list[cs.CdpScore]]) -> cs.CdpScore | None:
    if slug in SKIP:
        return None
    if slug in ALIASES:
        hits = by_name.get(ALIASES[slug], [])
        return hits[0] if len(hits) == 1 else None
    found: dict[str, cs.CdpScore] = {}
    for n in names:
        key = normalize_name(n)
        if len(key) < 3 or key in GENERIC:
            continue
        for h in by_norm.get(key, []):
            found[h.company] = h
    return next(iter(found.values())) if len(found) == 1 else None


def rows_for(slug: str, s: cs.CdpScore) -> list[EvidenceRow]:
    out = []
    for field, code in (("climate", "ENV_CDP_CLIMATE"), ("water", "WAT_CDP"), ("forests", "ENV_CDP_FORESTS")):
        letter = getattr(s, field)
        if letter is None:
            continue
        what = ("« Did not disclose » : sollicitée par CDP, l'entreprise n'a pas répondu "
                "(note F selon la méthode CDP)") if letter == "F" else f"note {letter}"
        out.append(EvidenceRow(
            entity_slug=slug, indicator_code=code, source_code="CDP", nature="result",
            observed_on=f"{cs.SCORES_YEAR}-12-31", value_type="ordinal", value_text=letter,
            normalized_value=GRADE_MAP[letter], confidence=0.85, source_url=cs.SCORES_PAGE,
            excerpt=(f"CDP, notes publiques {cs.SCORES_YEAR} (liste complète, page « Scores and A Lists ») : "
                     f"« {s.company} » ({s.country}), {LABEL[field]} — {what}."),
            reviewer="import_cdp_scores",
        ))
    return out


def _rest(c: httpx.Client, method: str, table: str, **kw) -> httpx.Response:
    r = c.request(method, f"{config.SUPABASE_URL}/rest/v1/{table}",
                  headers={**supabase_client._headers(), **kw.pop("headers", {})}, **kw)
    r.raise_for_status()
    return r


def main() -> None:
    ap = argparse.ArgumentParser(description="CDP : notes publiques climat, eau et forêts des groupes suivis.")
    ap.add_argument("--file", help="page Flourish déjà téléchargée (sinon téléchargée)")
    ap.add_argument("--apply", action="store_true", help="écrit en base (sinon dry-run)")
    args = ap.parse_args()
    config.require_supabase()
    with httpx.Client(timeout=180) as c:
        if args.file:
            page = open(args.file, encoding="utf-8").read()
        else:
            r = c.get(flourish.flourish_url(cs.SCORES_VIS), headers={"User-Agent": "Mozilla/5.0 (DIAMS)"})
            r.raise_for_status()
            page = r.text
        scores = cs.parse_scores(page)
        print(f"{len(scores)} entreprises notées par CDP en {cs.SCORES_YEAR}")
        if len(scores) < 20000:
            raise SystemExit("Liste incomplète : rien n'est écrit.")
        by_name: dict[str, list[cs.CdpScore]] = {}
        by_norm: dict[str, list[cs.CdpScore]] = {}
        for s in scores:
            by_name.setdefault(s.company, []).append(s)
            by_norm.setdefault(normalize_name(s.company), []).append(s)
        ents = supabase_client.get_all(c, "entities", {"select": "slug,legal_name,display_name,parent_id"})
        rows: list[EvidenceRow] = []
        for g in (e for e in ents if not e.get("parent_id")):
            s = match(g["slug"], [g[k] for k in ("display_name", "legal_name") if g.get(k)], by_name, by_norm)
            if s:
                new = rows_for(g["slug"], s)
                rows += new
                print(f"  ✔ {g['slug']:<18} climat {s.climate or '—':<3} eau {s.water or '—':<3} forêts {s.forests or '—':<3} ({s.company})")
        print(f"{len(rows)} notes à écrire")
        old = []
        for code in ("ENV_CDP_CLIMATE", "WAT_CDP"):
            ind = _rest(c, "GET", "indicators", params={"select": "id", "code": f"eq.{code}"}).json()[0]["id"]
            old += _rest(c, "GET", "evidence", params={
                "select": "id", "indicator_id": f"eq.{ind}",
                "reviewer": "eq.curation-v1", "review_status": "eq.approved"}).json()
        print(f"{len(old)} ligne(s) curation-v1 à retirer")
        if not args.apply:
            print("(dry-run : rien n'a été écrit. Relancer avec --apply.)")
            return
        print(insert_evidence(rows, c))
        if old:
            _rest(c, "PATCH", "evidence", params={"id": f"in.({','.join(o['id'] for o in old)})"},
                  headers={"Prefer": "return=minimal"},
                  json={"review_status": "rejected", "reviewer": "remplace:import_cdp_scores"})
            print(f"{len(old)} ligne(s) curation-v1 retirées")


if __name__ == "__main__":
    main()
