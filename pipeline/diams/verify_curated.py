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
    python -m diams.verify_curated --file curated/banques_2026-10_lot1.csv --bocc-pdf tables.pdf
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
    # Politique d'exclusion, ou signature des Principes pour l'investissement responsable (méthode : « signataire UN PRI »).
    "INV_RESPONSIBLE_POLICY": [r"exclu|politiques? sectorielles?|Principes pour l.[Ii]nvestissement [Rr]esponsable|Principles for Responsible Investment|\bPRI\b"],
    "LAB_GENDER_PAYGAP": [r"[ée]cart|gap", r"r[ée]mun[ée]ration|salari|pay", r"femmes?|hommes?|genres?|gender|women|female"],
    # « ratio de rémunération annuelle totale » : intitulé ESRS S1-16, défini par rapport à la médiane.
    "LAB_CEO_PAY_RATIO": [r"ratio", r"m[ée]dian|r[ée]mun[ée]ration annuelle totale|annual total remuneration|total remuneration ratio"],
    "GOV_BOARD_GENDER": [r"femmes?|administratrices?|f[ée]minisation|f[ée]minin|wom[ae]n|female", r"conseil|board|director"],
    "GOV_BOARD_INDEP": [r"ind[ée]pendan|independen"],
    "ENV_SCOPE3_DISCLOSED": [r"scope 3"],
    "ENV_GHG_INTENSITY": [r"intensit", r"/\s?M€|/\s?million (?:CHF|USD|EUR|GBP|DKK|SEK)|revenu net|produit net|chiffre d.affaires|millions? d.euros|net revenue|rapportées? au revenu|per (?:1 )?million (?:EUR|euros?) of revenue|mln\.? EUR revenue|/EUR\b|/€m sales|per \$\s?1\s?M\b|net sales|per €"],
    "ENV_GHG_TREND": [r"GES|GHG|[ée]missions|CO2|CO ?₂|carbone|carbon"],
    # Avis du Jury de déontologie publicitaire (16/10/2026) : « Recommandation » (Développement durable
    # de l'ARPP) et ses verbes de conclusion.
    "ENV_GREENWASHING": [r"sustainab|durab|environment|environnement|green|[ée]colog|ambienta|recycl|Recommandation",
                         r"mislead|inaccurate|inexact|tromp|unclear|vague|claims?|all[ée]gation|m[ée]conna|contrevien|contraire|ne respecte"],
    # Plan de vigilance « complet » (barème de l'indicateur) : cartographie ET suivi,
    # lus dans le plan lui-même (C. com. L225-102-4 : cinq mesures).
    "SUP_VIGILANCE_PLAN": [r"vigilance", r"cartographie|analyse des risques|identifie les risques|risques d.atteintes graves", r"suivi|contr[ôo]le du respect|compte rendu"],
    # Taxonomie verte UE (art. 8) : part des CapEx ALIGNÉS (pas seulement éligibles).
    "ENV_TAXONOMY_CAPEX": [r"taxonom", r"capex|capital expenditure", r"align|afgestemd|allineat"],
    # Audit de marques Break Free From Plastic : classement des pollueurs.
    "PLA_POLLUTER": [r"polluter|pollueur"],
    # Recours à des matières animales (plafond du pilier animal).
    # Matières (mode, luxe), ingrédients (alimentation), tests (cosmétique).
    "ANI_EXPLOITATION": [r"cuirs?|maroquinerie|peaux?|shearling|fourrures?|crocodil|leather|skins?|fur\b|\blaine|\bwool|cachemire|cashmere"
                         r"|duvet|\bsoie\b|\bsilk\b|\blait|laiti|\bmilk|dairy|viande|\bmeat|\bbeef|b[œo]euf|\bporc\b|pork"
                         r"|poulet|chicken|volaille|poultry|(?:œ|oe)ufs?\b|\beggs?\b|\bmiel\b|honey|g[ée]latine|gelatin"
                         # Alimentation (règle de l'éditeur du 14/10/2026 : fromagerie, biscuits au
                         # beurre ou aux œufs…). « beurre de cacahuète / karité / cacao » exclu.
                         r"|fromages?\b|\bbeurre\b(?! de (?:cacahu|karit|cacao))|\bcr[èe]me fra[îi]che|yaourts?\b"
                         r"|foie gras|canards?\b|jambons?\b|charcuterie|saucisses?\b|saucissons?\b|rillettes|boudins?\b"
                         r"|poissons?\b|saumons?\b|\bthons?\b|sardines?\b|maquereaux?\b|anchois|crustac|mollusques"
                         r"|hu[îi]tres|caviar|[ée]levage|aquaculture|p[êe]che en (?:mer|eau douce)"
                         # Équivalents anglais des rapports en anglais (15/10/2026, lot 109) : fromage,
                         # beurre (hors beurres d'oléagineux), yaourt, poisson, saumon ; pas « cream », qui
                         # désigne aussi une crème cosmétique.
                         r"|\bcheeses?\b|\bbutter\b(?<!nut butter)(?<!almond butter)(?<!peanut butter)(?<!cocoa butter)(?<!shea butter)"
                         r"|yogh?urts?\b|\bfish\b|\bsalmon\b|seafood"
                         # Rapports en allemand (16/10/2026, Schwarz) : viande, poisson, lait, fromage, œufs.
                         r"|fleisch|\bfisch|\bmilch|\bkäse|\beier\b"
                         # « produits carnés » (viande) et « produits de la mer » (poissons, coquillages),
                         # ajoutés le 15/10/2026 pendant la relecture des marques (vague 6).
                         r"|produits carn[ée]s|produits de la mer"
                         r"|d.origine animale|of animal origin|animal[- ]derived|tests? sur (les )?animaux|animal testing"
                         r"|tested on animals"],
    "ANI_FUR_FREE": [r"fourrure|fur\b"],
    # Politiques des matières animales de la mode (16/10/2026) : la citation nomme la matière.
    "ANI_DOWN_RDS": [r"duvet|plumes|\bdown\b", r"Responsible Down|RDS|plumage|virgin down|duvet neuf|recycl|live.?(?:birds|pluck)"],
    "ANI_WOOL_MULESING": [r"laine|wool", r"mulesing|Responsible Wool|RWS"],
    "ANI_ANGORA_MOHAIR": [r"angora|mohair"],
    "ANI_EXOTIC_SKINS": [r"exotiques?|exotic|peaux pr[ée]cieuses|precious skins|crocodil|python|autruche|ostrich|l[ée]zard|lizard"],
    "ANI_LEATHER_TRACE": [r"cuirs?|leather|tanneri", r"Leather Working Group|LWG|tra[çc]abilit|traceab"],
    # Pilier animal à trois niveaux (15/10/2026) : marque entièrement végétale, ou produits
    # 100 % végétaux proposés.
    "ANI_ANIMAL_FREE": [r"100 ?% v[ée]g[ée]ta|vegan|sans exploitation animale|sans (aucun )?ingr[ée]dient d.origine animale"],
    "ANI_OFFRE_VEGETALE": [r"100 ?% v[ée]g[ée]ta|vegan|v[ée]g[ée]talien|ne contient pas de produits animaux|d.origine v[ée]g[ée]tale"],
    "GEO_LOBBYING_ALIGN": [r"InfluenceMap|Climate Policy Engagement"],
    # Évolution du plastique vierge (tonnage absolu, pas par unité vendue).
    "PLA_REDUCTION": [r"plasti", r"vierge|virgin"],
    # Décision officielle d'une autorité : amende, ou infraction constatée sans amende.
    "GOV_SANCTIONS": [r"fine[ds]?\b|fining|amende|sanction|penalt(?:y|ies)"],
    # Arrêté de mise en demeure (Géorisques) ou convention judiciaire d'intérêt public (ministère de la
    # Justice) portant sur l'eau ; texte reconnu par OCR, accents parfois perdus.
    "WAT_CONTROVERSY": [r"rejet|effluent|eaux|[ée]puration|pr[ée]l[èe]vement|milieu|d[ée]versement|rivi[èe]re|forages?"],
}


# Barèmes de normalisation fixes (méthodologie) : mixité rapportée à la parité,
# indépendance en part du conseil.
NORMALIZE = {
    "GOV_BOARD_GENDER": lambda v: min(1.0, v / 50),
    "GOV_BOARD_INDEP": lambda v: v / 100,
    "ENV_TAXONOMY_CAPEX": lambda v: v / 100,
}

# Indicateurs classés entre pairs du secteur au calcul (percentile) : aucune note précalculée,
# sinon la ligne échappe au classement et n'est plus comparable aux autres (contrôle du 17/10/2026,
# après huit lignes « emballages » notées en part brute alors que les 26 autres étaient classées).
PEER_RANKED = {"PLA_RECYCLED", "PLA_RECYCLABLE", "WAT_WITHDRAWAL_INTENSITY", "PLA_REDUCTION", "WAT_INTENSITY", "ENV_GHG_INTENSITY", "LAB_GENDER_PAYGAP",
               "LAB_CEO_PAY_RATIO", "TAX_EFFECTIVE_RATE", "TAX_HAVEN_PRESENCE"}


def _canon(s: str) -> str:
    # Accents décomposés (« e » + accent combinant) : certaines pages officielles (Autorité de la
    # concurrence) sont en NFD ; la comparaison se fait en forme composée (ajout du 15/10/2026).
    s = unicodedata.normalize("NFC", s)
    s = s.replace("’", "'").replace(" ", " ").replace(" ", " ")
    # Signe moins typographique : « –9.9 % » est la valeur -9,9.
    s = s.replace("\u2013", "-").replace("\u2212", "-").replace("\u2011", "-")
    return re.sub(r"\s+", " ", s).strip()


def _value_variants(v: float) -> list[str]:
    out = {f"{v:.2f}".replace(".", ","), f"{v:.1f}".replace(".", ",")}
    out |= {f"{v:.2f}", f"{v:.1f}"}                      # notation anglaise : 17.4
    if round(v, 3) == v and round(v, 2) != v:            # trois décimales publiées : 3,147
        out |= {f"{v:.3f}", f"{v:.3f}".replace(".", ",")}
    if float(v).is_integer():
        out |= {f"{int(v)}", f"{int(v):,}"}             # 1980 et 1,980
    elif abs(v) >= 1000:                                 # milliers et décimale en anglais : 1,790.6
        out |= {f"{v:,.1f}", f"{v:,.2f}"}
    return list(out)


_NUM_WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
    "seventeen eighteen nineteen twenty".split())}
_NUM_WORDS.update({w: i for i, w in enumerate(
    "zéro un deux trois quatre cinq six sept huit neuf dix onze douze treize quatorze quinze seize dix-sept "
    "dix-huit dix-neuf vingt".split())})
_NUM_WORDS["une"] = 1   # féminin : « une seule femme … sur 12 membres »
_NUM = r"\d{1,2}|" + "|".join(sorted(_NUM_WORDS, key=len, reverse=True))
_COUNT = re.compile(rf"\b({_NUM})\b(?:\s+\w+){{0,3}}?\s+(?:of|sur)\s+(?:our\s+|the\s+|its\s+)?({_NUM})\b", re.I)


# Conseil entièrement indépendant, déclaré comme tel (valeur 100 %).
_ALL_INDEP = re.compile(r"\ball (?:the )?(?:other )?(?:members of the board(?: of directors)?|board members|directors|members)\b"
                        r"[^.;]{0,40}?\bare independent\b|l.ensemble (?:de ses|des) membres (?:du conseil[^.;]{0,30})?est ind[ée]pendant",
                        re.I)


# Conseil sans aucun membre indépendant, déclaré comme tel (valeur 0 %).
_NO_INDEP = re.compile(r"\babsence d.administrateurs? ind[ée]pendants?\b|\baucun(?:e)? (?:administrat(?:eur|rice)|membre)s? "
                       r"(?:du conseil )?(?:n.est )?ind[ée]pendante?s?\b|\bno independent (?:directors|board members)\b"
                       r"|\bnone of (?:the|our|its) directors (?:is|are) independent\b", re.I)


_SLASH = re.compile(r"\b(\d{1,2})\s*/\s*(\d{1,2})\b")
# « nine men and seven women » / « sept femmes et neuf hommes » : part des femmes = femmes / total.
_MEN_WOMEN = re.compile(rf"\b({_NUM})\b\s+(?:men|hommes)\s+(?:and|et)\s+\b({_NUM})\b\s+(?:women|femmes)\b", re.I)
_WOMEN_MEN = re.compile(rf"\b({_NUM})\b\s+(?:women|femmes)\s+(?:and|et)\s+\b({_NUM})\b\s+(?:men|hommes)\b", re.I)
# « Number of Directors 11, including 6 external directors » : part = 6 / 11.
_INCLUDING = re.compile(rf"\b({_NUM})\b,?\s+(?:including|dont)\s+\b({_NUM})\b\s+(?:external|independent|outside|ind[ée]pendants?|externes?)\b", re.I)


def _count_ratio_matches(value: float, quote: str) -> bool:
    """« 11 of 12 director nominees », « six femmes Administratrices sur 14 »,
    « 4 /10 women » : le pourcentage déclaré doit être le rapport des effectifs cités."""
    for m in list(_COUNT.finditer(quote)) + list(_SLASH.finditer(quote)):
        a, b = (int(x) if x.isdigit() else _NUM_WORDS.get(x.lower()) for x in m.groups())
        if a is not None and b and a <= b and abs(round(100 * a / b, 1) - value) <= 0.05:
            return True
    for m in _INCLUDING.finditer(quote):
        b, a = (int(v) if v.isdigit() else _NUM_WORDS.get(v.lower()) for v in m.groups())
        if a is not None and b and a <= b and abs(round(100 * a / b, 1) - value) <= 0.05:
            return True
    for rx, women_first in ((_MEN_WOMEN, False), (_WOMEN_MEN, True)):
        for m in rx.finditer(quote):
            x, y = (int(v) if v.isdigit() else _NUM_WORDS.get(v.lower()) for v in m.groups())
            if x is None or y is None or not x + y:
                continue
            women = x if women_first else y
            if abs(round(100 * women / (x + y), 1) - value) <= 0.05:
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


# Évolution des émissions : rythme annuel moyen recalculé depuis deux totaux cités.
# « … rythme annuel moyen (2019 → 2025, 6 ans) : (6855000 / 10227000)^(1/6) − 1 = −6,45 % »
TREND_RE = re.compile(r"rythme annuel moyen \((\d{4}) → (\d{4}), (\d+) ans?\) : \(([\d.,]+) / ([\d.,]+)\)"
                      r"\^\(1/(\d+)\) − 1 = ([−-]?[\d,]+) %")
TREND_FULL = 4.2  # baisse annuelle (en %) qui vaut la note pleine : trajectoire 1,5 °C de la SBTi
TREND_MIN_YEARS_FOR_DECLINE = 2  # une baisse sur une seule année ne prouve pas une trajectoire


def trend_score(rate_pct: float) -> float:
    """1 si baisse ≥ 4,2 %/an, 0 si pas de baisse, linéaire entre les deux."""
    return round(max(0.0, min(1.0, -rate_pct / TREND_FULL)), 4)


# Variante : l'entreprise publie une variation en pourcentage depuis l'année de
# référence (« 19% CO2 reduction vs. 2022 baseline in Scope 1, 2 and 3 »).
# « … rythme annuel moyen (2022 → 2025, 3 ans) : (1 − 19 %)^(1/3) − 1 = −6,78 % »
TREND_PCT_RE = re.compile(r"rythme annuel moyen \((\d{4}) → (\d{4}), (\d+) ans?\) : \(1 ([−+-]) ([\d,]+) %\)"
                          r"\^\(1/(\d+)\) − 1 = ([−-]?[\d,]+) %")


def _trend_norm_ok(row, stated: float) -> bool:
    """Émissions : note fixée par le seuil 1,5 °C. Autres rythmes (plastique vierge) :
    pas de note précalculée, la valeur est classée entre pairs du secteur."""
    if row.indicator_code == "ENV_GHG_TREND":
        return row.normalized_value is not None and abs(row.normalized_value - trend_score(stated)) < 1e-3
    return row.normalized_value is None


def check_trend_pct(row, quote: str) -> tuple[bool, list[str], bool]:
    m = TREND_PCT_RE.search(row.excerpt or "")
    if not m:
        return True, [], False
    y0, y1, n_s, sign, pct_s, n2_s, r_s = m.groups()
    n = int(n_s)
    pct = float(pct_s.replace(",", "."))
    change = -pct if sign in "−-" else pct
    rate = (pow(1 + change / 100, 1 / n) - 1) * 100
    stated = float(r_s.replace("−", "-").replace(",", "."))
    pct_forms = {pct_s, pct_s.replace(",", "."), f"{pct:g}"}
    joined = re.sub(r"(\d) ([.,]\d)", r"\1\2", quote)   # « 17 .7 % » (extraction de PDF)
    # « (29) % » : baisse en notation comptable (rapport annuel d'Unilever).
    paren = r"\)?" if sign in "−-" else ""
    present = any(re.search(rf"(?<![\d.,]){re.escape(f)}{paren}\s?%", x) for f in pct_forms for x in (quote, joined))
    # Tableau dont l'unité est dans l'intitulé de la ligne (« … (vs. 2020) (%)(2)(10) 11.5 4.6 ») :
    # la variation y figure comme nombre isolé, sans « % » collé (ajout du 15/10/2026).
    if not present and "(%)" in quote:
        present = any(re.search(rf"(?<![\d.,]){re.escape(f)}(?![\d.,])", x) for f in pct_forms for x in (quote, joined))
    years_ok = int(y1) - int(y0) == n and n_s == n2_s and n > 0 and (y0 in quote)
    calc_ok = abs(rate - stated) <= 0.01
    value_ok = row.value_numeric is not None and abs(row.value_numeric - stated) < 1e-9
    norm_ok = _trend_norm_ok(row, stated)
    span_ok = n >= TREND_MIN_YEARS_FOR_DECLINE or stated >= 0
    ok = present and years_ok and calc_ok and value_ok and norm_ok and span_ok
    return ok, [
        f"variation {sign}{pct_s} % présente dans la citation {'✓' if present else '✗'}",
        f"{y0} → {y1} = {n} an(s), année de référence citée {'✓' if years_ok else '✗'}",
        f"durée suffisante pour une baisse ({n} an(s)) {'✓' if span_ok else '✗'}",
        f"rythme recalculé {rate:.2f} % = déclaré {stated} % {'✓' if calc_ok else '✗'}",
        f"valeur et note ({trend_score(stated)}) conformes {'✓' if value_ok and norm_ok else '✗'}",
    ], True


# Conseil « tous indépendants sauf le PDG » : la part est calculée depuis l'effectif cité.
# « … calcul : (12 − 1) / 12 = 91,7 % » ; la citation donne l'effectif (« twelve directors »)
# et l'exception (« with the exception of our CEO »).
# Exception composée : « calcul : (9 − (2 + 1)) / 9 = 66,7 % » (deux exécutifs cités, plus
# l'administrateur nommé après « except for »).
EXCEPT_RE = re.compile(r"calcul : \((\d+) − (\d+|\(\d+ \+ \d+\))\) / (\d+) = ([\d,]+) %")
_EXCEPT_PHRASE = re.compile(r"with the exception of|\bexcept\b|other than|\bsauf\b|à l'exception", re.I)
# Exception nommée à part : « all of the Company’s current non-management directors are …
# “independent” » puis « Mr. Peterson is not considered an independent director » ; les
# deux phrases sont exigées ensemble (l'une seule ne dit pas qui est indépendant).
_NOT_INDEP = re.compile(r"\bis not (?:considered|deemed|determined to be) (?:to be )?(?:an )?independent\b", re.I)
_ALL_INDEP_STMT = re.compile(r"\ball (?:of )?(?:the |our )?(?:company.s )?(?:current )?(?:other )?(?:non-management |non-employee )?"
                             r"directors\b[^.;]{0,120}?\b(?:are|were)\b[^.;]{0,40}?independent", re.I)


def check_except(row, quote: str) -> tuple[bool, list[str], bool]:
    m = EXCEPT_RE.search(row.excerpt or "")
    if not m:
        return True, [], False
    n_s, k_s, n2_s, v_s = m.groups()
    n, parts = int(n_s), [int(x) for x in re.findall(r"\d+", k_s)]
    k = sum(parts)
    words = [w for w, i in _NUM_WORDS.items() if i == n]
    size_cited = re.search(rf"\b{n}\b", quote) is not None or any(
        re.search(rf"\b{re.escape(w)}\b", quote, re.I) for w in words)
    exception = _EXCEPT_PHRASE.search(quote) is not None or (
        _NOT_INDEP.search(quote) is not None and _ALL_INDEP_STMT.search(quote) is not None)
    # Chaque partie de plus d'une personne doit être citée ; la personne nommée après
    # « sauf » compte pour 1 (une seule partie de 1 au plus).
    parts_ok = len(parts) == 1 or (sum(1 for x in parts if x == 1) <= 1
                                   and all(_cited(x, quote) for x in parts if x > 1))
    stated = float(v_s.replace(",", "."))
    calc_ok = (n_s == n2_s and 0 < k <= (3 if len(parts) > 1 else 2) and parts_ok
               and abs(round(100 * (n - k) / n, 1) - stated) < 1e-9)
    value_ok = row.value_numeric is not None and abs(row.value_numeric - stated) < 1e-9
    ok = size_cited and exception and calc_ok and value_ok
    return ok, [
        f"effectif {n} cité {'✓' if size_cited else '✗'}",
        f"exception citée (« sauf … ») {'✓' if exception else '✗'}"
        + (f", parties {' + '.join(map(str, parts))} citées {'✓' if parts_ok else '✗'}" if len(parts) > 1 else ""),
        f"part recalculée ({n} − {k}) / {n} = {round(100 * (n - k) / n, 1)} % = valeur {'✓' if calc_ok and value_ok else '✗'}",
    ], True


# Part calculée depuis deux effectifs cités dans des phrases distinctes :
# « the 10 incumbent directors » … « include four women » → « calcul : 4 / 10 = 40 % ».
# Effectif publié en deux parties (« two executive directors and 13 non-executive
# directors ») : « calcul : 13 / (2 + 13) = 86,7 % », chaque partie citée ; de même
# au numérateur (« calcul : (6 + 3) / 12 = 75 % »).
_TERM = r"(\d+|\(\d+(?: [+−] \d+)+\))"
RATIO_RE = re.compile(rf"calcul : {_TERM} / {_TERM} = ([\d,]+) %")


def _parts(term: str) -> list[int]:
    return [int(x) for x in re.findall(r"\d+", term)]


def _value(term: str) -> int:
    """Valeur d'un terme : nombre, somme « (a + b) » ou différence « (a − b) »
    (ex. membres du conseil hors représentants des salariés : (17 − 2))."""
    nums = _parts(term)
    return nums[0] - sum(nums[1:]) if "−" in term else sum(nums)


_CHAIR_INDEP = re.compile(r"\bChair(?:man|woman|person)?\b(?: of the Board)? (?:was|is) (?:considered |deemed |determined )?"
                          r"(?:to be )?independent\b"
                          r"|\bprésident(?:e)?\b(?: du conseil)? (?:est|était) (?:considérée? comme |qualifiée? d.)?indépendant", re.I)


def _cited(n: int, quote: str) -> bool:
    words = [w for w, i in _NUM_WORDS.items() if i == n]
    flat = re.sub(r"(?<=\d)[ \u00a0\u202f](?=\d{3}(?!\d))", "", quote)
    flat_en = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", quote)   # notation anglaise : 802,505
    # Montant écrit avec des espaces de milliers, suivi d'une autre colonne (« 430 809 336 503 » :
    # la fusion des espaces en ferait un seul nombre) : on cherche aussi la forme groupée.
    grouped = r"[   ]".join(re.findall(r"\d{1,3}(?=(?:\d{3})*$)", str(n))) if n >= 1000 else None
    return any(re.search(rf"(?<![\d,.]){n}(?!\d)(?![.,]\d)", x) for x in (quote, flat, flat_en)) or (
        grouped is not None and re.search(rf"(?<![\d,.])(?<!\d )(?<!\d )(?<!\d ){grouped}(?!\d)(?![.,]\d)", quote) is not None) or any(
        re.search(rf"\b{re.escape(w)}\b", quote, re.I) for w in words)


# Indépendants désignés par leur nom (« The Board has determined that Messrs. A, B and C and Mses. D
# and E are independent ») : les noms sont comptés dans la citation (16/10/2026).
# « … calcul : 7 administrateurs nommés indépendants / 10 = 70 % … »
NAMED_RE = re.compile(r"calcul : (\d+) administrateurs nommés indépendants / (\d+) = ([\d,]+) %")
_NAMED_LIST = re.compile(r"determined that (.+?) (?:are independent|do not have a relationship|is independent)", re.I)


def check_named(row, quote: str) -> tuple[bool, list[str], bool]:
    m = NAMED_RE.search(row.excerpt or "")
    if not m:
        return True, [], False
    n, b, v_s = int(m.group(1)), int(m.group(2)), m.group(3)
    lst = _NAMED_LIST.search(quote)
    names = []
    if lst:
        body = re.sub(r"\b(?:Messrs|Mses|Mmes|Mr|Mrs|Ms|Dr)\.\s*", "", lst.group(1))
        names = [x for x in re.split(r",\s*(?:and\s+)?|\s+and\s+", body) if x.strip()]
    count_ok = len(names) == n
    total_ok = _cited(b, quote)
    stated = float(v_s.replace(",", "."))
    calc_ok = 0 < n <= b and abs(round(100 * n / b, 1) - stated) < 1e-9
    value_ok = row.value_numeric is not None and abs(row.value_numeric - stated) < 1e-9
    return count_ok and total_ok and calc_ok and value_ok, [
        f"{len(names)} noms d'indépendants comptés dans la citation = {n} {'✓' if count_ok else '✗'}",
        f"effectif {b} cité {'✓' if total_ok else '✗'}",
        f"part recalculée {n} / {b} = {round(100 * n / b, 1) if b else '—'} % = valeur {'✓' if calc_ok and value_ok else '✗'}",
    ], True


def check_ratio(row, quote: str) -> tuple[bool, list[str], bool]:
    m = RATIO_RE.search(row.excerpt or "")
    if not m:
        return True, [], False
    a_s, b_s, v_s = m.groups()
    num, parts = _parts(a_s), _parts(b_s)
    a, b = _value(a_s), _value(b_s)
    stated = float(v_s.replace(",", "."))
    # Au numérateur d'une somme, le président déclaré indépendant compte pour 1
    # (« the Chair was considered to be independent on appointment »).
    chair = (row.indicator_code == "GOV_BOARD_INDEP" and len(num) > 1 and num.count(1) == 1
             and _CHAIR_INDEP.search(quote) is not None)
    both = all(_cited(x, quote) or (chair and x == 1 and i == num.index(1))
               for i, x in enumerate(num)) and all(_cited(x, quote) for x in parts)
    calc_ok = 0 < a <= b and abs(round(100 * a / b, 1) - stated) < 1e-9
    value_ok = row.value_numeric is not None and abs(row.value_numeric - stated) < 1e-9
    return both and calc_ok and value_ok, [
        f"effectifs {' + '.join(map(str, num))} et {' + '.join(map(str, parts))} cités {'✓' if both else '✗'}",
        f"part recalculée {a} / {b} = {round(100 * a / b, 1) if b else '—'} % = valeur {'✓' if calc_ok and value_ok else '✗'}",
    ], True


# Variante : l'entreprise publie des variations d'une année sur l'autre (« 6% » en
# 2025, « 5% » en 2024) ; elles sont composées.
# « … rythme annuel moyen (2023 → 2025, 2 ans) : ((1 − 5 %) × (1 − 6 %))^(1/2) − 1 = −5,50 % »
TREND_YOY_RE = re.compile(r"rythme annuel moyen \((\d{4}) → (\d{4}), (\d+) ans?\) : "
                          r"\(((?:\(1 [−+-] [\d,]+ %\)(?: × )?){2,})\)\^\(1/(\d+)\) − 1 = ([−-]?[\d,]+) %")


def check_trend_yoy(row, quote: str) -> tuple[bool, list[str], bool]:
    m = TREND_YOY_RE.search(row.excerpt or "")
    if not m:
        return True, [], False
    y0, y1, n_s, inner, n2_s, r_s = m.groups()
    n = int(n_s)
    factors = re.findall(r"\(1 ([−+-]) ([\d,]+) %\)", inner)
    prod = 1.0
    present = True
    for sign, pct_s in factors:
        pct = float(pct_s.replace(",", "."))
        prod *= 1 + (-pct if sign in "−-" else pct) / 100
        forms = {pct_s, pct_s.replace(",", "."), f"{pct:g}"}
        present &= any(re.search(rf"(?<![\d.,]){re.escape(f)}\s?%", quote) for f in forms)
    rate = (pow(prod, 1 / n) - 1) * 100
    stated = float(r_s.replace("−", "-").replace(",", "."))
    years_ok = int(y1) - int(y0) == n == len(factors) and n_s == n2_s
    calc_ok = abs(rate - stated) <= 0.01
    value_ok = row.value_numeric is not None and abs(row.value_numeric - stated) < 1e-9
    norm_ok = _trend_norm_ok(row, stated)
    span_ok = n >= TREND_MIN_YEARS_FOR_DECLINE or stated >= 0
    ok = present and years_ok and calc_ok and value_ok and norm_ok and span_ok
    return ok, [
        f"variations annuelles {', '.join(s + p for s, p in factors)} % présentes dans la citation {'✓' if present else '✗'}",
        f"{y0} → {y1} = {n} an(s), une variation par année {'✓' if years_ok else '✗'}",
        f"rythme recalculé {rate:.2f} % = déclaré {stated} % {'✓' if calc_ok else '✗'}",
        f"valeur et note conformes {'✓' if value_ok and norm_ok else '✗'}",
    ], True


# Unité publiée différente de celle de l'indicateur : la conversion est écrite dans
# l'extrait et recalculée. « conversion : 0,00039 t/€ × 1 000 000 = 390 t/M€ », ou
# depuis des kilogrammes par euro : « conversion : 0,23 kg/€ × 1 000 = 230 t/M€ ».
# Ajout du 15/10/2026 : intensité hydrique publiée en milliers de m³ par M€ (Heineken : « 1.12 thousand m3 / mEUR »).
UNIT_RE = re.compile(r"conversion : ([\d,]+) (t/€ × 1 000 000|kg/€ × 1 000|milliers de m³/M€ × 1 000|kt/M€ × 1 000|t/k€ × 1 000) = ([\d ,]+) (t/M€|m³/M€)")


def check_unit(row, quote: str) -> tuple[bool, list[str], bool]:
    m = UNIT_RE.search(row.excerpt or "")
    if not m:
        return True, [], False
    a_s, unit, c_s, out = m.groups()
    factor, unit_s = (1e6, "t/€") if unit.startswith("t/€") else (1e3, unit.split(" × ")[0])
    a, c = float(a_s.replace(",", ".")), float(c_s.replace(" ", "").replace(",", "."))
    # Le rapport peut être en anglais (0.23) quand l'extrait écrit 0,23.
    present = any(re.search(rf"(?<![\d,.]){re.escape(f)}(?!\d)", quote) is not None
                  for f in {a_s, a_s.replace(",", ".")})
    calc_ok = abs(a * factor - c) <= 0.5
    value_ok = row.value_numeric is not None and abs(row.value_numeric - c) < 1e-9
    return present and calc_ok and value_ok, [
        f"valeur publiée {a_s} {unit_s} présente dans la citation {'✓' if present else '✗'}",
        f"conversion {a_s} × {'1 000 000' if factor == 1e6 else '1 000'} = {a * factor:g} {out} = valeur {'✓' if calc_ok and value_ok else '✗'}",
    ], True


def check_trend(row, quote: str) -> tuple[bool, list[str], bool]:
    """Contrôle du rythme déclaré : années cohérentes, deux totaux présents dans la
    citation, calcul exact, valeur et note conformes. Le dernier booléen dit si la
    formule est présente (la valeur, calculée, n'est alors pas cherchée telle quelle)."""
    m = TREND_RE.search(row.excerpt or "")
    if not m:
        return True, [], False
    y0, y1, n_s, last_s, base_s, n2_s, r_s = m.groups()
    n = int(n_s)
    # Totaux écrits sans séparateur de milliers ; virgule = décimale (« 265,1 »).
    last, base = float(last_s.replace(",", ".")), float(base_s.replace(",", "."))
    rate = (pow(last / base, 1 / n) - 1) * 100 if base > 0 else float("nan")
    stated = float(r_s.replace("−", "-").replace(",", "."))
    flat = re.sub(r"(?<=\d)[\s,](?=\d{3}(?!\d))", "", quote)
    def forms(x: float) -> list[str]:
        # Écritures possibles d'un total : 6855000, 6,855,000, 6 855 000, 265,1, 265.1
        out = _value_variants(x)
        if float(x).is_integer():
            out.append(f"{int(x):,}".replace(",", " "))
        return out
    present = all(any(re.search(rf"(?<![\d.,]){re.escape(v)}(?![\d])", f) for v in forms(x) for f in (flat, quote))
                  for x in (last, base))
    years_ok = int(y1) - int(y0) == n and n_s == n2_s and n > 0
    calc_ok = abs(rate - stated) <= 0.01
    value_ok = row.value_numeric is not None and abs(row.value_numeric - stated) < 1e-9
    norm_ok = _trend_norm_ok(row, stated)
    # Une baisse ne vaut preuve que sur deux ans au moins (une année peut tenir aux
    # ventes ou à la météo) ; une hausse, même sur un an, montre que les émissions
    # ne baissent pas.
    span_ok = n >= TREND_MIN_YEARS_FOR_DECLINE or stated >= 0
    ok = present and years_ok and calc_ok and value_ok and norm_ok and span_ok
    return ok, [
        f"durée suffisante pour une baisse ({n} an(s), minimum {TREND_MIN_YEARS_FOR_DECLINE}) {'✓' if span_ok else '✗'}",
        f"totaux {last_s} et {base_s} présents dans la citation {'✓' if present else '✗'}",
        f"{y0} → {y1} = {n} an(s) {'✓' if years_ok else '✗'}",
        f"rythme recalculé {rate:.2f} % = déclaré {stated} % {'✓' if calc_ok else '✗'}",
        f"valeur et note ({trend_score(stated)}) conformes {'✓' if value_ok and norm_ok else '✗'}",
    ], True


# Sanction d'une autorité : la gravité suit le montant de l'amende, relu dans la
# citation officielle. « amende de 74,9 M€ » ↔ « Stellantis 50% €74 934 000 ».
SANCTION_TIERS = ((1e9, 0.9), (1e8, 0.7), (0.0, 0.5))
_SANCTION_VT = re.compile(r"amendes? de (?:plus de )?([\d ]+(?:,\d+)?) (M|Md)(€|£|A\$|\$)")
# Amende prononcée en livres ou en dollars (CMA, FTC) : montant relu dans la devise du
# communiqué, gravité calculée après conversion au taux annuel moyen de la BCE.
# Dollar australien (« MA$ ») : les jugements australiens écrivent « $60 million » sans préfixe.
_DEVISES = {"£": "GBP", "$": "USD", "A$": "AUD"}
# Montant en euros, quelle que soit l'écriture du communiqué : « €1.8 billion », « EUR 114,681,657 »,
# « 98,635,416.67 euro », « € 1,128 billion » (virgule décimale), « 150 millions d'euros »,
# « 100 000 euros ». Chaque nombre est lu à l'anglaise et à la française ; le montant
# déclaré doit correspondre à l'une des lectures.
_AMOUNT = r"\d{1,3}(?:[ ,.\u00a0\u202f]\d{3})*(?:[.,]\d+)?"
_SCALE_WORD = r"billion|million|milliards?|millions?|bn|m"   # « €17m », « €1.2bn »
_EUR_LEAD = re.compile(rf"(?:€|\bEUR)\s?({_AMOUNT})(?:\s?({_SCALE_WORD})\b)?", re.I)
_EUR_TRAIL = re.compile(rf"(?<![\d,.])({_AMOUNT})\s?(?:({_SCALE_WORD})\s?)?(?:d'\s?)?(?:euros?\b|€)", re.I)
_FX_LEAD = {cur: re.compile(rf"(?:{re.escape(sym)}|\b{cur})\s?({_AMOUNT})(?:\s?({_SCALE_WORD})\b)?", re.I)
            for sym, cur in {"£": "GBP", "$": "USD"}.items()}
_FX_LEAD["AUD"] = re.compile(rf"(?:A\$|\bAUD|\$)\s?({_AMOUNT})(?:\s?({_SCALE_WORD})\b)?", re.I)
_SCALE = {"bn": 1e9, "m": 1e6, "billion": 1e9, "million": 1e6, "milliard": 1e9, "milliards": 1e9, "millions": 1e6}


def _readings(n_s: str) -> list[float]:
    """« 1,128 » : 1128 à l'anglaise, 1,128 à la française ; « 98,635,416.67 » : anglaise seule."""
    s = re.sub(r"[ \u00a0\u202f]", "", n_s)
    out = []
    for txt in (s.replace(",", ""), s.replace(".", "").replace(",", ".")):
        try:
            out.append(float(txt))
        except ValueError:
            pass
    return out


def euro_amounts(quote: str) -> list[float]:
    found = []
    for rx in (_EUR_LEAD, _EUR_TRAIL):
        for n_s, word in rx.findall(quote):
            found += [n * _SCALE.get(word.lower(), 1) for n in _readings(n_s)]
    # Tableau dont l'en-tête donne l'unité : « Montants des sanctions (en euros) TEMF 115 820 000 ».
    if re.search(r"\((?:en )?euros\)|\(in (?:EUR|euros?)\)", quote, re.I):
        for n_s in re.findall(r"(?<![\d,.])\d{1,3}(?:[ \u00a0\u202f]\d{3}){2,}(?!\d)", quote):
            found += _readings(n_s)
    return found


def foreign_amounts(quote: str, currency: str) -> list[float]:
    found = []
    for n_s, word in _FX_LEAD[currency].findall(quote):
        found += [n * _SCALE.get(word.lower(), 1) for n in _readings(n_s)]
    return found


def sanction_rate_year(row) -> str:
    return str(row.observed_on)[:4]


def sanction_severity(amount_eur: float) -> float:
    """Amende d'au moins 1 Md€ = 0,9 ; de 100 M€ à 1 Md€ = 0,7 ; moins (ou infraction
    sans amende, immunité de clémence) = 0,5."""
    return next(sev for floor, sev in SANCTION_TIERS if amount_eur >= floor)


def check_sanction(row, quote: str, rates: dict | None = None) -> tuple[bool, list[str]]:
    vt = row.value_text or ""
    if "immunité" in vt:
        cited = re.search(r"not fined|immunity|immunité", quote, re.I) is not None
        norm_ok = row.normalized_value is not None and abs(row.normalized_value - 0.5) < 1e-9
        return cited and norm_ok, [
            f"infraction constatée sans amende (immunité) citée {'✓' if cited else '✗'}",
            f"sévérité 0,5 {'✓' if norm_ok else '✗'}"]
    m = _SANCTION_VT.search(vt)
    if not m:
        return False, [f"montant illisible dans « {vt} » ✗"]
    num_s, unit, sym = m.groups()
    decimals = len(num_s.split(",")[1]) if "," in num_s else 0
    stated = float(num_s.replace(" ", "").replace(",", "."))
    scale = 1e9 if unit == "Md" else 1e6
    conv = []
    if sym == "€":
        quoted, eur = euro_amounts(quote), stated * scale
    else:
        cur = _DEVISES[sym]
        quoted = foreign_amounts(quote, cur)
        rate = (rates or {}).get((cur, sanction_rate_year(row)))
        if rate is None:
            return False, [f"taux {cur} {sanction_rate_year(row)} de la BCE introuvable ✗"]
        eur = stated * scale / rate
        taux_s, eur_s = f"{rate:.4f}".replace(".", ","), f"{eur / 1e6:.1f}".replace(".", ",")
        conv = [f"converti au taux annuel moyen {(rates or {}).get(('annee', cur, sanction_rate_year(row)), sanction_rate_year(row))} de la BCE (1 € = {taux_s} {cur}) : ≈ {eur_s} M€"]
    present = any(round(q / scale, decimals) == stated for q in quoted)
    sev = sanction_severity(eur)
    norm_ok = row.normalized_value is not None and abs(row.normalized_value - sev) < 1e-9
    return present and norm_ok, [
        f"montant {num_s} {unit}{sym} retrouvé dans la citation {'✓' if present else '✗'}", *conv,
        f"sévérité {sev} conforme au barème {'✓' if norm_ok else '✗'}"]


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
    # PDF dont l'extraction coupe les mots (« ar e women ») : même suite de caractères,
    # espaces de mise en page ignorés. La citation affichée reste lisible.
    spaced = False
    if not found:
        bare = re.sub(r"\s", "", canon_report)
        found = spaced = all(re.sub(r"\s", "", q) in bare for q in quotes)
    label = "citation retrouvée" if len(quotes) == 1 else f"{len(quotes)} citations retrouvées"
    details = [f"{label} mot pour mot dans le rapport"
               f"{' (espaces de mise en page ignorés)' if spaced else ''} {'✓' if found else '✗'}"]
    quote = " … ".join(quotes)
    ok = found
    for kw in ([] if ignore_keywords else ESEF_KEYWORDS.get(row.indicator_code, [])):
        hit = re.search(kw, quote, re.I) is not None
        # Liste d'ingrédients d'un produit alimentaire : « crème » est une crème laitière par défaut
        # (décision de l'éditeur, 17/10/2026) ; hors de ce cadre, le mot peut désigner un cosmétique.
        if (not hit and row.indicator_code == "ANI_EXPLOITATION" and "liste des ingrédients" in (row.excerpt or "")
                and re.search(r"\bcr[èe]me\b(?! (?:de |d.)(?:coco|riz|soja|marrons?|amandes?|avoine|cajou))", quote, re.I)):
            hit = True
        ok &= hit
        details.append(f"la citation porte sur l'indicateur (« {kw} ») {'✓' if hit else '✗'}")
    # Valeur convertie d'une autre devise : la conversion est contrôlée, puis c'est
    # le montant d'origine qu'on cherche dans la citation.
    fx_ok, fx_details, fx_source = check_fx(row, quote, rates or {})
    ok &= fx_ok
    details += fx_details
    tr_ok, tr_details, tr_active = check_trend(row, quote)
    if not tr_active:
        tr_ok, tr_details, tr_active = check_trend_pct(row, quote)
    if not tr_active:
        tr_ok, tr_details, tr_active = check_trend_yoy(row, quote)
    if not tr_active:
        tr_ok, tr_details, tr_active = check_except(row, quote)
    if not tr_active and row.indicator_code == "SUP_BHRRC_ALLEG":
        # Allégations relayées par le BHRRC (16/10/2026) : la valeur est le nombre d'articles
        # cités, chacun par son titre exact dans le flux public.
        tr_active = True
        tr_ok = row.value_numeric is not None and int(row.value_numeric) == len(quotes)
        tr_details = [f"nombre d'articles cités {len(quotes)} = valeur {'✓' if tr_ok else '✗'}"]
    if not tr_active and row.indicator_code == "TAX_HAVEN_PRESENCE" and _HAVEN_MARK in (row.excerpt or ""):
        # Filiales dans les paradis fiscaux d'après les tableaux des sociétés consolidées
        # (17/10/2026) : la valeur est un décompte, refait depuis le rapport original (main).
        tr_active, tr_ok = True, True
        tr_details = ["décompte des filiales refait depuis le rapport original (ci-dessous)"]
    if not tr_active:
        tr_ok, tr_details, tr_active = check_named(row, quote)
    if not tr_active:
        tr_ok, tr_details, tr_active = check_ratio(row, quote)
    if not tr_active:
        tr_ok, tr_details, tr_active = check_unit(row, quote)
    ok &= tr_ok
    details += tr_details
    if row.indicator_code == "TAX_EFFECTIVE_RATE" and re.search(
            r"perte avant impôt|sur une perte|loss(?:es)? before (?:income )?tax", row.excerpt or "", re.I):
        # Méthodologie : un exercice en perte avant impôt n'a pas de taux interprétable (17/10/2026).
        ok = False
        details.append("exercice en perte avant impôt : taux non interprétable, pas de preuve ✗")
    if row.indicator_code == "GOV_SANCTIONS":
        sc_ok, sc_details = check_sanction(row, quote, rates)
        ok &= sc_ok
        details += sc_details
    if row.value_numeric is not None and not ignore_keywords and not tr_active:
        # Espaces de milliers seulement ; pas après un rapport « 137:1 » (colonnes de
        # ratios : « 137:1 126:1 » ne contient pas le nombre 1126).
        flat = re.sub(r"(?<=\d)(?<!:\d)\s(?=\d{3}(?!\d))", "", quote)
        # Extraction de PDF : espace avant la décimale (« 1 627 ,4 », AUGA, 17/10/2026).
        flat = re.sub(r"(\d) ([.,]\d)", r"\1\2", flat)
        target = fx_source if fx_source is not None else row.value_numeric
        variants = _value_variants(target)
        # Écart « en faveur des femmes » : publié en valeur absolue, compté négatif ;
        # ou en notation comptable entre parenthèses, « (8,0) % ».
        if row.value_numeric < 0 and re.search(
                r"in favou?r of women|en faveur des femmes|higher for (female|women)"
                r"|women (?:have been |were |are )?paid [\d.,]+ ?% more than men"
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
        # Part entre parenthèses suivie de « % » (« 9 out of 13 … independent (69.2%) ») :
        # ce n'est pas la notation comptable « (8,0) % », où la parenthèse fermante précède « % ».
        if row.value_numeric >= 0:
            pats += [rf"(?<![\d,])\({re.escape(c)}\s?%" for c in variants]
        hit = any(re.search(pt, flat) for pt in pats)
        # Colonnes voisines de 3 chiffres (« 345 352 ») : fusionnées à tort en un
        # seul nombre ; on accepte la valeur lue comme nombre isolé, la lecture des
        # colonnes étant écrite dans l'extrait.
        col = not hit and any(re.search(rf"(?:^|\s){pt}(?=\s|$)", quote) for pt in pats)
        cnt = (not hit and not col and row.indicator_code in ("GOV_BOARD_INDEP", "GOV_BOARD_GENDER")
               and _count_ratio_matches(row.value_numeric, quote))
        # « The Chair and all members of the Board of Directors are independent » : 100 %.
        tous = (not hit and not col and not cnt and row.indicator_code == "GOV_BOARD_INDEP"
                and row.value_numeric == 100 and _ALL_INDEP.search(quote) is not None)
        # « Absence d’administrateurs indépendants » : 0 %.
        aucun = (not hit and not col and not cnt and not tous and row.indicator_code == "GOV_BOARD_INDEP"
                 and row.value_numeric == 0 and _NO_INDEP.search(quote) is not None)
        # Valeur nulle écrite en toutes lettres (« l’alignement … reste nul en 2025 », Michelin, 17/10/2026).
        nul = (not hit and not col and not cnt and not tous and not aucun and row.value_numeric == 0
               and re.search(r"\bnul(?:le)?s?\b|\bz[ée]ro\b|\bnil\b", quote, re.I) is not None)
        ok &= hit or col or cnt or tous or aucun or nul
        details.append(f"valeur {target} présente dans la citation "
                       f"{'✓' if hit else '✓ (colonne isolée)' if col else '✓ (rapport des effectifs cités)' if cnt else '✓ (tous les membres déclarés indépendants)' if tous else '✓ (aucun membre indépendant déclaré)' if aucun else '✓ (valeur nulle écrite en toutes lettres)' if nul else '✗'}")
    elif row.value_boolean is not None:
        details.append("indicateur oui/non : la présence de la citation suffit")
    # Note normalisée imposée par le barème de l'indicateur : recalculée.
    rule = NORMALIZE.get(row.indicator_code)
    if rule and row.value_numeric is not None:
        expected = rule(row.value_numeric)
        norm_ok = row.normalized_value is not None and abs(expected - row.normalized_value) <= 0.002
        ok &= norm_ok
        details.append(f"note normalisée {row.normalized_value} = barème {round(expected, 3)} {'✓' if norm_ok else '✗'}")
    if row.indicator_code in PEER_RANKED and row.value_numeric is not None:
        peer_ok = row.normalized_value is None
        ok &= peer_ok
        details.append(f"pas de note précalculée (classement entre pairs) {'✓' if peer_ok else '✗'}")
    return Verdict("OK" if ok else "ÉCART", details)


_PRESSCORNER = re.compile(r"ec\.europa\.eu/commission/presscorner/detail/([a-z]{2})/([a-z]+)_(\d{2})_(\d+)", re.I)


def presscorner_text(url: str, client: httpx.Client) -> str | None:
    """Communiqué de la Commission européenne : la page publique est une application
    JavaScript ; son texte officiel est servi par l'interface du « press corner »
    (même référence, IP/25/1992). Titre, sous-titre et corps, balises retirées."""
    m = _PRESSCORNER.search(url)
    if not m:
        return None
    lang, kind, yy, num = m.groups()
    ref = f"{kind.upper()}/{yy}/{num}"
    r = client.get("https://ec.europa.eu/commission/presscorner/api/documents",
                   params={"reference": ref, "language": lang}, timeout=120,
                   headers={"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)"})
    r.raise_for_status()
    doc = r.json().get("docuLanguageResource") or {}
    raw = " ".join(str(doc.get(k) or "") for k in ("title", "subtitle", "htmlContent"))
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


_HAVEN_MARK = "tableaux des sociétés consolidées"


def document_raw(url: str, client: httpx.Client) -> str:
    """Document brut (balises conservées) : tableaux d'un rapport ESEF ou d'un paquet AMF."""
    ua = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}
    r = client.get(url, timeout=600, follow_redirects=True, headers=ua)
    r.raise_for_status()
    if url.lower().split("?")[0].endswith(".zip") or "zip" in r.headers.get("content-type", ""):
        import io
        import zipfile
        z = zipfile.ZipFile(io.BytesIO(r.content))
        name = max((i for i in z.infolist() if i.filename.lower().endswith((".xhtml", ".html"))),
                   key=lambda i: i.file_size).filename
        return z.read(name).decode("utf-8", errors="replace")
    page = r.text
    if "ixv-stub-viewer" in page:
        from urllib.parse import urljoin
        m = re.search(r'"docSetFiles"\s*:\s*\[\s*"([^"]+)"', page)
        if m:
            full = client.get(urljoin(url, m.group(1)), timeout=600, follow_redirects=True, headers=ua)
            if full.status_code == 200:
                page = full.text
    return page


def recount_havens(row, client: httpx.Client, raws: dict) -> tuple[bool, list[str]]:
    from .paradis_europe import compter, detail
    if row.source_url not in raws:
        raws[row.source_url] = document_raw(row.source_url, client)
    m = re.search(r"hors pays du siège \(([A-Z]{2})\)", row.excerpt or "")
    n, _, lignes = compter(raws[row.source_url], m.group(1) if m else None)
    total = sum(n.values())
    ok = row.value_numeric is not None and total == int(row.value_numeric) and total > 0
    return ok, [f"décompte refait : {total} filiales sur {lignes} lignes de tableau ({detail(n) or 'aucune'}) = valeur "
                f"{'✓' if ok else '✗'}"]


def document_text(url: str, client: httpx.Client) -> str:
    """Texte d'un document public (page web ou PDF), pour vérifier une citation."""
    pc = presscorner_text(url, client)
    if pc is not None:
        return pc
    from .connectors.sec import UA
    # Identifiant déclaré : certains sites refusent celui, par défaut, de la
    # bibliothèque HTTP ; la SEC exige le sien.
    # Même identité déclarée, avec « Accept: */* » : certains sites refusent une requête qui ne le
    # précise pas (Biscuiterie Husson, 16/10/2026).
    ua = UA if "sec.gov" in url else {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)",
                                      "Accept": "*/*"}
    r = client.get(url, timeout=300, follow_redirects=True, headers=ua)
    if r.status_code == 403:
        # Refus ponctuel au premier appel (DGCCRF) : une seule nouvelle demande, même identité.
        import time
        time.sleep(3)
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
        text = "\n".join(_page_text(p) for p in pypdf.PdfReader(io.BytesIO(r.content)).pages)
        if len(text.strip()) < 200:
            # PDF scanné, sans texte (arrêtés de Géorisques) : texte reconnu par OCR, le même que
            # celui de l'outil de collecte grâce au cache (16/10/2026).
            from .ocr import pdf_text_or_ocr
            text = pdf_text_or_ocr(r.content)[0]
        return text
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", r.text, flags=re.S)))


def _page_text(page) -> str:
    """Texte d'une page PDF ; une page dont un flux dépasse la limite de décompression de
    pypdf (image pleine page d'un rapport illustré) est ignorée plutôt que de faire échouer
    la lecture de tout le document : on ne cherche que des citations textuelles."""
    import pypdf
    try:
        return page.extract_text() or ""
    except pypdf.errors.LimitReachedError:
        return ""


#: Étiquette de relecture des preuves de tier 3 approuvées par délégation de
#: l'éditeur (« valide pour moi », 11/10/2026) : seulement vérifiées mot pour mot.
DELEGATED_REVIEWER = "delegue-editeur:verifie-mot-pour-mot"


def finalize(v: Verdict, note: str, tier: str | None, delegated: bool = False) -> Verdict:
    """Seul un OK sur source de tier 1-2, sans note de jugement, est approuvable.
    Avec la délégation de l'éditeur, un OK de tier 3 (rapport volontaire de
    l'entreprise) l'est aussi, sous une étiquette distincte ; jamais le tier « crowd »."""
    from .load import AUTO_PUBLISH_TIERS
    if v.status == "OK" and note:
        return Verdict("JUGEMENT", v.details + [f"signalé à la compilation : {note}"])
    if v.status == "OK" and tier == "press" and delegated:
        return Verdict("OK-DÉLÉGUÉ", v.details + ["tier 3 : approuvé par délégation de l'éditeur (vérifié mot pour mot)"])
    # Même vérifiée, une source de tier 3 / crowd passe par un humain (REVIEW_MODEL).
    if v.status == "OK" and tier not in AUTO_PUBLISH_TIERS:
        return Verdict("JUGEMENT", v.details + [f"source de tier « {tier} » : validation humaine requise"])
    return v


# --- Application ---------------------------------------------------------------
def approve(rows, reviewer: str = "auto:verify_curated") -> int:
    h = {"apikey": config.SUPABASE_SERVICE_ROLE_KEY, "Authorization": f"Bearer {config.SUPABASE_SERVICE_ROLE_KEY}",
         "Content-Type": "application/json"}
    base = f"{config.SUPABASE_URL}/rest/v1"
    n = 0
    with httpx.Client(timeout=60) as c:
        from .supabase_client import get_all
        ids = lambda t, k: {x[k]: x["id"] for x in get_all(c, t, {"select": f"id,{k}"}, h)}  # noqa: E731
        ents, inds, srcs = ids("entities", "slug"), ids("indicators", "code"), ids("sources", "code")
        for r in rows:
            resp = c.patch(f"{base}/evidence", headers={**h, "Prefer": "return=representation"},
                           params={"entity_id": f"eq.{ents[r.entity_slug]}", "indicator_id": f"eq.{inds[r.indicator_code]}",
                                   "source_id": f"eq.{srcs[r.source_code]}", "observed_on": f"eq.{r.observed_on}",
                                   # La citation vérifiée, et elle seule : sans ce filtre, une ancienne ligne
                                   # en attente (même marque, indicateur, source, date) serait approuvée à sa
                                   # place (lot 108, 15/10/2026).
                                   "excerpt": f"eq.{r.excerpt or ''}",
                                   "review_status": "eq.pending"},
                           json={"review_status": "approved", "reviewer": reviewer})
            resp.raise_for_status()
            n += len(resp.json())
    return n


def main() -> None:
    parser = argparse.ArgumentParser(description="Vérifie des preuves curées contre leur source primaire.")
    parser.add_argument("--file", required=True)
    parser.add_argument("--bocc-pdf", help="PDF des tableaux BOCC (sector-tables)")
    parser.add_argument("--apply", action="store_true", help="approuve les preuves OK encore en attente")
    parser.add_argument("--copie", action="append", default=[], metavar="URL=FICHIER",
                        help="copie locale d'une page dont le site refuse le vérificateur, obtenue sous la même "
                             "identité déclarée ; tous les contrôles s'y appliquent, l'approbation le mentionne")
    parser.add_argument("--delegue", action="store_true",
                        help="délégation de l'éditeur : approuve aussi les preuves de tier 3 vérifiées mot pour mot")
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

    ok_rows, delegated_rows, counts, reports = [], [], {}, {}
    raws: dict = {}
    copies = dict(c.split("=", 1) for c in args.copie)
    with httpx.Client(timeout=300) as client:
        for r, note in zip(rows, notes):
            if r.source_code == "BOCC" and tables:
                v = verify_bocc(r, tables)
            elif r.source_code == "HATVP":
                v = verify_hatvp(r, client, sirens)
            elif r.source_url and "«" in (r.excerpt or ""):
                # Citation verbatim d'un document public : rapport ESEF, page web ou PDF.
                if r.source_url not in reports and r.source_url in copies:
                    raw = open(copies[r.source_url], encoding="utf-8", errors="replace").read()
                    reports[r.source_url] = re.sub(r"\s+", " ", html.unescape(
                        re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", raw, flags=re.S)))
                    print(f"  copie locale lue : {copies[r.source_url]}")
                if r.source_url not in reports:
                    try:
                        if r.source_code == "ESEF":
                            from .connectors.esef import report_text
                            reports[r.source_url] = report_text(r.source_url, client)
                        else:
                            reports[r.source_url] = document_text(r.source_url, client)
                    except httpx.HTTPError as err:
                        # Source momentanément inaccessible (refus, délai) : la preuve reste
                        # en attente, les autres lignes sont vérifiées.
                        reports[r.source_url] = None
                        print(f"  source inaccessible ({type(err).__name__}) : {r.source_url}")
                if reports[r.source_url] is None:
                    v = Verdict("NON VÉRIFIABLE", ["source inaccessible au moment de la vérification"])
                    counts[v.status] = counts.get(v.status, 0) + 1
                    print(f"\n[{v.status}] {r.entity_slug} · {r.indicator_code} ({r.source_code})")
                    continue
                # Un cas signalé « jugement » (ex. définition voisine de l'indicateur)
                # est vérifié sur la citation et la valeur, puis rendu à l'humain.
                rates = {}
                fx = FX_RE.search(r.excerpt or "")
                if fx:
                    rates[(fx.group(3), fx.group(1))] = ecb_annual_rate(fx.group(3), fx.group(1), client)
                sm = _SANCTION_VT.search(r.value_text or "") if r.indicator_code == "GOV_SANCTIONS" else None
                if sm and sm.group(3) != "€":
                    cur, year = _DEVISES[sm.group(3)], sanction_rate_year(r)
                    # Année en cours : le taux annuel moyen n'est publié qu'en janvier suivant ;
                    # on prend alors celui de l'année précédente, et le contrôle le dit.
                    for y in (year, str(int(year) - 1)):
                        try:
                            rates[(cur, year)] = ecb_annual_rate(cur, y, client)
                            rates[("annee", cur, year)] = y
                            break
                        except Exception:
                            continue
                v = check_esef_quote(r, reports[r.source_url], ignore_keywords=bool(note), rates=rates)
                if r.indicator_code == "TAX_HAVEN_PRESENCE" and _HAVEN_MARK in (r.excerpt or ""):
                    try:
                        h_ok, h_details = recount_havens(r, client, raws)
                    except httpx.HTTPError as err:
                        h_ok, h_details = False, [f"rapport original inaccessible ({type(err).__name__}) ✗"]
                    v = Verdict(v.status if h_ok or v.status not in ("OK",) else "ÉCART", v.details + h_details)
            else:
                v = Verdict("NON VÉRIFIABLE", [f"aucun vérificateur pour la source {r.source_code}"])
            v = finalize(v, note, tiers.get(r.source_code), delegated=args.delegue)
            counts[v.status] = counts.get(v.status, 0) + 1
            print(f"\n[{v.status}] {r.entity_slug} · {r.indicator_code} ({r.source_code})")
            for d in v.details:
                print(f"    {d}")
            if v.status == "OK":
                ok_rows.append(r)
            elif v.status == "OK-DÉLÉGUÉ":
                delegated_rows.append(r)
    print("\nBilan : " + ", ".join(f"{k} {n}" for k, n in sorted(counts.items())))
    if args.apply and copies:
        # Vérifiées sur copie locale : la trace le dit (17/10/2026).
        cop = [r for r in ok_rows if r.source_url in copies]
        ok_rows = [r for r in ok_rows if r.source_url not in copies]
        if cop:
            print(f"Approuvées sur copie locale (auto:verify_curated:copie) : {approve(cop, 'auto:verify_curated:copie')}")
    if args.apply:
        print(f"Approuvées (auto:verify_curated) : {approve(ok_rows)}")
        if delegated_rows:
            print(f"Approuvées par délégation ({DELEGATED_REVIEWER}) : {approve(delegated_rows, DELEGATED_REVIEWER)}")
    else:
        print("(contrôle seulement : --apply approuve les seules preuves OK)")


if __name__ == "__main__":
    main()
