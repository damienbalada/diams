"""Normalisation de noms d'entreprises + matching conservateur.

Principe d'intégrité : on ne renseigne un identifiant (LEI/SIREN) que si le nom
correspond de façon nette. En cas de doute, on ne devine pas — on laisse vide et
on signale pour revue manuelle.
"""
from __future__ import annotations

import re
import unicodedata

# Formes juridiques à retirer pour comparer les noms. On NE retire PAS des mots
# porteurs de sens comme "international", "group", "holding" (risque de
# sur-correspondance).
LEGAL_SUFFIXES = {
    "se", "sa", "sas", "sasu", "sca", "snc", "sarl", "scs",
    "spa", "srl", "plc", "ltd", "limited", "llc", "inc", "corp",
    "gmbh", "ag", "nv", "bv", "co",
}


# Mots qui, seuls, ne désignent aucune entreprise en particulier.
GENERIC = {"group", "groupe", "international", "holding", "holdings", "company", "companies", "france",
           "industries", "corporation", "the", "de", "la", "le", "les", "et", "and", "of"}


def normalize_name(name: str, keep_letters: bool = False) -> str:
    """minuscule, sans accents, sans ponctuation ni suffixe juridique."""
    if not name:
        return ""
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    # Sigles à esperluette ou à points recollés avant de retirer la ponctuation : « H&M » -> « hm »,
    # « P&G » -> « pg », « S.p.A. » -> « spa » (16/10/2026 : « H&M Group » et « B&S Group » se
    # réduisaient tous deux à « group » et se correspondaient).
    s = re.sub(r"(?<![a-z0-9])[a-z0-9]{1,2}(?:\s*&\s*[a-z0-9]{1,2})+(?![a-z0-9])", lambda m: re.sub(r"\s*&\s*", "", m.group(0)), s)
    s = re.sub(r"(?<![a-z0-9])[a-z0-9](?:\.[a-z0-9])+(?![a-z0-9])", lambda m: m.group(0).replace(".", ""), s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    # on retire les tokens d'une seule lettre (issus d'abréviations à points,
    # ex: "S.p.A." -> "s p a") et les formes juridiques.
    if keep_letters:
        return " ".join(t for t in s.split() if len(t) == 1)
    tokens = [t for t in s.split() if len(t) > 1 and t not in LEGAL_SUFFIXES]
    return " ".join(tokens)


def is_strong_match(query: str, candidate: str) -> bool:
    """Vrai si les noms normalisés correspondent nettement (égalité ou inclusion)."""
    q = normalize_name(query)
    c = normalize_name(candidate)
    if not q or not c:
        return False
    # Un nom réduit à des mots génériques ne prouve rien (« Group », « International Holding »).
    if set(q.split()) <= GENERIC or set(c.split()) <= GENERIC:
        return False
    # Lettres isolées différentes de part et d'autre : deux noms distincts (« Bio-D » ≠ « U BIO »).
    lq, lc = normalize_name(query, keep_letters=True), normalize_name(candidate, keep_letters=True)
    if lq and lc and lq != lc:
        return False
    if q == c:
        return True
    # Inclusion tolérée seulement si le nom le plus court a >= 2 mots,
    # pour éviter qu'un mot unique (ex: "hermes") matche n'importe quoi.
    qt, ct = set(q.split()), set(c.split())
    smaller = qt if len(qt) <= len(ct) else ct
    if len(smaller) >= 2 and (qt.issubset(ct) or ct.issubset(qt)):
        return True
    return False


def best_match(query: str, candidates: list[dict], name_key: str) -> dict | None:
    """Retourne le 1er candidat en correspondance nette, sinon None (pas de devinette)."""
    for cand in candidates:
        if is_strong_match(query, cand.get(name_key) or ""):
            return cand
    return None
