"""Connecteur BDIF (AMF) — documents d'enregistrement universel déposés.

Base des décisions et informations financières de l'Autorité des marchés
financiers. On cherche le document d'enregistrement universel (DEU) d'un
exercice ; l'émetteur déclaré au dépôt doit correspondre à l'entité (contrôlé
par le compilateur, comme pour un SIREN).
"""
from __future__ import annotations

from dataclasses import dataclass

import httpx

API = "https://bdif.amf-france.org/back/api/v1"


@dataclass
class Urd:
    number: str
    issuer: str
    fiscal_year: int
    filed: str
    pdf_url: str            # notice de dépôt (quelques pages)
    esef_url: str | None    # paquet ESEF : le document complet (rapport .xhtml)


def find_urd(query: str, fiscal_year: int, client: httpx.Client, issuer: str | None = None) -> list[Urd]:
    """DEU de l'exercice `fiscal_year` trouvés par `query` (émetteur ou numéro) ;
    avec `issuer`, seul l'émetteur de ce nom exact (déclaré au dépôt) est gardé."""
    r = client.get(f"{API}/informations", params={"RechercheTexte": query, "TypesDocument": "DocumentEnregistrementUniversel",
                                                  "From": 0, "Size": 50},
                   headers={"Accept": "application/json"})
    r.raise_for_status()
    out: list[Urd] = []
    for x in r.json().get("result", []):
        if "DocumentEnregistrementUniversel" not in (x.get("typesDocument") or []) or x.get("anneeComptable") != fiscal_year:
            continue
        pdf = next((d for d in x.get("documents", []) if d.get("format") == "PDF" and d.get("accessible")), None)
        esef = next((d for d in x.get("documents", []) if d.get("format") == "ZIP" and d.get("accessible")), None)
        name = next((s["raisonSociale"] for s in x.get("societes", []) if s.get("role") == "Emetteur"), "")
        if pdf and (issuer is None or issuer.upper() == name.upper()):
            out.append(Urd(number=x["numero"], issuer=name, fiscal_year=fiscal_year,
                           filed=(x.get("dateAction") or x.get("datePublication") or "")[:10],
                           pdf_url=f"{API}/documents/{pdf['path']}",
                           esef_url=f"{API}/documents/{esef['path']}" if esef else None))
    return out
