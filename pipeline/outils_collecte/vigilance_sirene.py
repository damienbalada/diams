"""Obligation de plan de vigilance d'après l'effectif officiel (répertoire Sirene de l'Insee), 17/10/2026.

La loi n° 2017-399 (C. com. art. L225-102-4) vise les sociétés qui emploient au moins 5 000 salariés avec leurs
filiales françaises (ou 10 000 avec leurs filiales dans le monde). Une société française dont la tranche
d'effectif Sirene est, à elle seule, « 5 000 à 9 999 » (52) ou « 10 000 et plus » (53) dépasse donc le seuil.
Les sociétés de tête plus petites (holdings, coopératives) ne sont pas marquées : leur groupe peut dépasser le
seuil, mais le registre ne le prouve pas.

Lecture seule de l'annuaire officiel des entreprises (recherche-entreprises.api.gouv.fr) ; écrit une
migration SQL à relire puis appliquer.

Usage : python outils_collecte/vigilance_sirene.py migration.sql
"""
from __future__ import annotations

import os
import sys
import time

import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"), override=True)
from diams import supabase_client  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)"}
TRANCHES = {"52": "5 000 à 9 999 salariés", "53": "10 000 salariés et plus"}


def main() -> None:
    sortie = sys.argv[1]
    db = httpx.Client(verify=os.environ.get("SSL_CERT_FILE", True), timeout=60)
    web = httpx.Client(verify=os.environ.get("SSL_CERT_FILE", True), timeout=30, headers=UA)
    ents = supabase_client.get_all(db, "entities", {"select": "id,slug,siren,country", "siren": "not.is.null", "country": "eq.FR"})
    regimes = supabase_client.get_all(db, "disclosure_regimes", {"select": "id,code"})
    vig = next(r["id"] for r in regimes if r["code"] == "FR_VIGILANCE")
    deja = {r["entity_id"] for r in supabase_client.get_all(db, "entity_regimes", {"select": "entity_id", "regime_id": f"eq.{vig}", "order": "entity_id.asc"})}
    sirens = sorted({e["siren"] for e in ents if e["id"] not in deja})
    print(f"{len(sirens)} SIREN français à lire", flush=True)
    retenus = {}
    for i, s in enumerate(sirens):
        for essai in (1, 2):
            r = web.get("https://recherche-entreprises.api.gouv.fr/search", params={"q": s})
            if r.status_code == 429 and essai == 1:
                time.sleep(2)
                continue
            break
        time.sleep(0.15)
        if r.status_code != 200:
            print("   ", s, r.status_code)
            continue
        res = [x for x in r.json().get("results", []) if x.get("siren") == s]
        if not res:
            continue
        x = res[0]
        t = x.get("tranche_effectif_salarie")
        if t in TRANCHES:
            retenus[s] = (x.get("nom_raison_sociale") or x.get("nom_complet", ""), t, x.get("annee_tranche_effectif_salarie"))
            print(f"   {s} {x.get('nom_complet', '')[:50]} — {TRANCHES[t]} ({x.get('annee_tranche_effectif_salarie')})", flush=True)
        if i % 100 == 99:
            print(f"   … {i + 1} lus", flush=True)
    lignes = []
    for e in ents:
        if e["id"] in deja or e["siren"] not in retenus:
            continue
        nom, t, an = retenus[e["siren"]]
        base = (f"SIREN {e['siren']} ({nom}) : tranche d'effectif salarié « {TRANCHES[t]} » au répertoire Sirene de l'Insee ({an}), "
                f"au-delà du seuil de 5 000 salariés de la loi n° 2017-399 sur le devoir de vigilance (C. com. art. L225-102-4).")
        lignes.append(f"('{e['id']}', '{vig}', '{base.replace(chr(39), chr(39) * 2)}', 'https://annuaire-entreprises.data.gouv.fr/entreprise/{e['siren']}', '2026-10-17', 'auto:vigilance_sirene')")
    with open(sortie, "w", encoding="utf-8") as f:
        f.write("-- Obligation de plan de vigilance d'après l'effectif Sirene (outil pipeline/outils_collecte/vigilance_sirene.py, 17/10/2026).\n")
        f.write("-- Société française de 5 000 salariés ou plus à elle seule : soumise à la loi n° 2017-399 (C. com. art. L225-102-4).\n")
        if lignes:
            f.write("insert into entity_regimes (entity_id, regime_id, basis, source_url, observed_on, reviewer) values\n")
            f.write(",\n".join(lignes))
            f.write("\non conflict do nothing;\n")
    print(f"{len(lignes)} entités soumises ajoutées dans {sortie}")


if __name__ == "__main__":
    main()
