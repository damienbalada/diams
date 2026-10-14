"""Aide à la lecture des états de durabilité (ESRS) — ne crée AUCUNE preuve.

Repère, dans un rapport annuel (ESEF xhtml ou PDF), les passages candidats pour
chaque donnée obligatoire suivie par DIAMS. Un compilateur choisit la bonne
citation et l'écrit dans un CSV de `curated/` ; `verify_curated` contrôle
ensuite qu'elle figure mot pour mot dans le rapport et contient la valeur.

Usage :
    python -m diams.esrs_candidates --slug loreal                # dernier dépôt ESEF (par LEI)
    python -m diams.esrs_candidates --url https://…/rapport.pdf --only GOV_BOARD_GENDER
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re

import httpx

# Motifs FR + EN. Large à dessein : on préfère trop de candidats à une donnée ratée.
PATTERNS: dict[str, list[str]] = {
    "GOV_BOARD_GENDER": [
        r"(?:conseil|board)[^.]{0,200}\d{1,2}(?:[,.]\d+)?\s?% (?:de femmes|d.administratrices|women|female)",
        r"\d{1,2}(?:[,.]\d+)?\s?% (?:de femmes|d.administratrices|women|female)[^.]{0,120}(?:conseil|board)",
        r"(?:femmes|women)[^.]{0,60}(?:conseil|board)[^.]{0,80}\d{1,2}(?:[,.]\d+)?\s?%",
    ],
    "GOV_BOARD_INDEP": [
        r"(?:qualifi[ée]s? d.ind[ée]pendants?|taux d.ind[ée]pendance|administrateurs ind[ée]pendants|independent (?:directors|members))[^.]{0,140}\d{1,3}(?:[,.]\d+)?\s?%",
        r"\d{1,3}(?:[,.]\d+)?\s?% (?:d.administrateurs ind[ée]pendants|d.ind[ée]pendants|independent)",
    ],
    "LAB_GENDER_PAYGAP": [
        r"[ée]cart de r[ée]mun[ée]ration (?:entre les )?(?:femmes et (?:les )?hommes|hommes et (?:les )?femmes|F/H)[^.]{0,300}\d+(?:,\d+)?\s?%",
        r"(?:gender pay gap|pay gap)[^.]{0,300}\d+(?:\.\d+)?\s?%",
    ],
    "LAB_CEO_PAY_RATIO": [
        r"ratio (?:de|entre) (?:la )?r[ée]mun[ée]ration (?:annuelle )?(?:totale|la plus)[^.]{0,400}",
        r"annual total remuneration ratio[^.]{0,300}",
    ],
    "ENV_SCOPE3_DISCLOSED": [
        r"[ÉE]missions (?:totales|brutes)[^.]{0,40}(?:Scope|p[ée]rim[èe]tre|champ d.application) 3[^.]{0,100}",
        r"(?:Total|Gross) Scope 3 (?:GHG )?emissions[^.]{0,100}",
    ],
    "ENV_GHG_INTENSITY": [
        r"Intensit[ée] (?:des |de )?(?:[ée]missions de )?GES[^.]{0,300}",
        r"GHG intensity[^.]{0,300}",
    ],
    "TAX_EFFECTIVE_RATE": [
        r"taux (?:effectif|r[ée]el|moyen) d.imp(?:[ôo]t|osition)[^.]{0,200}",
        r"effective tax rate[^.]{0,200}",
    ],
    "SUP_VIGILANCE_PLAN": [
        r"Plan de vigilance[^.]{0,400}",
    ],
}

# Sommaires et tables de concordance : renvois de pages, pas des données.
_TOC = re.compile(r"\s\d{1,4}\s*[-–]\s*\d{1,4}\b|\.{4,}|\bp\.\s?\d")


def _cache_path(url: str, cache: str) -> str:
    return os.path.join(cache, hashlib.sha256(url.encode()).hexdigest()[:16] + ".txt")


def fetch_text(url: str, cache: str | None = None) -> str:
    from .verify_curated import document_text
    if cache:
        p = _cache_path(url, cache)
        if os.path.exists(p):
            return open(p, encoding="utf-8").read()
    with httpx.Client(timeout=300) as c:
        text = re.sub(r"\s+", " ", document_text(url, c))
    if cache:
        os.makedirs(cache, exist_ok=True)
        open(_cache_path(url, cache), "w", encoding="utf-8").write(text)
    return text


def fetch_lines(url: str, cache: str | None = None) -> list[str]:
    """Le rapport découpé en lignes (paragraphes, lignes et cellules de tableau) :
    garde la structure des tableaux que le texte aplati perd."""
    import html as _html
    raw_path = _cache_path(url, cache) + ".html" if cache else None
    if raw_path and os.path.exists(raw_path):
        raw = open(raw_path, encoding="utf-8").read()
    else:
        with httpx.Client(timeout=300) as c:
            r = c.get(url, timeout=300, follow_redirects=True)
            r.raise_for_status()
            raw = r.text
        if raw_path:
            os.makedirs(cache, exist_ok=True)
            open(raw_path, "w", encoding="utf-8").write(raw)
    raw = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S)
    raw = re.sub(r"</t[dh]>", " ¦ ", raw)
    raw = re.sub(r"</(?:tr|p|div|li|h\d)>|<br\s*/?>", "\n", raw)
    text = _html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return [ln for ln in (re.sub(r"[ \t\xa0]+", " ", x).strip() for x in text.split("\n")) if ln]


def candidates(text: str, code: str, limit: int = 8, context: int = 160) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for pat in PATTERNS[code]:
        for m in re.finditer(pat, text, re.I):
            snippet = text[max(0, m.start() - context): m.end() + context]
            if _TOC.search(text[m.start(): m.end() + 60]):
                continue
            key = text[m.start(): m.start() + 80]
            if key in seen:
                continue
            seen.add(key)
            out.append(snippet)
            if len(out) >= limit:
                return out
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Passages candidats ESRS (aucune écriture).")
    ap.add_argument("--slug", help="entité DIAMS : dernier dépôt ESEF trouvé par son LEI")
    ap.add_argument("--url", help="rapport à lire (xhtml ESEF ou PDF)")
    ap.add_argument("--only", help="codes d'indicateurs séparés par des virgules")
    ap.add_argument("--limit", type=int, default=6)
    ap.add_argument("--cache", default=os.environ.get("DIAMS_CACHE"))
    ap.add_argument("--grep", action="append", help="motif libre (répétable), au lieu des motifs par indicateur")
    ap.add_argument("--context", type=int, default=160)
    ap.add_argument("--lines", type=int, help="avec --grep : affiche N lignes suivantes (structure des tableaux)")
    args = ap.parse_args()

    url = args.url
    if args.slug and not url:
        from . import config
        from .connectors import esef
        h = {"apikey": config.SUPABASE_SERVICE_ROLE_KEY, "Authorization": f"Bearer {config.SUPABASE_SERVICE_ROLE_KEY}"}
        with httpx.Client(timeout=120) as c:
            ent = c.get(f"{config.SUPABASE_URL}/rest/v1/entities", params={"select": "lei,country", "slug": f"eq.{args.slug}"},
                        headers=h).json()
            f = (esef.latest_filing(ent[0]["lei"], c, prefer_country=ent[0]["country"])
                 if ent and ent[0]["lei"] else None)
        if not f or not f.report_url:
            raise SystemExit(f"Aucun dépôt ESEF récent pour {args.slug}.")
        url = f.report_url
        print(f"# {args.slug} — exercice clos le {f.period_end}, déposé le {f.date_added}\n# {url}")
    if not url:
        raise SystemExit("--slug ou --url requis")

    if args.grep and args.lines is not None:
        lines = fetch_lines(url, args.cache)
        for pat in args.grep:
            print(f"\n=== /{pat}/ (lignes)")
            n = 0
            for i, ln in enumerate(lines):
                if re.search(pat, ln, re.I):
                    print("  ┌ " + "\n  │ ".join(x[:300] for x in lines[i: i + 1 + args.lines]))
                    n += 1
                    if n >= args.limit:
                        break
        return
    text = fetch_text(url, args.cache)
    if args.grep:
        for pat in args.grep:
            print(f"\n=== /{pat}/")
            for i, m in enumerate(re.finditer(pat, text, re.I)):
                if i >= args.limit:
                    break
                print(f"  · …{text[max(0, m.start() - args.context): m.end() + args.context]}…")
        return
    codes = args.only.split(",") if args.only else list(PATTERNS)
    for code in codes:
        print(f"\n=== {code}")
        for s in candidates(text, code, args.limit):
            print(f"  · …{s}…")


if __name__ == "__main__":
    main()
