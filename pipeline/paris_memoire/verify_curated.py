"""Vérification DÉTERMINISTE des preuves curées contre leur source primaire.

Une preuve compilée par une IA (reviewer `ai:…`) attend une validation. Quand la
source primaire est lisible par machine, cette validation peut être mécanique :
le script relit la source, recalcule chaque chiffre et le compare à la preuve.
Mêmes entrées → même verdict, et le détail de chaque comparaison est affiché :
c'est la garantie qui fonde la publication automatique des connecteurs
(REVIEW_MODEL.md). Ce que la machine ne peut pas trancher reste humain.

Verdicts :
  OK              tout concorde avec la source → approuvable (`auto:verify_curated`)
  ÉCART           la source dit autre chose → reste en revue, écart affiché
  JUGEMENT        la source ne vise pas exactement l'entité (attribution) → humain
  NON VÉRIFIABLE  aucun vérificateur pour cette source → humain

Usage :
    python -m paris_memoire.verify_curated --file curated/banques_2026-10_lot1.csv --bocc-pdf tables.pdf
    ... --apply     # approuve les seules preuves OK encore en attente
"""
from __future__ import annotations

import argparse
import csv
import io
import html
import re
import unicodedata
from dataclasses import dataclass, field

import httpx

from . import config, supabase_client
from .import_curated import parse_file

# --- BOCC : tableaux « Oil & Gas Expansion » ---------------------------------
BOCC_SECTIONS = {"Upstream": "amont", "Midstream": "transport/GNL", "Gas Power": "centrales à gaz"}
# Libellé exact de la ligne BOCC pour chaque entité. `attribution` : le libellé
# désigne un périmètre plus large que l'entité notée → décision humaine.
BOCC_LABELS = {
    "societe-generale": ("societe generale", False),
    "credit-agricole": ("credit agricole", False),
    "bpce": ("groupe bpce", False),
    "bnp-paribas": ("bnp paribas", False),
    "la-banque-postale": ("la banque postale", False),
    "credit-mutuel-alliance-federale": ("credit mutuel", True),
}
_ROW = re.compile(
    r"(?:^|\s)(\d{1,2})\s+([A-Za-z&'.\- ]+?)\s+"
    r"\$(\d+\.\d)\s+\$(\d+\.\d)\s+\$(\d+\.\d)\s+\$(\d+\.\d)\s+\$(\d+\.\d)\s+\$(\d+\.\d)"
)


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()


def parse_bocc_text(text: str) -> dict[str, dict[str, list[float]]]:
    """Texte des tableaux → {section: {libellé normalisé: [2021..2025, total]}}."""
    out: dict[str, dict[str, list[float]]] = {}
    for chunk in re.split(r"Financing to ", text)[1:]:
        title = chunk.split("Companies", 1)[0]
        section = next((k for k in BOCC_SECTIONS if k.lower() in title.lower()), None)
        if section is None:
            continue
        flat = re.sub(r"\s+", " ", _norm(chunk))
        rows = out.setdefault(section, {})
        for m in _ROW.finditer(flat):
            rows.setdefault(m.group(2).strip(), [float(x) for x in m.groups()[2:]])
    return out


def parse_bocc_pdf(path: str) -> dict[str, dict[str, list[float]]]:
    import pypdf
    reader = pypdf.PdfReader(path)
    return parse_bocc_text("\n".join(p.extract_text() or "" for p in reader.pages))


def _fr(x: float) -> str:
    return f"{x:.1f}".replace(".", ",")


@dataclass
class Verdict:
    status: str
    details: list[str] = field(default_factory=list)


def verify_bocc(row, tables: dict[str, dict[str, list[float]]]) -> Verdict:
    label, attribution = BOCC_LABELS.get(row.entity_slug, (None, False))
    if label is None:
        return Verdict("NON VÉRIFIABLE", [f"pas de libellé BOCC connu pour {row.entity_slug}"])
    details, total, ok = [], 0.0, True
    for section, fr_name in BOCC_SECTIONS.items():
        vals = tables.get(section, {}).get(label)
        if vals is None:
            return Verdict("ÉCART", [f"ligne « {label} » introuvable dans le tableau {section}"])
        v2025 = vals[4]
        total += v2025
        claimed = f"{fr_name} {_fr(v2025)}"
        found = claimed in (row.excerpt or "")
        ok &= found
        details.append(f"{section} 2025 = ${v2025:.1f} → extrait « {claimed} » {'✓' if found else '✗ ABSENT'}")
    total = round(total, 1)
    total_ok = row.value_numeric is not None and abs(row.value_numeric - total) < 1e-9
    ok &= total_ok
    details.append(f"total recalculé {total:.1f} vs valeur {row.value_numeric} {'✓' if total_ok else '✗'}")
    if not ok:
        return Verdict("ÉCART", details)
    if attribution:
        details.append(f"la ligne « {label} » couvre un périmètre plus large que {row.entity_slug} : attribution à trancher")
        return Verdict("JUGEMENT", details)
    return Verdict("OK", details)


# --- HATVP : répertoire des représentants d'intérêts --------------------------
def _range(s: str) -> tuple[int, int] | None:
    nums = [int(n.replace(" ", "").replace(" ", "")) for n in re.findall(r"\d[\d  ]*\d", s)]
    return (nums[0], nums[1]) if len(nums) >= 2 else None


def check_hatvp(row, record: dict, entity_siren: str | None) -> Verdict:
    pub = record.get("publicationCourante") or {}
    siren = str(pub.get("identifiantNational") or "")
    details = [f"fiche : {pub.get('denomination')} (SIREN {siren}), inscrite le {str(pub.get('datePremierePublication'))[:10]}"]
    if not siren or not pub.get("datePremierePublication"):
        return Verdict("ÉCART", details + ["fiche vide : organisation non inscrite"])
    ok = True
    excerpt = row.excerpt or ""
    m = re.search(r"(\d{2}/\d{2}/\d{4})", excerpt)
    if m:
        same = m.group(1) == str(pub["datePremierePublication"])[:10]
        ok &= same
        details.append(f"date citée {m.group(1)} {'✓' if same else '✗'}")
    exercises = {str(e["publicationCourante"].get("dateDebut", ""))[-4:]: e["publicationCourante"]
                 for e in record.get("exercices", []) if e.get("publicationCourante")}
    for year, rng in re.findall(r"(\d{4})\)? ?: ([\d  ]+ à [\d  ]+ €)", excerpt):
        declared = (exercises.get(year) or {}).get("montantDepense") or ""
        same = _range(declared) == _range(rng) and _range(rng) is not None
        ok &= same
        details.append(f"dépenses {year} citées « {rng} » vs déclarées « {declared or '—'} » {'✓' if same else '✗'}")
    na = re.search(r"aucune activité déclarée pour (\d{4}) et (\d{4})", excerpt)
    if na:
        for y in na.groups():
            e = exercises.get(y) or {}
            none = bool(e.get("noActivite")) or int(e.get("nombreActivite") or 0) == 0
            ok &= none
            details.append(f"aucune activité en {y} {'✓' if none else '✗'}")
    if not ok:
        return Verdict("ÉCART", details)
    if entity_siren and siren != entity_siren:
        details.append(f"fiche d'une autre entité (SIREN {siren} ≠ {entity_siren}) : attribution à trancher")
        return Verdict("JUGEMENT", details)
    return Verdict("OK", details)


def verify_hatvp(row, client: httpx.Client, sirens: dict[str, str | None]) -> Verdict:
    m = re.search(r"organisation=(\d{9})", row.source_url or "")
    if not m:
        return Verdict("NON VÉRIFIABLE", ["URL HATVP sans SIREN"])
    r = client.get(f"https://www.hatvp.fr/agora/{m.group(1)}.json", timeout=60)
    if r.status_code != 200:
        return Verdict("ÉCART", [f"données HATVP indisponibles (HTTP {r.status_code})"])
    return check_hatvp(row, r.json(), sirens.get(row.entity_slug))


# --- ESEF : citation verbatim du rapport financier annuel ----------------------
# Mots qui doivent figurer dans la citation pour qu'elle porte bien sur l'indicateur.
ESEF_KEYWORDS = {
    "INV_FOSSIL_FINANCING": [r"fossile"],
    "INV_RESPONSIBLE_POLICY": [r"exclu"],
    "LAB_GENDER_PAYGAP": [r"[ée]cart|gap", r"r[ée]mun[ée]ration|salari|pay", r"femmes?|hommes?|genres?|gender|women"],
    # « ratio de rémunération annuelle totale » : intitulé ESRS S1-16, défini par rapport à la médiane.
    "LAB_CEO_PAY_RATIO": [r"ratio", r"m[ée]dian|r[ée]mun[ée]ration annuelle totale|annual total remuneration|total remuneration ratio"],
    "GOV_BOARD_GENDER": [r"femmes|administratrices|f[ée]minisation|women|female", r"conseil|board|director"],
    "GOV_BOARD_INDEP": [r"ind[ée]pendan|independen"],
    "ENV_SCOPE3_DISCLOSED": [r"scope 3"],
    "ENV_GHG_INTENSITY": [r"intensit", r"/\s?M€|revenu net|produit net|chiffre d.affaires|millions d.euros|net revenue"],
    # Plan de vigilance « complet » (barème de l'indicateur) : cartographie ET suivi,
    # lus dans le plan lui-même (C. com. L225-102-4 : cinq mesures).
    "SUP_VIGILANCE_PLAN": [r"vigilance", r"cartographie|analyse des risques", r"suivi|contr[ôo]le du respect|compte rendu"],
    # Taxonomie verte UE (art. 8) : part des CapEx ALIGNÉS (pas seulement éligibles).
    "ENV_TAXONOMY_CAPEX": [r"taxonom", r"capex|capital expenditure", r"align"],
    # Audit de marques Break Free From Plastic : classement des pollueurs.
    "PLA_POLLUTER": [r"polluter|pollueur"],
    # Recours à des matières animales (plafond du pilier animal).
    "ANI_EXPLOITATION": [r"cuirs?|peaux?|fourrures?|crocodil|leather|skins?|fur\b"],
    "ANI_FUR_FREE": [r"fourrure|fur\b"],
    "GEO_LOBBYING_ALIGN": [r"InfluenceMap|Climate Policy Engagement"],
}


def _canon(s: str) -> str:
    s = s.replace("’", "'").replace(" ", " ").replace(" ", " ")
    # Signe moins typographique : « –9.9 % » est la valeur -9,9.
    s = s.replace("\u2013", "-").replace("\u2212", "-").replace("\u2011", "-")
    return re.sub(r"\s+", " ", s).strip()


def _value_variants(v: float) -> list[str]:
    out = {f"{v:.2f}".replace(".", ","), f"{v:.1f}".replace(".", ",")}
    out |= {f"{v:.2f}", f"{v:.1f}"}                      # notation anglaise : 17.4
    if float(v).is_integer():
        out |= {f"{int(v)}", f"{int(v):,}"}             # 1980 et 1,980
    return list(out)


_NUM_WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
    "seventeen eighteen nineteen twenty".split())}
_NUM_WORDS.update({w: i for i, w in enumerate(
    "zéro un deux trois quatre cinq six sept huit neuf dix onze douze treize quatorze quinze seize dix-sept "
    "dix-huit dix-neuf vingt".split())})
_NUM = r"\d{1,2}|" + "|".join(sorted(_NUM_WORDS, key=len, reverse=True))
_COUNT = re.compile(rf"\b({_NUM})\b(?:\s+\w+){{0,3}}?\s+(?:of|sur)\s+(?:our\s+|the\s+|its\s+)?({_NUM})\b", re.I)


def _count_ratio_matches(value: float, quote: str) -> bool:
    """« 11 of 12 director nominees », « six femmes Administratrices sur 14 » :
    le pourcentage déclaré doit être le rapport des effectifs cités."""
    for m in _COUNT.finditer(quote):
        a, b = (int(x) if x.isdigit() else _NUM_WORDS.get(x.lower()) for x in m.groups())
        if a is not None and b and a <= b and abs(round(100 * a / b, 1) - value) <= 0.05:
            return True
    return False


# Valeur publiée dans une autre devise, convertie en euros au taux annuel moyen de
# la BCE ; la conversion est écrite dans l'extrait et recalculée ici :
# « … taux de change annuel moyen 2025 de la BCE (1 € = 11,0663 SEK) : 30 × 11,0663 = 332 ».
FX_RE = re.compile(r"taux de change annuel moyen (\d{4}) de la BCE \(1 € = ([\d,]+) ([A-Z]{3})\) : "
                   r"([\d,]+) × ([\d,]+) = ([\d,]+)")


def _num(s: str) -> float:
    return float(s.replace(",", "."))


def ecb_annual_rate(currency: str, year: str, client: httpx.Client) -> float:
    """Taux annuel moyen BCE (unités de devise pour 1 €), série EXR.A.<CUR>.EUR.SP00.A."""
    r = client.get(f"https://data-api.ecb.europa.eu/service/data/EXR/A.{currency}.EUR.SP00.A",
                   params={"startPeriod": year, "endPeriod": year, "format": "csvdata"}, timeout=60)
    r.raise_for_status()
    rows = list(csv.DictReader(io.StringIO(r.text)))
    return float(rows[0]["OBS_VALUE"])


def check_fx(row, quote: str, rates: dict[tuple[str, str], float]) -> tuple[bool, list[str], float | None]:
    """Contrôle d'une conversion déclarée : taux = celui de la BCE, montant d'origine
    cité, produit exact à l'arrondi près, résultat = valeur. Renvoie le montant
    d'origine, à chercher dans la citation à la place de la valeur."""
    m = FX_RE.search(row.excerpt or "")
    if not m:
        return True, [], None
    year, rate_s, cur, a_s, rate2_s, c_s = m.groups()
    rate, a, c = _num(rate_s), _num(a_s), _num(c_s)
    ecb = rates.get((cur, year))
    rate_ok = ecb is not None and abs(round(ecb, 4) - rate) < 1e-9 and rate_s == rate2_s
    calc_ok = abs(a * rate - c) <= 0.5 and row.value_numeric is not None and abs(c - row.value_numeric) < 1e-9
    return rate_ok and calc_ok, [
        f"taux {cur} {year} de la BCE {ecb if ecb is not None else 'introuvable'} = taux déclaré {rate_s} {'✓' if rate_ok else '✗'}",
        f"conversion {a_s} × {rate_s} = {a * rate:.2f} ≈ {c_s} = valeur {'✓' if calc_ok else '✗'}",
    ], a


def check_esef_quote(row, report_text: str, ignore_keywords: bool = False,
                     rates: dict[tuple[str, str], float] | None = None) -> Verdict:
    # Une ou plusieurs citations « … » : chacune doit figurer mot pour mot ; mots
    # de l'indicateur et valeur sont cherchés dans leur ensemble.
    quotes = [_canon(q) for q in re.findall(r"«\s?(.+?)\s?»", row.excerpt or "")]
    if not quotes:
        return Verdict("NON VÉRIFIABLE", ["pas de citation « … » dans l'extrait"])
    canon_report = _canon(report_text)
    found = all(q in canon_report for q in quotes)
    label = "citation retrouvée" if len(quotes) == 1 else f"{len(quotes)} citations retrouvées"
    details = [f"{label} mot pour mot dans le rapport {'✓' if found else '✗'}"]
    quote = " … ".join(quotes)
    ok = found
    for kw in ([] if ignore_keywords else ESEF_KEYWORDS.get(row.indicator_code, [])):
        hit = re.search(kw, quote, re.I) is not None
        ok &= hit
        details.append(f"la citation porte sur l'indicateur (« {kw} ») {'✓' if hit else '✗'}")
    # Valeur convertie d'une autre devise : la conversion est contrôlée, puis c'est
    # le montant d'origine qu'on cherche dans la citation.
    fx_ok, fx_details, fx_source = check_fx(row, quote, rates or {})
    ok &= fx_ok
    details += fx_details
    if row.value_numeric is not None and not ignore_keywords:
        flat = re.sub(r"(?<=\d)\s(?=\d{3}(?!\d))", "", quote)  # espaces de milliers seulement
        target = fx_source if fx_source is not None else row.value_numeric
        variants = _value_variants(target)
        # Écart « en faveur des femmes » : publié en valeur absolue, compté négatif ;
        # ou en notation comptable entre parenthèses, « (8,0) % ».
        if row.value_numeric < 0 and re.search(
                r"in favou?r of women|en faveur des femmes|higher for (female|women)"
                r"|sup[ée]rieure? pour les (salari[ée]es )?femmes", quote, re.I):
            variants += _value_variants(-row.value_numeric)
        if row.value_numeric < 0:
            variants += [f"({c})" for c in _value_variants(-row.value_numeric)]
        # Le signe compte : 9,9 ne correspond pas à « -9,9 » ; un tiret après une
        # lettre n'est pas un signe (« 1-to-51 »).
        # Une valeur positive collée à une parenthèse ouvrante (« (8,0) % ») est
        # une négative en notation comptable : elle ne la confirme pas.
        paren = "" if row.value_numeric < 0 else r"(?<!\()"
        pats = [rf"(?<![\d,])(?<!(?<![A-Za-z])-){paren}{re.escape(c)}(?![\d])" for c in variants]
        hit = any(re.search(pt, flat) for pt in pats)
        # Colonnes voisines de 3 chiffres (« 345 352 ») : fusionnées à tort en un
        # seul nombre ; on accepte la valeur lue comme nombre isolé, la lecture des
        # colonnes étant écrite dans l'extrait.
        col = not hit and any(re.search(rf"(?:^|\s){pt}(?=\s|$)", quote) for pt in pats)
        cnt = (not hit and not col and row.indicator_code in ("GOV_BOARD_INDEP", "GOV_BOARD_GENDER")
               and _count_ratio_matches(row.value_numeric, quote))
        ok &= hit or col or cnt
        details.append(f"valeur {target} présente dans la citation "
                       f"{'✓' if hit else '✓ (colonne isolée)' if col else '✓ (rapport des effectifs cités)' if cnt else '✗'}")
    elif row.value_boolean is not None:
        details.append("indicateur oui/non : la présence de la citation suffit")
    return Verdict("OK" if ok else "ÉCART", details)


def document_text(url: str, client: httpx.Client) -> str:
    """Texte d'un document public (page web ou PDF), pour vérifier une citation."""
    from .connectors.sec import UA
    # Identifiant déclaré : certains sites refusent celui, par défaut, de la
    # bibliothèque HTTP ; la SEC exige le sien.
    ua = UA if "sec.gov" in url else {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)"}
    r = client.get(url, timeout=300, follow_redirects=True, headers=ua)
    r.raise_for_status()
    if url.lower().split("?")[0].endswith(".zip") or "zip" in r.headers.get("content-type", ""):
        # Paquet ESEF (dépôt AMF) : le rapport est le plus gros .xhtml du dossier reports/.
        import io
        import zipfile
        z = zipfile.ZipFile(io.BytesIO(r.content))
        name = max((i for i in z.infolist() if i.filename.lower().endswith((".xhtml", ".html"))),
                   key=lambda i: i.file_size).filename
        raw = z.read(name).decode("utf-8", errors="replace")
        return re.sub(r"\s+", " ", html.unescape(re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", raw, flags=re.S)))
    if url.lower().split("?")[0].endswith(".pdf") or "pdf" in r.headers.get("content-type", ""):
        import io
        import logging

        import pypdf
        logging.getLogger("pypdf").setLevel(logging.ERROR)
        return "\n".join(p.extract_text() or "" for p in pypdf.PdfReader(io.BytesIO(r.content)).pages)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", r.text, flags=re.S)))


def finalize(v: Verdict, note: str, tier: str | None) -> Verdict:
    """Seul un OK sur source de tier 1-2, sans note de jugement, est approuvable."""
    from .load import AUTO_PUBLISH_TIERS
    if v.status == "OK" and note:
        return Verdict("JUGEMENT", v.details + [f"signalé à la compilation : {note}"])
    # Même vérifiée, une source de tier 3 / crowd passe par un humain (REVIEW_MODEL).
    if v.status == "OK" and tier not in AUTO_PUBLISH_TIERS:
        return Verdict("JUGEMENT", v.details + [f"source de tier « {tier} » : validation humaine requise"])
    return v


# --- Application ---------------------------------------------------------------
def approve(rows) -> int:
    h = {"apikey": config.SUPABASE_SERVICE_ROLE_KEY, "Authorization": f"Bearer {config.SUPABASE_SERVICE_ROLE_KEY}",
         "Content-Type": "application/json"}
    base = f"{config.SUPABASE_URL}/rest/v1"
    n = 0
    with httpx.Client(timeout=60) as c:
        ids = lambda t, k: {x[k]: x["id"] for x in c.get(f"{base}/{t}", params={"select": f"id,{k}"}, headers=h).json()}  # noqa: E731
        ents, inds, srcs = ids("entities", "slug"), ids("indicators", "code"), ids("sources", "code")
        for r in rows:
            resp = c.patch(f"{base}/evidence", headers={**h, "Prefer": "return=representation"},
                           params={"entity_id": f"eq.{ents[r.entity_slug]}", "indicator_id": f"eq.{inds[r.indicator_code]}",
                                   "source_id": f"eq.{srcs[r.source_code]}", "observed_on": f"eq.{r.observed_on}",
                                   "review_status": "eq.pending"},
                           json={"review_status": "approved", "reviewer": "auto:verify_curated"})
            resp.raise_for_status()
            n += len(resp.json())
    return n


def main() -> None:
    parser = argparse.ArgumentParser(description="Vérifie des preuves curées contre leur source primaire.")
    parser.add_argument("--file", required=True)
    parser.add_argument("--bocc-pdf", help="PDF des tableaux BOCC (sector-tables)")
    parser.add_argument("--apply", action="store_true", help="approuve les preuves OK encore en attente")
    args = parser.parse_args()

    rows, errors = parse_file(args.file)
    if errors:
        raise SystemExit("CSV invalide : " + "; ".join(errors))
    # Colonne facultative `review_note` : un cas signalé comme jugement à la
    # compilation reste humain, même si tout concorde avec la source.
    import csv
    with open(args.file, newline="", encoding="utf-8-sig") as fh:
        notes = [(r.get("review_note") or "").strip() for r in csv.DictReader(fh)]
    tables = {}
    if args.bocc_pdf:
        import hashlib
        with open(args.bocc_pdf, "rb") as fh:
            print(f"PDF BOCC : sha256 {hashlib.sha256(fh.read()).hexdigest()}")
        tables = parse_bocc_pdf(args.bocc_pdf)
    sirens = {e["slug"]: e.get("siren") for e in supabase_client.list_entities()}
    from .load import _lookup_ids
    with httpx.Client(timeout=60) as c:
        tiers = {code: tier for code, (_, tier) in _lookup_ids(c)[2].items()}

    ok_rows, counts, reports = [], {}, {}
    with httpx.Client(timeout=300) as client:
        for r, note in zip(rows, notes):
            if r.source_code == "BOCC" and tables:
                v = verify_bocc(r, tables)
            elif r.source_code == "HATVP":
                v = verify_hatvp(r, client, sirens)
            elif r.source_url and "«" in (r.excerpt or ""):
                # Citation verbatim d'un document public : rapport ESEF, page web ou PDF.
                if r.source_url not in reports:
                    if r.source_code == "ESEF":
                        from .connectors.esef import report_text
                        reports[r.source_url] = report_text(r.source_url, client)
                    else:
                        reports[r.source_url] = document_text(r.source_url, client)
                # Un cas signalé « jugement » (ex. définition voisine de l'indicateur)
                # est vérifié sur la citation et la valeur, puis rendu à l'humain.
                rates = {}
                fx = FX_RE.search(r.excerpt or "")
                if fx:
                    rates[(fx.group(3), fx.group(1))] = ecb_annual_rate(fx.group(3), fx.group(1), client)
                v = check_esef_quote(r, reports[r.source_url], ignore_keywords=bool(note), rates=rates)
            else:
                v = Verdict("NON VÉRIFIABLE", [f"aucun vérificateur pour la source {r.source_code}"])
            v = finalize(v, note, tiers.get(r.source_code))
            counts[v.status] = counts.get(v.status, 0) + 1
            print(f"\n[{v.status}] {r.entity_slug} · {r.indicator_code} ({r.source_code})")
            for d in v.details:
                print(f"    {d}")
            if v.status == "OK":
                ok_rows.append(r)
    print("\nBilan : " + ", ".join(f"{k} {n}" for k, n in sorted(counts.items())))
    if args.apply:
        print(f"Approuvées (auto:verify_curated) : {approve(ok_rows)}")
    else:
        print("(contrôle seulement : --apply approuve les seules preuves OK)")


if __name__ == "__main__":
    main()
