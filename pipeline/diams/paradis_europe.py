"""Présence des groupes européens dans le top 10 de l'indice des paradis fiscaux pour les entreprises
(Corporate Tax Haven Index du Tax Justice Network, édition du 2 décembre 2025), d'après les tableaux
des sociétés consolidées de leur rapport annuel (ESEF xhtml ou paquet déposé à l'AMF).

Règles (décision de l'éditeur, 17/10/2026), mêmes principes que l'annexe 21 des groupes américains :
  - une ligne de tableau compte si son premier champ est une société (forme juridique, ou pourcentage
    de détention d'au moins 50 %), et si le premier champ « pays » de la ligne est l'une des dix
    juridictions (pays d'immatriculation, avant un éventuel pays d'activité) ;
  - exclus : pays du siège, succursales, sociétés mises en équivalence et coentreprises, détention de
    l'exercice inférieure à 50 %, lignes d'emprunts (« En millions de… »), doublons ;
  - le rapport peut ne lister que les principales sociétés : la valeur est un minimum, jamais un zéro
    publié (un tableau illisible ne prouve pas l'absence).
Le vérificateur refait ce décompte depuis le rapport original.
"""
from __future__ import annotations

import html
import re
from collections import Counter

from .import_paradis_fiscaux import TOP10

FR = {"VG": r"[ÎI]les? Vierges britanniques", "KY": r"[ÎI]les? Ca[ïi]mans?", "CH": r"Suisse", "BM": r"Bermudes?",
      "SG": r"Singapour", "HK": r"Hong[- ]Kong", "NL": r"Pays[- ]Bas", "JE": r"Jersey", "IE": r"Irlande", "LU": r"Luxembourg"}
PAT = {code: re.compile(rf"^(?:{en}|{FR[code]})$", re.I) for _, code, _, en in TOP10}
NOMS = {code: nom for _, code, nom, _ in TOP10}
PAYS = """Afrique du Sud|South Africa|Algérie|Algeria|Allemagne|Germany|Angola|Arabie saoudite|Saudi Arabia|Argentine|Argentina|Australie|Australia|Autriche|Austria|Belgique|Belgium|Brésil|Brazil|Bulgarie|Bulgaria|Cameroun|Cameroon|Canada|Chili|Chile|Chine|China|Colombie|Colombia|Corée du Sud|Corée|South Korea|Korea|Côte d'Ivoire|Ivory Coast|Croatie|Croatia|Danemark|Denmark|Égypte|Egypt|Émirats arabes unis|United Arab Emirates|Espagne|Spain|Estonie|Estonia|États-Unis|Etats-Unis|United States|USA|U.S.A.|Finlande|Finland|France|Gabon|Ghana|Grèce|Greece|Guyana|Hongrie|Hungary|Inde|India|Indonésie|Indonesia|Irak|Iraq|Iran|Israël|Israel|Italie|Italy|Japon|Japan|Kazakhstan|Kenya|Lettonie|Latvia|Liban|Lebanon|Lituanie|Lithuania|Malaisie|Malaysia|Maroc|Morocco|Mexique|Mexico|Mozambique|Nigéria|Nigeria|Norvège|Norway|Nouvelle-Zélande|New Zealand|Oman|Ouganda|Uganda|Pakistan|Panama|Pérou|Peru|Philippines|Pologne|Poland|Portugal|Qatar|République tchèque|Czech Republic|Czechia|Roumanie|Romania|Royaume-Uni|United Kingdom|UK|Russie|Russia|Sénégal|Senegal|Serbie|Serbia|Slovaquie|Slovakia|Slovénie|Slovenia|Suède|Sweden|Taïwan|Taiwan|Tanzanie|Tanzania|Thaïlande|Thailand|Tunisie|Tunisia|Turquie|Türkiye|Turkey|Ukraine|Uruguay|Venezuela|Viêt Nam|Vietnam|Viet Nam|Yémen|Yemen|Brunei|Chypre|Cyprus|Malte|Malta|Monaco|Maurice|Mauritius|Liechtenstein|Andorre|Islande|Iceland|Irlande du Nord|Northern Ireland|Écosse|Scotland|Porto Rico|Puerto Rico|Bahreïn|Bahrain|Koweït|Kuwait|Jordanie|Jordan|Azerbaïdjan|Azerbaijan|Congo|RDC|Bénin|Benin|Togo|Mali|Burkina Faso|Madagascar|Zambie|Zambia|Botswana|Namibie|Namibia|Équateur|Ecuador|Bolivie|Bolivia|Paraguay|Costa Rica|Guatemala|Cuba|Jamaïque|Jamaica|Trinité-et-Tobago|Trinidad and Tobago|Sri Lanka|Bangladesh|Cambodge|Cambodia|Myanmar|Mongolie|Mongolia|Macao|Macau|Belarus|Biélorussie|Géorgie|Georgia|Arménie|Armenia|Ouzbékistan|Uzbekistan|Albanie|Albania|Bosnie-Herzégovine|Macédoine du Nord|Monténégro|Kosovo|Moldavie|Moldova|Guernesey|Guernsey|Île de Man|Isle of Man|Gibraltar|Bahamas|Barbade|Barbados|Curaçao|Antilles néerlandaises|Nouvelle-Calédonie|Polynésie française|Réunion|Martinique|Guadeloupe|Guyane"""
_PAYS_RX = re.compile("^(?:" + PAYS.replace(".", "\.") + ")$", re.I)
_FORME = re.compile(r"\b(?:S\.?A\.?S?|SAS|SARL|Sarl|S\.?à r\.?l\.?|S\.?r\.?l\.?|B\.?V\.?|N\.?V\.?|Ltd\.?|Limited|LLC|Inc\.?|GmbH|AG|PTE|Pte|Company|Unlimited|Holdings?|S\.?p\.?A\.?|SE|Plc|PLC|Co\.?|Corp(?:oration)?|K\.?K\.?|ApS|A/S|AB|Oy|SCS|SNC)\b", re.I)
_PCT = re.compile(r"\d{1,3}(?:[.,]\d+)?\s?%?")
_MEE = {"E", "ME", "MEE", "JV", "EQ", "Equity", "Mise en équivalence", "Equity method"}


def rows_of(raw: str) -> list[list[str]]:
    out = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", raw, flags=re.S | re.I):
        cells = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", td))).strip()
                 for td in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, flags=re.S | re.I)]
        cells = [c for c in cells if c]
        if len(cells) >= 2:
            out.append(cells)
    return out


def _est_pays(c: str) -> bool:
    return bool(_PAYS_RX.match(c)) or any(rx.match(c) for rx in PAT.values())


def compter(raw: str, home: str | None) -> tuple[Counter, dict[str, list[str]], int]:
    """Filiales par juridiction du top 10, citations (cellules jusqu'au pays), nombre de lignes lues."""
    rows = rows_of(raw)
    n: Counter = Counter()
    cit: dict[str, list[str]] = {}
    vus = set()
    for cells in rows:
        nom = cells[0]
        if not re.search(r"[A-Za-z]{3}", nom) or re.match(r"^[\d\s.,%()-]+$", nom) or _est_pays(nom):
            continue
        if re.search(r"succ\.|succursale|\bbranch\b", nom, re.I):
            continue
        if re.match(r"(?:En|In) (?:millions|milliards|thousands|billions)|Montant", nom, re.I):
            continue
        if any(c.strip() in _MEE for c in cells[1:]):
            continue
        pcts = [float(c.replace(",", ".").rstrip(" %")) for c in cells[1:] if _PCT.fullmatch(c)]
        pcts = [x for x in pcts if 0 <= x <= 100]
        if pcts and pcts[0] < 50:
            continue
        pays = next((c for c in cells[1:] if _est_pays(c)), None)
        if not pays:
            continue
        code = next((k for k, rx in PAT.items() if rx.match(pays)), None)
        if not code or code == home:
            continue
        if not (_FORME.search(nom) or (pcts and pcts[0] >= 50)):
            continue
        cle = (re.sub(r"[^a-z0-9]", "", nom.lower()), code)
        if cle in vus:
            continue
        vus.add(cle)
        n[code] += 1
        cit.setdefault(code, []).append(" ".join(cells[:cells.index(pays) + 1]))
    return n, cit, len(rows)


def detail(n: Counter) -> str:
    return " ; ".join(f"{NOMS[c]} {v}" for c, v in sorted(n.items(), key=lambda x: -x[1]))
