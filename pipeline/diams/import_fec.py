"""Financement politique aux États-Unis : contributions versées par le comité d'action politique
(PAC) d'une entreprise, d'après les fichiers publics de la Commission électorale fédérale (FEC).

Fichiers (domaine public) : registre des comités (cm26 : comité, type d'organisation, organisation
rattachée) et résumé des comités d'action politique (webk26 : total des contributions versées à
d'autres comités, dont les candidats, pour le cycle 2025-2026 à date).

Règles : seuls les comités dont l'organisation rattachée est une entreprise (ORG_TP = C) et dont le
nom correspond nettement à celui d'un groupe racine de l'Index ; plusieurs comités d'un même groupe
sont additionnés. Indicateur de contexte (aucune note), montant en dollars dans l'extrait.

Usage :
    python -m diams.import_fec --dir <dossier des fichiers>            # contrôle
    python -m diams.import_fec --dir <dossier des fichiers> --apply
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import os
import re
import zipfile

import httpx

from . import config, supabase_client
from .load import EvidenceRow, insert_evidence
from .normalize.names import normalize_name

REVIEWER = "auto:fec"
CYCLE = "2026"


# Suffixes admis après le nom du groupe : filiale américaine du groupe, forme juridique.
SUFFIXES = {"usa", "us", "north", "america", "americas", "inc", "llc", "corp", "corporation", "company", "co", "the", "holdings",
            "com", "services"}

# Comité sans organisation rattachée déclarée : nom de l'entreprise tiré du nom du comité
# (« KEURIG DR PEPPER INC. PAC », « YUM BRANDS INC. GOOD GOVERNMENT FUND »).
_PAC_TAIL = re.compile(r"[,.]?\s*(?:\(.*\)|POLITICAL ACTION COMMITTEE|PAC|GOOD GOVERNMENT FUND|SEPARATE SEGREGATED FUND|FEDERAL)\s*$", re.I)


def committee_company(cmte_name: str) -> str:
    s = cmte_name.strip()
    while True:
        s2 = _PAC_TAIL.sub("", s).strip()
        if s2 == s:
            return s
        s = s2


def same_company(group_name: str, connected: str) -> bool:
    """Nom identique, ou nom du groupe suivi d'une mention géographique ou juridique seulement
    (« Pernod Ricard USA LLC »). Exclut les homonymes partiels (« Heartland Coca-Cola Bottling »)."""
    # Apostrophe retirée avant normalisation : « McDonald's » = « MCDONALDS CORPORATION ».
    g, k = (normalize_name(re.sub(r"['’]", "", x)) for x in (group_name, connected))
    if not g or not k:
        return False
    if g == k:
        return True
    gw, kw = g.split(), k.split()
    return kw[:len(gw)] == gw and set(kw[len(gw):]) <= SUFFIXES


def read_zip(path: str) -> list[list[str]]:
    with zipfile.ZipFile(path) as z:
        name = z.namelist()[0]
        return [line.split("|") for line in io.TextIOWrapper(z.open(name), encoding="latin-1").read().splitlines()]


def main() -> None:
    ap = argparse.ArgumentParser(description="Contributions des comités d'action politique d'entreprise (FEC).")
    ap.add_argument("--dir", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    config.require_supabase()
    cm = read_zip(os.path.join(args.dir, f"cm{CYCLE[2:]}.zip"))
    webk = {r[0]: r for r in read_zip(os.path.join(args.dir, f"webk{CYCLE[2:]}.zip"))}
    # CMTE_ID, CMTE_NM, …, ORG_TP (12), CONNECTED_ORG_NM (13)
    corp = [r for r in cm if len(r) > 13 and r[12] == "C"]
    rattache = {r[0]: (r[13].strip() or committee_company(r[1])) for r in corp}
    c = httpx.Client(timeout=120)
    ents = supabase_client.get_all(c, "entities", {"select": "slug,display_name,legal_name,is_brand,parent_id,country"})
    roots = [e for e in ents if not e["is_brand"] and not e["parent_id"]]
    rows = []
    for e in roots:
        noms = {e["legal_name"], e.get("display_name") or e["legal_name"]}
        cmtes = [r for r in corp if any(same_company(n, rattache[r[0]]) for n in noms)]
        if not cmtes:
            continue
        total, details, fin = 0.0, [], ""
        for r in cmtes:
            k = webk.get(r[0])
            if not k:
                continue
            montant = float(k[22] or 0)   # CONTRIB_TO_OTHER_CMTE
            total += montant
            fin = max(fin, k[26])         # CVG_END_DT (MM/DD/YYYY)
            details.append(f"comité « {r[1].strip()} » ({r[0]}), rattaché à « {r[13].strip() or rattache[r[0]] + ' » (nom du comité, organisation non déclarée)'}{' »' if r[13].strip() else ''} : {montant:,.0f} $".replace(",", " "))
        if not details:
            continue
        observed = dt.datetime.strptime(fin, "%m/%d/%Y").date().isoformat() if fin else dt.date.today().isoformat()
        excerpt = (f"Commission électorale fédérale des États-Unis (FEC), fichiers publics du cycle 2025-2026 (registre des comités "
                   f"et résumé des comités d'action politique, données arrêtées au {fin}) : contributions versées à des candidats et "
                   f"à d'autres comités politiques — " + " ; ".join(details) + f". Total : {total:,.0f} $.".replace(",", " "))
        rows.append(EvidenceRow(entity_slug=e["slug"], indicator_code="GEO_POL_FINANCING", source_code="FEC", nature="result",
                                observed_on=observed, value_type="numeric", value_numeric=round(total, 2), confidence=0.9,
                                source_url=f"https://www.fec.gov/data/committee/{cmtes[0][0]}/", excerpt=excerpt, reviewer=REVIEWER))
        print(f"✔ {e['slug']} : {total:,.0f} $ ({len(details)} comité(s))")
    print(f"\n{len(rows)} groupes avec un comité d'entreprise")
    if args.apply and rows:
        stats = insert_evidence(rows)
        print(f"Insérées: {stats['inserted']} · ignorées: {stats['skipped']}")


if __name__ == "__main__":
    main()
