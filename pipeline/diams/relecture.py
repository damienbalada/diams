"""Relecture complète des preuves (PLAN_REFONTE.md), consignée dans le journal `indicator_reviews`.

    python -m diams.relecture connecteurs [--apply] [--rapport f.json] [--eu-file x] [--kse-file x]
                                          [--cdp-file x] [--sbti-file x] [--egapro-file x]
        Vague 0 : chaque preuve issue d'un connecteur (Égapro, CDP, registre européen, KSE, SBTi)
        est comparée, valeur par valeur, à ce que le connecteur produit sur sa source relue.
    python -m diams.relecture citations (--vague N | --only a,b) [--apply] [--rapport f.json]
        Chaque preuve documentaire du périmètre : citation retrouvée mot pour mot dans la source,
        valeur présente dans la citation (vérificateur de verify_curated).
    python -m diams.relecture manques (--vague N | --only a,b) [--rapport f.json]
        Indicateurs que la loi impose sans preuve : passages candidats du rapport réglementé, à
        lire avant de consigner « absence_confirmee » ou d'ajouter la preuve. Aucune écriture.

Vagues (périmètre = groupe racine et toute son arborescence) : 1 groupes soumis à la CSRD ;
2 groupes avec LEI et au moins 5 marques ; 3 sans LEI, au moins 5 marques ; 4 avec LEI, moins de
5 marques ; 5 autres. Sans --apply, rien n'est écrit.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from collections import defaultdict
from urllib.parse import urlparse

import httpx

from . import config, supabase_client
from .load import EvidenceRow

REVIEWER = "auto:relecture"
CONNECTOR_SOURCES = {"EGAPRO", "CDP", "EU_TRANSPARENCY", "KSE_LEAVE_RUSSIA", "SBTI"}
# Classements à édition publiée (données ouvertes, tableaux) : la page web citée n'en contient pas le
# texte ; ils se relisent contre leur jeu de données, par leur connecteur (passe dédiée).
RANKING_SOURCES = {"CCC", "KNOWTHECHAIN", "FTI", "FINANSOL", "BOCC"}
BLOCKING = {403, 429, 503}
# Preuves curées (citation relue à l'entrée) : relues mot pour mot. Les autres viennent d'un
# connecteur et se relisent par lui.
CURATED_REVIEWERS = {"auto:verify_curated", "delegue-editeur:verifie-mot-pour-mot", "revue-manuelle"}
# Décisions de l'éditeur (« decision-editeur:AAAA-MM-JJ ») : preuves curées, elles aussi.
CURATED_PREFIXES = ("decision-editeur:", "delegue-editeur:", "revue-")


def curated(ev: dict) -> bool:
    r = ev.get("reviewer") or ""
    return r in CURATED_REVIEWERS or r.startswith(CURATED_PREFIXES)


# --- Chargement -----------------------------------------------------------------------------

class Base:
    def __init__(self, c: httpx.Client):
        g = supabase_client.get_all
        self.ents = g(c, "entities", {"select": "id,slug,parent_id,is_brand,lei,siren,legal_name,display_name,country"})
        self.by_id = {e["id"]: e for e in self.ents}
        self.by_slug = {e["slug"]: e for e in self.ents}
        self.ind = {i["id"]: i["code"] for i in g(c, "indicators", {"select": "id,code"})}
        self.ind_id = {v: k for k, v in self.ind.items()}
        self.src = {s["id"]: s for s in g(c, "sources", {"select": "id,code,tier"})}
        self.ev = g(c, "evidence_active", {"select": "id,entity_id,indicator_id,source_id,value_type,value_numeric,"
                                                    "value_boolean,value_text,normalized_value,nature,observed_on,"
                                                    "confidence,excerpt,source_url,reviewer"})
        self.regimes = {r["id"]: r for r in g(c, "disclosure_regimes", {"select": "id,code,name"})}
        self.ent_reg = g(c, "entity_regimes", {"select": "entity_id,regime_id", "order": "entity_id.asc,regime_id.asc"})
        self.ind_reg = g(c, "indicator_regimes", {"select": "indicator_id,regime_id", "order": "indicator_id.asc,regime_id.asc"})
        self.exempt = {(x["entity_id"], x["indicator_id"]) for x in
                       g(c, "obligation_exemptions", {"select": "entity_id,indicator_id"})}
        self.children = defaultdict(list)
        for e in self.ents:
            if e.get("parent_id"):
                self.children[e["parent_id"]].append(e["id"])

    def tree(self, root_id: str) -> list[str]:
        out, todo = [], [root_id]
        while todo:
            x = todo.pop()
            out.append(x)
            todo += self.children.get(x, [])
        return out

    def row(self, ev: dict) -> EvidenceRow:
        f = lambda x: float(x) if x is not None else None  # noqa: E731
        return EvidenceRow(
            entity_slug=self.by_id[ev["entity_id"]]["slug"], indicator_code=self.ind[ev["indicator_id"]],
            source_code=self.src[ev["source_id"]]["code"], nature=ev["nature"], observed_on=ev["observed_on"],
            value_type=ev["value_type"], value_numeric=f(ev["value_numeric"]), value_boolean=ev["value_boolean"],
            value_text=ev["value_text"], normalized_value=f(ev["normalized_value"]), confidence=f(ev["confidence"]) or 0,
            source_url=ev["source_url"], excerpt=ev["excerpt"])

    def waves(self) -> dict[int, list[str]]:
        csrd = {r["entity_id"] for r in self.ent_reg if "CSRD" in self.regimes[r["regime_id"]]["name"]}
        out: dict[int, list[str]] = defaultdict(list)
        for e in self.ents:
            if e.get("parent_id") or e["is_brand"]:
                continue
            nb = sum(1 for x in self.tree(e["id"]) if self.by_id[x]["is_brand"])
            w = 1 if e["id"] in csrd else 2 if e.get("lei") and nb >= 5 else 3 if nb >= 5 else 4 if e.get("lei") else 5
            out[w].append(e["id"])
        return out

    def perimeter(self, vague: int | None, only: list[str] | None) -> tuple[list[str], set[str]]:
        roots = [self.by_slug[s]["id"] for s in only] if only else self.waves()[vague]
        ids: set[str] = set()
        for r in roots:
            ids.update(self.tree(r))
        return roots, ids


def write_reviews(c: httpx.Client, rows: list[dict]) -> int:
    h = {**supabase_client._headers(), "Prefer": "return=minimal"}
    for i in range(0, len(rows), 500):
        r = c.post(f"{config.SUPABASE_URL}/rest/v1/indicator_reviews", headers=h, json=rows[i:i + 500])
        r.raise_for_status()
    return len(rows)


def review(b: Base, ev: dict, outcome: str, detail: str, wave: int) -> dict:
    return {"entity_id": ev["entity_id"], "indicator_id": ev["indicator_id"], "evidence_id": ev["id"],
            "outcome": outcome, "detail": detail[:2000], "source_url": ev["source_url"],
            "reviewer": REVIEWER, "wave": wave}


# --- Vague 0 : preuves des connecteurs ------------------------------------------------------

def _roots_dicts(b: Base) -> list[dict]:
    return [e for e in b.ents if not e.get("parent_id")]


def produce_egapro(c, b, args) -> tuple[str, list[EvidenceRow]]:
    from .connectors import egapro
    from .import_egapro import build_rows
    if args.egapro_file:
        records, label = egapro.parse_csv(args.egapro_file), f"fichier {args.egapro_file}"
    else:
        sirens = sorted({str(e["siren"]) for e in b.ents if e.get("siren")})
        records, label = egapro.fetch_for_sirens(sirens), "API ouverte Égapro (data.economie.gouv.fr)"
    return label, build_rows(b.ents, egapro.latest_by_siren(records))


def produce_cdp(c, b, args):
    from .connectors import cdp_scores as cs, flourish
    from .import_cdp_scores import match, rows_for
    from .normalize.names import normalize_name
    if args.cdp_file:
        page, label = open(args.cdp_file, encoding="utf-8").read(), f"fichier {args.cdp_file}"
    else:
        r = c.get(flourish.flourish_url(cs.SCORES_VIS), headers={"User-Agent": "Mozilla/5.0 (DIAMS)"})
        r.raise_for_status()
        page, label = r.text, "liste publique CDP téléchargée"
    scores = cs.parse_scores(page)
    if len(scores) < 20000:
        raise RuntimeError(f"liste CDP incomplète ({len(scores)})")
    by_name, by_norm = defaultdict(list), defaultdict(list)
    for s in scores:
        by_name[s.company].append(s)
        by_norm[normalize_name(s.company)].append(s)
    rows = []
    for g in _roots_dicts(b):
        s = match(g["slug"], [g[k] for k in ("display_name", "legal_name") if g.get(k)], by_name, by_norm)
        if s:
            rows += rows_for(g["slug"], s)
    return label, rows


def produce_eu(c, b, args):
    from .connectors import eu_register as eu
    from .import_eu_register import match, rows_for
    from .normalize.names import normalize_name
    if args.eu_file:
        raw, label = open(args.eu_file, "rb").read(), f"fichier {args.eu_file}"
    else:
        r = c.get(eu.EXPORT_URL, headers={"User-Agent": "Mozilla/5.0 (DIAMS)"}, timeout=600)
        r.raise_for_status()
        raw, label = r.content, "export du registre téléchargé"
    export_date, regs = eu.parse_export(raw)
    if not export_date or len(regs) < 3000:
        raise RuntimeError("export du registre incomplet")
    by_name, by_norm = defaultdict(list), defaultdict(list)
    for r in regs:
        by_name[r.name].append(r)
        by_norm[normalize_name(r.name)].append(r)
    rows = []
    for g in _roots_dicts(b):
        r = match(g["slug"], [g[k] for k in ("display_name", "legal_name") if g.get(k)], by_name, by_norm)
        if r:
            rows += rows_for(g["slug"], r, export_date)
    return f"{label} (export du {export_date})", rows


def produce_kse(c, b, args):
    from .connectors import kse_russia as kse
    from .import_kse import build_row, match_group
    if args.kse_file:
        page, label = open(args.kse_file, encoding="utf-8").read(), f"fichier {args.kse_file}"
    else:
        r = c.get(kse.LIST_URL, headers={"User-Agent": "Mozilla/5.0 (DIAMS)", "X-Requested-With": "XMLHttpRequest"})
        r.raise_for_status()
        page, label = r.text, "liste KSE téléchargée"
    companies = kse.parse_list(page)
    if len(companies) < 3000:
        raise RuntimeError(f"liste KSE incomplète ({len(companies)})")
    groups, rows, seen = _roots_dicts(b), [], set()
    today = dt.date.today().isoformat()
    for co in companies:
        g = match_group(co, groups)
        if g and g["slug"] not in seen:
            seen.add(g["slug"])
            rows.append(build_row(g["slug"], co, today))
    return label, rows


def produce_sbti(c, b, args):
    from .connectors import sbti
    from .import_sbti import build_rows
    if not args.sbti_file:
        raise RuntimeError("export SBTi non fourni (--sbti-file)")
    return f"fichier {args.sbti_file}", build_rows(b.ents, sbti.parse_csv(args.sbti_file), dt.date.today().isoformat())


def produce_via_module(modname: str, extra: list[str]):
    """Lance un connecteur existant comme en écriture, mais toute écriture en base est bloquée :
    ses lignes sont capturées à la place (insert_evidence remplacé, requêtes autres que GET vers
    la base neutralisées). Sert à relire les sources que seul le connecteur sait lire."""
    def make(c, b, args):
        import contextlib
        import importlib
        import io
        import sys
        m = importlib.import_module(f".{modname}", "diams")
        captured: list[EvidenceRow] = []

        def fake_insert(rows, *a, **k):
            captured.extend(rows)
            return {"inserted": 0, "skipped": len(rows)}

        orig_send = httpx.Client.send

        def guard(self, request, *a, **k):
            if request.method != "GET" and config.SUPABASE_URL in str(request.url):
                return httpx.Response(200, json=[], request=request)
            return orig_send(self, request, *a, **k)

        old_ins, old_argv = m.insert_evidence, sys.argv
        m.insert_evidence, httpx.Client.send = fake_insert, guard
        sys.argv = [modname, "--apply", *extra]
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                m.main()
        except SystemExit as err:
            if err.code not in (None, 0):
                raise RuntimeError(f"{modname} : {err.code}")
        finally:
            m.insert_evidence, httpx.Client.send, sys.argv = old_ins, orig_send, old_argv
        return f"connecteur {modname} (source relue)", captured
    return make


PRODUCERS = {"EGAPRO": produce_egapro, "CDP": produce_cdp, "EU_TRANSPARENCY": produce_eu,
             "KSE_LEAVE_RUSSIA": produce_kse, "SBTI": produce_sbti,
             "FTI": produce_via_module("import_fti", []), "KNOWTHECHAIN": produce_via_module("import_ktc", []),
             "CCC": produce_via_module("import_fashion_checker", []),
             "FINANSOL": produce_via_module("import_finansol", []), "BBFAW": produce_via_module("import_bbfaw", []),
             "FUR_FREE": produce_via_module("import_fur_free", []), "B_LAB": produce_via_module("import_bcorp", [])}
# Lancés seulement sur demande (--sources) : relecture lourde (un rapport par groupe) ou quota serré.
ON_DEMAND = {"ESEF", "SEC_FILING", "INPI_SIRENE"}
# INPI_SIRENE : le connecteur ne produit que les preuves manquantes ; relu par l'annuaire (APE).


def _same(ev: dict, r: EvidenceRow) -> bool:
    def eq(a, x, nd):
        return (a is None and x is None) or (a is not None and x is not None and round(float(a), nd) == round(float(x), nd))
    return (eq(ev["normalized_value"], r.normalized_value, 3) and eq(ev["value_numeric"], r.value_numeric, 2)
            and (ev["value_boolean"] is None or r.value_boolean is None or ev["value_boolean"] == r.value_boolean))


def _val(x) -> str:
    v = x["value_numeric"] if isinstance(x, dict) else x.value_numeric
    n = x["normalized_value"] if isinstance(x, dict) else x.normalized_value
    return f"valeur {v if v is not None else '—'}, note {n if n is not None else '—'}"


def check_ape(c: httpx.Client, b: Base) -> tuple[list[dict], dict]:
    """Preuves « activité principale » (avis de situation Sirene) : le code APE cité est comparé
    à celui de l'annuaire officiel des entreprises (recherche-entreprises.api.gouv.fr), à jour."""
    import time
    sid = {s_id for s_id, s in b.src.items() if s["code"] == "INPI_SIRENE"}
    evs = [e for e in b.ev if e["source_id"] in sid]
    cache: dict[str, str | None] = {}
    reviews, ok, bad, ko = [], 0, [], 0
    for ev in evs:
        m = re.search(r"SIREN (\d{9})", ev["excerpt"] or "")
        a = re.search(r"\(APE\) (\d{2}\.\d{2}[A-Z])", ev["excerpt"] or "")
        if not (m and a):
            reviews.append(review(b, ev, "non_verifiable", "SIREN ou code APE introuvable dans l'extrait.", 0))
            ko += 1
            continue
        siren = m.group(1)
        if siren not in cache:
            time.sleep(0.2)
            r = c.get("https://recherche-entreprises.api.gouv.fr/search", params={"q": siren})
            if r.status_code in BLOCKING:
                raise RuntimeError(f"annuaire : HTTP {r.status_code}")
            hit = [x for x in r.json().get("results", []) if x.get("siren") == siren]
            cache[siren] = hit[0].get("activite_principale") if hit else None
        cur = cache[siren]
        if cur == a.group(1):
            ok += 1
            reviews.append(review(b, ev, "confirmee", f"Annuaire officiel des entreprises : SIREN {siren}, APE {cur} (identique).", 0))
        else:
            bad.append((b.by_id[ev["entity_id"]]["slug"], siren, a.group(1), cur))
            reviews.append(review(b, ev, "ecart", f"Annuaire officiel des entreprises : SIREN {siren}, APE {cur} (preuve : {a.group(1)}).", 0))
    print(f"✔ INPI_SIRENE (annuaire officiel) : {ok} confirmées, {len(bad)} écarts, {ko} non vérifiables")
    for x in bad:
        print(f"    écart {x[0]} : SIREN {x[1]}, preuve {x[2]}, annuaire {x[3]}")
    return reviews, {"confirmees": ok, "ecarts": bad}


def cmd_connecteurs(c: httpx.Client, b: Base, args) -> dict:
    reviews, report = [], {}
    if args.sources and "APE" in args.sources.split(","):
        r, rep = check_ape(c, b)
        reviews += r
        report["APE"] = rep
    wanted = set(args.sources.split(",")) if args.sources else set(PRODUCERS) - ON_DEMAND
    PRODUCERS.setdefault("ESEF", produce_via_module("import_esef", []))
    PRODUCERS.setdefault("SEC_FILING", produce_via_module("import_sec", []))
    for code, produce in PRODUCERS.items():
        if code not in wanted:
            continue
        try:
            label, rows = produce(c, b, args)
        except (httpx.HTTPError, RuntimeError, OSError) as err:
            print(f"✗ {code} : source indisponible ({err}) — rien n'est consigné pour cette source")
            report[code] = {"erreur": str(err)}
            continue
        expected = {(r.entity_slug, r.indicator_code): r for r in rows}
        sid = {s_id for s_id, s in b.src.items() if s["code"] == code}
        latest: dict[tuple, dict] = {}
        older = 0
        for ev in (e for e in b.ev if e["source_id"] in sid and not curated(e)):
            k = (b.by_id[ev["entity_id"]]["slug"], b.ind[ev["indicator_id"]])
            if k in latest:
                older += 1
                if ev["observed_on"] <= latest[k]["observed_on"]:
                    continue
            latest[k] = ev
        ok, ecarts, absentes = 0, [], []
        for k, ev in latest.items():
            r = expected.get(k)
            if r is None:
                absentes.append(k)
                reviews.append(review(b, ev, "ecart", f"Relecture du connecteur ({label}) : la preuve n'y figure plus.", 0))
            elif _same(ev, r):
                ok += 1
                reviews.append(review(b, ev, "confirmee", f"Relecture du connecteur ({label}) : même {_val(r)}.", 0))
            else:
                ecarts.append((k, _val(ev), _val(r)))
                reviews.append(review(b, ev, "ecart", f"Relecture du connecteur ({label}) : base {_val(ev)} ; source {_val(r)}.", 0))
        nouvelles = sorted(k for k in expected if k not in latest)
        report[code] = {"source": label, "confirmees": ok, "ecarts": ecarts, "absentes": absentes,
                        "nouvelles": nouvelles, "preuves_plus_anciennes_ignorees": older}
        print(f"✔ {code} ({label}) : {ok} confirmées, {len(ecarts)} écarts de valeur, {len(absentes)} absentes de la "
              f"source, {len(nouvelles)} nouvelles à importer ({older} preuves plus anciennes ignorées)")
        for k, a, z in ecarts[:15]:
            print(f"    écart {k[0]} · {k[1]} : base {a} → source {z}")
        for k in absentes[:15]:
            print(f"    absente {k[0]} · {k[1]}")
    return {"reviews": reviews, "report": report}


# --- Vague 6 : preuves d'appartenance marque → groupe ---------------------------------------

# Sites qui refusent les lectures automatiques (constaté lors des sessions précédentes) : on ne
# les sollicite pas, la preuve est notée « source_inaccessible ».
BLOCKED_HOSTS = {"www.nestle.com", "nestle.com", "www.unilever.com", "unilever.com", "www.suntory.com",
                 "www.pepsico.fr", "www.barilla.com"}


def cmd_proprietes(c: httpx.Client, b: Base, args) -> dict:
    from .verify_curated import _canon, document_text
    from .connectors.esef import report_text
    params = {"select": "id,entity_id,owner_id,source_url,excerpt"}
    if args.reprise:
        params["check_result"] = "in.(ecart,source_inaccessible)"
    rows = supabase_client.get_all(c, "entity_ownership_sources", params)
    if args.only:
        keep = {b.by_slug[s]["id"] for s in args.only if s in b.by_slug}
        rows = [r for r in rows if r["entity_id"] in keep or r["owner_id"] in keep]
    texts: dict[str, str | None] = {}
    blocked = set(BLOCKED_HOSTS)
    results: dict[str, list] = defaultdict(list)
    print(f"{len(rows)} preuves d'appartenance ({len({r['source_url'] for r in rows})} documents)")
    for n, r in enumerate(sorted(rows, key=lambda r: r["source_url"] or ""), 1):
        url = r["source_url"] or ""
        host = urlparse(url).netloc
        # Comme à l'import (import_brand_portfolio) : la citation probante est la DERNIÈRE « … »
        # de l'extrait, celle qui nomme la marque ; les guillemets précédents désignent un titre
        # de page ou citent une autre page (mentions légales).
        quotes = [_canon(q) for q in re.findall(r"«\s?(.+?)\s?»", r["excerpt"] or "")][-1:]
        if not quotes:
            results["non_verifiable"].append((r["id"], "pas de citation « … »"))
            continue
        if url not in texts:
            if host in blocked:
                texts[url] = None
            else:
                try:
                    texts[url] = _canon(report_text(url, c) if "filings.xbrl.org" in url else document_text(url, c))
                except httpx.HTTPStatusError as err:
                    texts[url] = None
                    if err.response.status_code in BLOCKING:
                        blocked.add(host)
                        print(f"  {host} répond {err.response.status_code} : site mis de côté")
                except (httpx.HTTPError, ValueError, OSError) as err:
                    texts[url] = None
                    print(f"  source illisible ({type(err).__name__}) : {url[:100]}")
        t = texts[url]
        if t is None:
            results["source_inaccessible"].append((r["id"], f"source inaccessible ({host})"))
            continue
        ok = all(q in t for q in quotes) or all(re.sub(r"\s", "", q) in re.sub(r"\s", "", t) for q in quotes)
        if ok:
            results["confirmee"].append((r["id"], "citation retrouvée mot pour mot"))
        else:
            missing = [q for q in quotes if q not in t]
            results["ecart"].append((r["id"], "citation introuvable : « " + missing[0][:200] + " »"))
            print(f"  [ÉCART] {b.by_id[r['entity_id']]['slug']} → {b.by_id[r['owner_id']]['slug']} : {url[:90]}")
        if n % 200 == 0:
            print(f"  … {n}/{len(rows)}")
    print("Bilan : " + ", ".join(f"{k} {len(v)}" for k, v in sorted(results.items())))
    if args.apply:
        h = {**supabase_client._headers(), "Prefer": "return=minimal"}
        today = dt.date.today().isoformat()
        for outcome, items in results.items():
            by_detail = defaultdict(list)
            for i, d in items:
                by_detail[d].append(i)
            for d, ids in by_detail.items():
                for k in range(0, len(ids), 150):
                    resp = c.patch(f"{config.SUPABASE_URL}/rest/v1/entity_ownership_sources",
                                   params={"id": f"in.({','.join(ids[k:k + 150])})"}, headers=h,
                                   json={"checked_on": today, "check_result": outcome, "check_detail": d})
                    resp.raise_for_status()
        print("Résultats notés sur les preuves d'appartenance.")
    return {"reviews": [], "report": {k: [(i, d) for i, d in v] for k, v in results.items() if k != "confirmee"}}


# --- Absences : cherché dans la liste complète, non trouvé ---------------------------------

def produce_hatvp(c, b, args):
    from .connectors import hatvp
    from .import_hatvp import build_rows
    if not args.hatvp_file:
        raise RuntimeError("répertoire HATVP non fourni (--hatvp-file)")
    orgs = hatvp.load_registry_file(args.hatvp_file)
    roots = [e for e in b.ents if not e.get("parent_id") and not e["is_brand"]]
    return f"fichier {args.hatvp_file}", build_rows(roots, orgs, dt.date.today().isoformat())


ABSENCE_SOURCES = {
    "CDP": (("ENV_CDP_CLIMATE", "WAT_CDP"), "absente de la liste publique complète des notes CDP 2025"),
    "SBTI": (("ENV_SBTI_VALIDATED",), "absente de l'export complet SBTi « Companies taking action » (08/10/2026)"),
    "KSE_LEAVE_RUSSIA": (("GEO_RUSSIA_EXIT",), "absente de la base « Leave Russia » du KSE Institute"),
    # Sans inscription, aucune dépense de lobbying n'est déclarée : l'absence vaut aussi pour les
    # dépenses (ajout du 16/10/2026).
    "EU_TRANSPARENCY": (("GEO_LOBBYING_TRANSP", "GEO_LOBBYING_SPEND"), "aucune inscription au registre de transparence de l'UE"),
    "HATVP": (("GEO_LOBBYING_TRANSP", "GEO_LOBBYING_SPEND"), "aucune inscription à son nom au répertoire des représentants d'intérêts (HATVP)"),
    # Listes complètes ajoutées le 15/10/2026 (trois niveaux : on cherche aussi chaque marque quand
    # la liste nomme des marques).
    "FTI": (("SUP_FTI_SCORE",), "absente de l'indice de transparence de la mode 2023 (Fashion Transparency Index, 250 marques)"),
    "KNOWTHECHAIN": (("SUP_KNOWTHECHAIN",), "absente des comparaisons KnowTheChain (alimentation et boissons, habillement, technologies)"),
    "BBFAW": (("ANI_BBFAW_TIER",), "absente du classement BBFAW (liste complète des entreprises évaluées)"),
    "FUR_FREE": (("ANI_FUR_FREE",), "absente de la liste des membres Fur Free Retailer (Fur Free Alliance)"),
    "CCC": (("SUP_LIVING_WAGE",), "absente du Fashion Checker (Clean Clothes Campaign)"),
    "FINANSOL": (("INV_SOLIDARITY_LABEL",), "aucun produit labellisé à son nom dans la liste officielle Finansol"),
    # Le classement ne publie que les dix plus gros pollueurs (ajout du 16/10/2026).
    "BFFP": (("PLA_POLLUTER",), "absente des dix plus gros pollueurs plastique de l'audit mondial des marques 2023 de Break Free From Plastic"),
}
# Listes qui nomment aussi des marques : l'absence est consignée pour les marques, pas seulement
# pour les groupes.
ABSENCE_MARQUES = {"FTI", "FUR_FREE", "CCC"}
# Contrôle du 15/10/2026 (noms bruts de chaque liste comparés aux entités non rapprochées) : la
# liste nomme une société LIÉE (filiale, homonyme d'un autre pays du même réseau) sans qu'on puisse
# attribuer la donnée. Ni preuve ni « absente » : on ne consigne rien.
ABSENCE_EXCLUSIONS = {
    "BBFAW": {"amazon": "« Amazon/Whole Foods Market » : Whole Foods, filiale, est évaluée",
              "aldi-france": "ALDI Nord et ALDI Sud sont évalués, pas Aldi France"},
    "FUR_FREE": {"aldi-france": "« ALDI », « ALDI NORD », « ALDI SUED » membres, sans précision pour la France"},
    "KNOWTHECHAIN": {"suntory-holdings": "« Suntory Beverage & Food Limited », filiale cotée, est évaluée",
                     "orangina-schweppes-france": "« Suntory Beverage & Food Limited », sa maison mère, est évaluée"},
    "FINANSOL": {"axa": "« Axa IM », société de gestion distincte, distribue des produits labellisés",
                 "credit-mutuel-arkea": "« Crédit Mutuel AM », autre entité du Crédit Mutuel"},
}


def produce_bffp(c, b, args):
    """Groupes nommés dans le classement de l'audit 2023 (lot 14, relu sur la page de Break Free From Plastic)."""
    import os
    from .import_curated import parse_file
    path = os.path.join(os.path.dirname(__file__), "..", "curated", "groupes_2026-10_lot14_bffp.csv")
    rows, _ = parse_file(path, "ai:relecture")
    return "audit mondial des marques 2023 de Break Free From Plastic", rows


def cmd_absences(c: httpx.Client, b: Base, args) -> dict:
    """Pour chaque groupe racine sans preuve sur un indicateur, consigne « non_trouvee » pour chaque
    source dont la liste complète a été relue sans y trouver le groupe. C'est ce qui permet d'écrire
    sur la fiche « aucune information : absent de … (date) » plutôt qu'un simple vide."""
    producers = {**PRODUCERS, "HATVP": produce_hatvp, "BFFP": produce_bffp}
    have = {(e["entity_id"], e["indicator_id"]) for e in b.ev}
    wave_of = {r: w for w, rs in b.waves().items() for r in rs}
    roots = [e for e in b.ents if not e.get("parent_id") and not e["is_brand"]]
    brands = [e for e in b.ents if e["is_brand"]]
    reviews, report = [], {}
    wanted = set(args.sources.split(",")) if args.sources else set(ABSENCE_SOURCES)
    # Absences déjà consignées (même entité, indicateur et source) : pas de doublon (16/10/2026).
    from . import supabase_client as _sc
    deja = {(r["entity_id"], r["indicator_id"], (r["detail"] or "").split(" (")[0])
            for r in _sc.get_all(c, "indicator_reviews", {"select": "entity_id,indicator_id,detail",
                                                          "outcome": "eq.non_trouvee", "reviewer": f"eq.{REVIEWER}"})}
    for code, (inds, phrase) in ABSENCE_SOURCES.items():
        if code not in wanted:
            continue
        try:
            label, rows = producers[code](c, b, args)
        except (httpx.HTTPError, RuntimeError, OSError) as err:
            print(f"✗ {code} : source indisponible ({err})")
            continue
        found = {r.entity_slug for r in rows}
        n = 0
        # Une marque dont un propriétaire (groupe, enseigne) figure dans la liste n'est pas dite
        # « absente » : la liste a évalué son propriétaire (l'indice de la mode note « Hermes
        # International », pas la marque ; Fur Free Retailer nomme Monoprix, pas Monoprix Bio).
        def ancetres(ent):
            out, cur = set(), ent
            for _ in range(20):
                if not cur.get("parent_id") or cur["parent_id"] not in b.by_id:
                    return out
                cur = b.by_id[cur["parent_id"]]
                out.add(cur["slug"])
            return out
        exclus = ABSENCE_EXCLUSIONS.get(code, {})
        cibles = roots + ([m for m in brands if not (ancetres(m) & found)] if code in ABSENCE_MARQUES else [])
        for e in [x for x in cibles if x["slug"] not in exclus]:
            if code == "HATVP" and not e.get("siren"):
                continue  # répertoire français : rapprochement par SIREN
            if e["slug"] in found:
                continue
            for ind in inds:
                iid = b.ind_id[ind]
                if (e["id"], iid) in have or (e["id"], iid, f"Cherché, non trouvé : {phrase}".split(" (")[0]) in deja:
                    continue
                reviews.append({"entity_id": e["id"], "indicator_id": iid, "evidence_id": None,
                                "outcome": "non_trouvee", "detail": f"Cherché, non trouvé : {phrase} ({label}, relu le "
                                f"{dt.date.today().strftime('%d/%m/%Y')}).", "source_url": None,
                                "reviewer": REVIEWER, "wave": wave_of.get(e["id"])})
                n += 1
        report[code] = {"source": label, "trouves": len(found), "non_trouves": n}
        print(f"✔ {code} ({label}) : {len(found)} groupes présents, {n} absences consignées")
    return {"reviews": reviews, "report": report}


# --- Preuves documentaires : citations mot pour mot -----------------------------------------

def cmd_citations(c: httpx.Client, b: Base, args) -> dict:
    from .verify_curated import FX_RE, check_esef_quote, document_text, ecb_annual_rate, verify_hatvp
    from .connectors.esef import report_text
    _, ids = b.perimeter(args.vague, args.only)
    evs = [e for e in b.ev if e["entity_id"] in ids and (curated(e) or (
        b.src[e["source_id"]]["code"] not in PRODUCERS and b.src[e["source_id"]]["code"] not in ON_DEMAND))]
    sirens = {e["slug"]: e.get("siren") for e in b.ents}
    texts: dict[str, str | None] = {}
    blocked: set[str] = set()
    reviews, counts, details = [], defaultdict(int), []
    print(f"{len(evs)} preuves documentaires à relire ({len({e['source_url'] for e in evs})} documents)")
    for n, ev in enumerate(sorted(evs, key=lambda e: e["source_url"] or ""), 1):
        r = b.row(ev)
        url = r.source_url or ""
        host = urlparse(url).netloc
        if r.source_code in RANKING_SOURCES:
            counts["non_verifiable"] += 1
            reviews.append(review(b, ev, "non_verifiable",
                                  f"Classement à édition publiée ({r.source_code}) : à relire contre son jeu de données.",
                                  args.vague or 0))
            continue
        if r.source_code == "HATVP":
            v = verify_hatvp(r, c, sirens)
        elif url and "«" in (r.excerpt or ""):
            if url not in texts:
                if host in blocked:
                    texts[url] = None
                else:
                    try:
                        texts[url] = report_text(url, c) if r.source_code == "ESEF" else document_text(url, c)
                    except httpx.HTTPStatusError as err:
                        texts[url] = None
                        if err.response.status_code in BLOCKING:
                            blocked.add(host)
                            print(f"  {host} répond {err.response.status_code} : site mis de côté pour cette passe")
                    except (httpx.HTTPError, ValueError, OSError) as err:
                        texts[url] = None
                        print(f"  source illisible ({type(err).__name__}) : {url[:110]}")
            if texts[url] is None:
                counts["source_inaccessible"] += 1
                reviews.append(review(b, ev, "source_inaccessible", "Source inaccessible au moment de la relecture.",
                                      args.vague or 0))
                continue
            rates = {}
            fx = FX_RE.search(r.excerpt or "")
            if fx:
                rates[(fx.group(3), fx.group(1))] = ecb_annual_rate(fx.group(3), fx.group(1), c)
            v = check_esef_quote(r, texts[url], rates=rates)
            if v.status != "OK":
                # Preuve approuvée jadis comme cas de jugement (définition voisine) : on regarde si
                # citation et valeur tiennent sans exiger les mots-clés de l'indicateur.
                loose = check_esef_quote(r, texts[url], ignore_keywords=True, rates=rates)
                if loose.status == "OK":
                    v = loose
                    v.details.append("mots-clés de l'indicateur non exigés (cas de jugement approuvé)")
        else:
            counts["non_verifiable"] += 1
            reviews.append(review(b, ev, "non_verifiable",
                                  f"Pas de citation « … » : valeur produite par le connecteur {r.source_code}, à relancer.",
                                  args.vague or 0))
            continue
        outcome = {"OK": "confirmee", "ÉCART": "ecart"}.get(v.status, "non_verifiable")
        counts[outcome] += 1
        reviews.append(review(b, ev, outcome, " ; ".join(v.details), args.vague or 0))
        if outcome != "confirmee":
            details.append({"entite": r.entity_slug, "indicateur": r.indicator_code, "source": r.source_code,
                            "url": url, "verdict": v.status, "details": v.details})
            print(f"  [{v.status}] {r.entity_slug} · {r.indicator_code} ({r.source_code})")
            for d in v.details:
                print(f"      {d}")
        if n % 50 == 0:
            print(f"  … {n}/{len(evs)}")
    print("Bilan : " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    return {"reviews": reviews, "report": {"bilan": dict(counts), "a_reprendre": details}}


# --- Obligations sans preuve ----------------------------------------------------------------

REPORT_SOURCES = {"ESEF", "AMF_BDIF", "ANNUAL_REPORT", "SEC_FILING", "AMF", "VIGILANCE_PLAN"}


def cmd_manques(c: httpx.Client, b: Base, args) -> dict:
    from .verify_curated import ESEF_KEYWORDS, document_text
    from .connectors.esef import report_text
    _, ids = b.perimeter(args.vague, args.only)
    have = {(e["entity_id"], e["indicator_id"]) for e in b.ev}
    by_regime = defaultdict(list)
    for x in b.ind_reg:
        by_regime[x["regime_id"]].append(x["indicator_id"])
    out = []
    texts: dict[str, str | None] = {}
    for er in b.ent_reg:
        if er["entity_id"] not in ids:
            continue
        for ind in by_regime[er["regime_id"]]:
            k = (er["entity_id"], ind)
            if k in have or k in b.exempt:
                continue
            ent = b.by_id[er["entity_id"]]
            code = b.ind[ind]
            reports = sorted({(b.src[e["source_id"]]["code"], e["source_url"]) for e in b.ev
                              if e["entity_id"] == er["entity_id"] and b.src[e["source_id"]]["code"] in REPORT_SOURCES
                              and e["source_url"]})
            cands = []
            for src_code, url in reports[:2]:
                if url not in texts:
                    try:
                        texts[url] = report_text(url, c) if src_code == "ESEF" else document_text(url, c)
                    except (httpx.HTTPError, ValueError, OSError):
                        texts[url] = None
                t = texts[url]
                if not t:
                    continue
                flat = re.sub(r"\s+", " ", t)
                for kw in ESEF_KEYWORDS.get(code, [])[:1]:
                    for m in list(re.finditer(kw, flat, re.I))[:4]:
                        cands.append({"url": url, "passage": flat[max(0, m.start() - 220): m.end() + 260]})
            out.append({"entite": ent["slug"], "indicateur": code, "regime": b.regimes[er["regime_id"]]["name"],
                        "rapports": [u for _, u in reports], "passages": cands})
            print(f"• {ent['slug']} · {code} ({b.regimes[er['regime_id']]['name']}) : {len(reports)} rapport(s), "
                  f"{len(cands)} passage(s) candidat(s)")
    return {"reviews": [], "report": {"manques": out}}


def main() -> None:
    ap = argparse.ArgumentParser(description="Relecture complète des preuves (journal indicator_reviews).")
    ap.add_argument("commande", choices=["connecteurs", "citations", "manques", "absences", "proprietes"])
    ap.add_argument("--vague", type=int)
    ap.add_argument("--only", help="groupes racines, séparés par des virgules")
    ap.add_argument("--apply", action="store_true", help="consigne le résultat dans le journal")
    ap.add_argument("--rapport", help="fichier JSON du détail")
    ap.add_argument("--ani-cache", help="cache des avis Sirene (import_ani_ape)")
    ap.add_argument("--hatvp-file", help="répertoire HATVP (open data AGORA, JSON)")
    ap.add_argument("--reprise", action="store_true", help="proprietes : ne relire que les écarts et sources inaccessibles")
    ap.add_argument("--sources", help="connecteurs à relire (EGAPRO,CDP,EU_TRANSPARENCY,KSE_LEAVE_RUSSIA,SBTI)")
    for k in ("eu", "kse", "cdp", "sbti", "egapro"):
        ap.add_argument(f"--{k}-file")
    args = ap.parse_args()
    args.only = [s.strip() for s in args.only.split(",")] if args.only else None
    if args.commande not in ("connecteurs", "absences", "proprietes") and not (args.vague or args.only):
        raise SystemExit("--vague ou --only requis")
    config.require_supabase()
    with httpx.Client(timeout=300, follow_redirects=True) as c:
        b = Base(c)
        res = {"connecteurs": cmd_connecteurs, "citations": cmd_citations, "manques": cmd_manques,
               "absences": cmd_absences, "proprietes": cmd_proprietes}[args.commande](c, b, args)
        if args.rapport:
            with open(args.rapport, "w", encoding="utf-8") as fh:
                json.dump(res["report"], fh, ensure_ascii=False, indent=1, default=str)
        if args.apply and res["reviews"]:
            print(f"Journal de relecture : {write_reviews(c, res['reviews'])} ligne(s) consignée(s)")
        elif res["reviews"]:
            print(f"(contrôle : {len(res['reviews'])} ligne(s) seraient consignées ; relancer avec --apply)")


if __name__ == "__main__":
    main()
