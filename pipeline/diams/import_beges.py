"""Émissions indirectes (scope 3) publiées, d'après les bilans d'émissions de gaz à effet de serre
déposés sur la plateforme de l'Ademe (jeu ouvert « Bilan GES », Licence Ouverte 2.0).

Règle : on prend, pour chaque groupe racine français, le dernier bilan déposé sous son SIREN au
format actuel (méthode BEGES v5, année de reporting 2021 ou après), qui impose de publier les
émissions indirectes significatives (catégories 3 à 6). Le bilan les chiffre : ENV_SCOPE3_DISCLOSED
vrai ; il ne les chiffre pas : faux. Un bilan ancien (v4) ne dit rien. Le bilan couvre la société
déclarante (SIREN), pas forcément tout le groupe : l'extrait le dit.

Usage :
    python -m diams.import_beges              # contrôle
    python -m diams.import_beges --apply      # écrit (source réglementaire : publiée)
    python -m diams.import_beges --absences --apply   # consigne aussi les groupes sans bilan
"""
from __future__ import annotations

import argparse
import datetime as dt
import urllib.parse as up

import httpx

from . import config, supabase_client
from .load import EvidenceRow, insert_evidence

DATASET = "https://data.ademe.fr/data-fair/api/v1/datasets/9nd9avrbto3l14md-wkode4o/lines"
REVIEWER = "auto:beges"
SCOPE12 = ["p11", "p12", "p13", "p14", "p15", "p21", "p22"]
SCOPE3 = ["p31", "p32", "p33", "p34", "p35", "p41", "p42", "p43", "p44", "p45", "p51", "p52", "p53", "p54", "p61"]


GROUPES = {3: ["p31", "p32", "p33", "p34", "p35"], 4: ["p41", "p42", "p43", "p44", "p45"],
           5: ["p51", "p52", "p53", "p54"], 6: ["p61"]}
CATEGORIES = {3: "transport (catégorie 3)", 4: "produits et services achetés (catégorie 4)",
              5: "utilisation des produits vendus (catégorie 5)", 6: "autres émissions indirectes (catégorie 6)"}


def total(rec: dict, postes: list[str]) -> float:
    return sum(float(rec.get(f"emissions_publication_{p}") or 0) for p in postes)


def latest_v5(records: list[dict]) -> dict | None:
    v5 = [r for r in records if r.get("methode_beges_v4v5") == "v5" and int(r.get("annee_de_reporting") or 0) >= 2021]
    return max(v5, key=lambda r: (int(r.get("annee_de_reporting") or 0), r.get("date_de_publication") or ""), default=None)


def build_rows(groups: list[dict], by_siren: dict[str, list[dict]], documented: set[str], today: str) -> list[EvidenceRow]:
    rows = []
    for g in groups:
        rec = latest_v5(by_siren.get(str(g["siren"]), []))
        if not rec or g["slug"] in documented:
            continue
        s3 = total(rec, SCOPE3)
        date = (rec.get("date_de_publication") or "")[:10]
        # Pas de tonnage dans l'extrait : certaines déclarations comportent des erreurs d'unité manifestes
        # (Delpeyrat : 5,8 Mt pour ses seules émissions directes). On dit seulement quelles catégories
        # d'émissions indirectes le bilan chiffre.
        cats = [CATEGORIES[k] for k, postes in GROUPES.items() if total(rec, postes) > 0]
        excerpt = (f"Bilan d'émissions de gaz à effet de serre de {rec.get('raison_sociale')} (SIREN {g['siren']}), déposé sur la "
                   f"plateforme de l'Ademe le {'/'.join(reversed(date.split('-')))}, année de reporting {rec.get('annee_de_reporting')}, "
                   f"méthode BEGES v5, périmètre de la société déclarante : émissions indirectes (scope 3) "
                   + (f"chiffrées pour : {', '.join(cats)}." if s3 > 0 else "non chiffrées (catégories 3 à 6 vides)."))
        rows.append(EvidenceRow(
            entity_slug=g["slug"], indicator_code="ENV_SCOPE3_DISCLOSED", source_code="ADEME_BEGES", nature="result",
            observed_on=date or today, value_type="boolean", value_boolean=s3 > 0, normalized_value=1.0 if s3 > 0 else 0.0,
            confidence=0.9, source_url=f"{DATASET}?qs=id:%22{up.quote(str(rec.get('id')))}%22", excerpt=excerpt, reviewer=REVIEWER))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description="Scope 3 publié, d'après les bilans GES de l'Ademe.")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--absences", action="store_true", help="consigne les groupes sans bilan v5 (journal)")
    args = ap.parse_args()
    config.require_supabase()
    c = httpx.Client(timeout=120)
    recs, after = [], None
    while True:
        p = {"size": 2000, **({"after": after} if after else {})}
        r = c.get(DATASET, params=p)
        r.raise_for_status()
        d = r.json()
        recs += d["results"]
        after = up.parse_qs(up.urlparse(d.get("next") or "").query).get("after", [None])[0]
        if not d["results"] or not after:
            break
    by_siren: dict[str, list[dict]] = {}
    for x in recs:
        by_siren.setdefault(str(x.get("siren_principal") or ""), []).append(x)
    ents = supabase_client.get_all(c, "entities", {"select": "id,slug,siren,is_brand,parent_id"})
    groups = [e for e in ents if not e["is_brand"] and not e["parent_id"] and e.get("siren")]
    ind = supabase_client.get_all(c, "indicators", {"select": "id,code", "code": "eq.ENV_SCOPE3_DISCLOSED"})[0]["id"]
    ev = supabase_client.get_all(c, "evidence", {"select": "entity_id", "indicator_id": f"eq.{ind}",
                                                  "review_status": "in.(approved,pending)"})
    slug_by_id = {e["id"]: e["slug"] for e in ents}
    documented = {slug_by_id.get(r["entity_id"]) for r in ev}
    today = dt.date.today().isoformat()
    rows = build_rows(groups, by_siren, documented, today)
    print(f"{len(recs)} bilans lus ; {len(rows)} preuves ({sum(1 for r in rows if r.value_boolean)} avec scope 3 chiffré)")
    for r in rows[:15]:
        print("  ", r.entity_slug, "|", r.excerpt[-110:])
    if args.apply and rows:
        stats = insert_evidence(rows)
        print(f"Insérées: {stats['inserted']} · ignorées: {stats['skipped']}")
    if args.absences:
        from .relecture import write_reviews
        sans = [g for g in groups if not latest_v5(by_siren.get(str(g["siren"]), [])) and g["slug"] not in documented]
        reviews = [{"entity_id": g["id"], "indicator_id": ind, "evidence_id": None, "outcome": "non_trouvee",
                    "detail": f"Cherché, non trouvé : aucun bilan d'émissions de GES au format actuel (v5) déposé sous ce SIREN "
                              f"sur la plateforme de l'Ademe (jeu ouvert relu le {dt.date.today().strftime('%d/%m/%Y')}).",
                    "source_url": "https://data.ademe.fr/datasets/9nd9avrbto3l14md-wkode4o", "reviewer": REVIEWER, "wave": None}
                   for g in sans]
        print(f"{len(reviews)} groupes sans bilan v5")
        if args.apply and reviews:
            print("consignées :", write_reviews(c, reviews))


if __name__ == "__main__":
    main()
