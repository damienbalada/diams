"""Import des fiches produits lues par ingredients.py (essai du 17/10/2026).

1. Chaque fiche est relue : la liste d'ingrédients doit figurer mot pour mot sur la page (accents et
   espaces normalisés) ; sinon la ligne reste en attente.
2. Les fiches sont écrites dans la table products (une ligne par marque et par page).
3. Pour chaque marque, un produit à ingrédient animal donne une ligne de preuve ANI_EXPLOITATION au
   format des lots (CSV), à importer puis vérifier avec import_curated / verify_curated.

Avec --matieres : fiches lues par compositions.py (vêtements, chaussures) ; la composition remplace la liste
d'ingrédients et les matières animales (laine, cuir, soie, duvet…) les ingrédients animaux.

Avec --copies DOSSIER : pages enregistrées par l'éditeur depuis son navigateur (« saved from url=… »), lues
à la place du site quand celui-ci refuse le vérificateur ; la fiche et la preuve le disent.

Champ « releve » d'une fiche : passage indiquant la matière, relevé à la lecture quand la page n'a pas de
rubrique « Composition » (descriptif de Louis Vuitton, ligne des matières de Saint Laurent) ; il n'est
retenu que s'il figure mot pour mot dans la page.

Usage : python outils_collecte/import_produits.py lecture.json lot.csv [--apply] [--matieres] [--copies DOSSIER]
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
import time
import unicodedata
from urllib.parse import urlparse

import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"), override=True)
sys.path.insert(0, os.path.dirname(__file__))
from diams import config, supabase_client  # noqa: E402
import compositions as C  # noqa: E402
import ingredients as I  # noqa: E402

JOUR = "2026-10-17"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s.replace("’", "'")).strip()


ALLERGENE = re.compile(r"\b(?:LAIT|CR[EÈ]ME|BEURRE|FROMAGES?|[ŒO]E?UFS?|POISSONS?|LACTOS[EÉ]RUM|LACTOSE)\b")


def extrait(ingr: str) -> str | None:
    """L'ingrédient animal le plus court de la liste, recopié tel quel entre deux virgules (ou un
    allergène en capitales, signe d'une vraie liste d'ingrédients étiquetée)."""
    propre = I.SANS_RE.sub(lambda m: " " * len(m.group(0)), I.TRACES_RE.sub(lambda m: " " * len(m.group(0)), ingr))
    items = []
    for m in I.ANIMAL_RE.finditer(propre):
        debut = ingr.rfind(", ", 0, m.start())
        debut = 0 if debut < 0 else debut + 2
        fin = ingr.find(", ", m.end())
        fin = len(ingr) if fin < 0 else fin
        q = ingr[debut:fin].strip(" ,.")
        if len(q) <= 160:
            # Allergène en capitales d'abord ; un mot seul (« beurre ») cède devant un ingrédient complet.
            items.append((0 if ALLERGENE.search(q) else 1, 0 if len(q) >= 12 else 1, len(q), q))
    return min(items)[3] if items else None


def extrait_matiere(compo: str) -> str | None:
    """La composition entière quand elle est courte ; sinon le plus court passage qui nomme une matière
    animale, recopié tel quel : coupé aux séparateurs de la page (virgule, tiret, nouvelle rubrique
    « Doublure : » ou « Rembourrage 90 % »). Un sigle (« version APA : ») n'ouvre pas de rubrique."""
    propre = C.IMITATION_RE.sub(lambda m: " " * len(m.group(0)), compo)
    if len(compo) <= 160 and C.ANIMAL_RE.search(propre):
        return compo.strip(" ,.-")
    rubrique = r"\s(?=[A-ZÉ][a-zà-ÿ][\w’' ]{1,30}\s?:\s|(?:Ext[ée]rieur|Rembourrage|Garnissage|Doublure|Poches?|Coquille \d|Capuche|Col|Empi[èe]cements?)\s\d)"
    # Rubrique entière d'abord (« Garnissage du buste: 90% Duvet d’oie, 10% Plume d’oie ») ; les virgules
    # ne coupent qu'à défaut, pour ne pas citer « 10% Plume d’oie » seul.
    for sep in (r";\s|\s-\s|" + rubrique, r",\s|;\s|\s-\s|" + rubrique):
        coupes = [0] + [m.end() for m in re.finditer(sep, compo)] + [len(compo)]
        items = []
        for m in C.ANIMAL_RE.finditer(propre):
            debut = max(x for x in coupes if x <= m.start())
            fin = min(x for x in coupes if x >= m.end())
            q = compo[debut:fin].strip(" ,.;-")
            if 3 <= len(q) <= 160:
                items.append((0 if re.search(r"\d\s?%", q) else 1, len(q), q))
        if items:
            return min(items)[2]
    return None


def main() -> None:
    lecture, sortie, *opts = sys.argv[1:]
    appliquer = "--apply" in opts
    matieres = "--matieres" in opts
    copies = {}
    if "--copies" in opts:
        dossier = opts[opts.index("--copies") + 1]
        for nom in sorted(os.listdir(dossier)):
            if nom.endswith((".html", ".htm")):
                chemin = os.path.join(dossier, nom)
                if m := re.search(r"saved from url=\(\d+\)(\S+)", open(chemin, encoding="utf-8", errors="replace").read(4000)):
                    copies[m.group(1)] = chemin
    M = C if matieres else I
    config.require_supabase()
    lus = json.load(open(lecture, encoding="utf-8"))
    c = httpx.Client(verify=os.environ.get("SSL_CERT_FILE", True), timeout=40, follow_redirects=True, headers=I.UA)
    # La base refuse la clé secrète derrière un en-tête de navigateur : client distinct, sans « Mozilla ».
    db = httpx.Client(verify=os.environ.get("SSL_CERT_FILE", True), timeout=60)
    ents = {e["slug"]: e for e in supabase_client.get_all(db, "entities", {"select": "id,slug,display_name"})}
    lignes, preuves, vues = [], {}, set()
    for r in lus:
        # Même produit publié à deux adresses (« Boisson végétale amande 1L ») : une seule fiche.
        cle = (r["slug"], norm(r["produit"]))
        if r["slug"] not in ents or r["url"] in vues or cle in vues:
            continue
        vues.add(r["url"])
        vues.add(cle)
        copie = copies.get(r["url"])
        try:
            if copie:
                page = I.texte(open(copie, encoding="utf-8", errors="replace").read())
                print("   copie lue :", os.path.basename(copie))
            else:
                rep = c.get(r["url"])
                time.sleep(0.4)
                if rep.status_code in (401, 403, 429):
                    # Refus du site : on n'insiste pas, la fiche n'est pas importée.
                    print("   refus", rep.status_code, r["url"])
                    continue
                page = I.texte(rep.text)
        except Exception as e:
            print("   injoignable", r["url"], type(e).__name__)
            continue
        releve = r.get("releve")
        ingr = releve or (C.bloc_composition(page) if matieres else I.bloc_ingredients(page))
        mot_pour_mot = bool(ingr) and norm(ingr) in norm(page)
        a = M.analyse(ingr) if ingr else {"animaux": [], "douteux": [], "statut": "aucun_ingredient_animal_declare"}
        statut, preuve_veg = a["statut"], None
        # Produit présenté comme végétal par son nom (« Boisson végétale », « vegan ») : déclaré, non certifié.
        if not matieres and statut != "ingredient_animal" and re.search(r"v[ée]g[ée]tal|vegan|v[ée]gan", r["produit"], re.I):
            statut, preuve_veg = "vegetal_declare", f"Nom du produit sur le site de la marque : « {r['produit']} »"
        lignes.append({
            "entity_id": ents[r["slug"]]["id"], "name": r["produit"][:200] or r["url"], "source_url": r["url"],
            "ingredients": ingr, "animal_ingredients": a["animaux"], "doubtful_ingredients": a["douteux"],
            "status": statut, "vegetal_proof": preuve_veg, "observed_on": JOUR,
            "nature": "composition" if matieres else "ingredients",
            "reviewer": (("auto:releve-mot-pour-mot" if releve else "auto:composition-mot-pour-mot" if matieres else "auto:ingredients-mot-pour-mot")
                         + (":copie" if copie else "")) if mot_pour_mot else None,
            "review_status": "approved" if mot_pour_mot else "pending",
        })
        print(f"   {'✓' if mot_pour_mot else '…'} {statut:32} {r['slug']:16} {r['produit'][:50]}")
        if mot_pour_mot and statut == "ingredient_animal":
            q = extrait_matiere(ingr) if matieres else extrait(ingr)
            rang = (0 if q and (matieres or ALLERGENE.search(q)) else 1, 0 if len(q or "") >= 12 else 1, len(q or ""))
            if q and (r["slug"] not in preuves or rang < preuves[r["slug"]]["_rang"]):
                dom = urlparse(r["url"]).netloc.removeprefix("www.")
                preuves[r["slug"]] = {
                    "entity_slug": r["slug"], "indicator_code": "ANI_EXPLOITATION", "source_code": "COMPANY_REPORT",
                    "nature": "result", "observed_on": JOUR, "value_type": "category", "value_numeric": "",
                    "value_boolean": "", "value_text": ", ".join(a["animaux"][:4]), "normalized_value": "0",
                    "confidence": "0.85", "source_url": r["url"],
                    "excerpt": (f"Site officiel de la marque ({dom}), fiche produit « {r['produit']} », {'matière indiquée' if releve else 'composition' if matieres else 'liste des ingrédients'}, "
                                f"consultée le 17/10/2026{' (copie de la page enregistrée par l’éditeur, le site refusant le vérificateur)' if copie else ''} : « {q} » — recours à l'exploitation animale ({', '.join(a['animaux'][:4])})."),
                    "review_note": "", "_rang": rang,
                }
    print(f"{len(lignes)} fiches, dont {sum(l['review_status'] == 'approved' for l in lignes)} relues mot pour mot ; "
          f"{len(preuves)} marques avec un ingrédient animal")
    with open(sortie, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[k for k in next(iter(preuves.values())) if k != "_rang"] if preuves else ["entity_slug"], lineterminator="\n")
        w.writeheader()
        w.writerows({k: v for k, v in p.items() if k != "_rang"} for p in preuves.values())
    if not appliquer:
        print("(simulation : rien n'est écrit en base)")
        return
    r = db.post(f"{config.SUPABASE_URL}/rest/v1/products", params={"on_conflict": "entity_id,source_url"},
               headers={**supabase_client._headers(), "Prefer": "resolution=merge-duplicates,return=minimal"}, json=lignes)
    r.raise_for_status()
    print(f"{len(lignes)} fiches écrites dans products")
    # Les fiches de ces marques qui ne sont plus retenues (doublon d'adresse) sont retirées.
    for eid in {l["entity_id"] for l in lignes}:
        garder = {l["source_url"] for l in lignes if l["entity_id"] == eid}
        anciens = supabase_client.get_all(db, "products", {"select": "id,source_url", "entity_id": f"eq.{eid}"})
        retirer = [x["id"] for x in anciens if x["source_url"] not in garder]
        if retirer:
            db.delete(f"{config.SUPABASE_URL}/rest/v1/products", params={"id": f"in.({','.join(retirer)})"},
                      headers=supabase_client._headers()).raise_for_status()
            print(f"   {len(retirer)} fiche(s) en double retirée(s)")


if __name__ == "__main__":
    main()
