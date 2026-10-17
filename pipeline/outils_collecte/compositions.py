"""Lecture des compositions sur les fiches produits des sites de marques de mode (17/10/2026).

Même démarche que ingredients.py : plan du site (ou catalogue rendu par un navigateur) → fiches produits
→ bloc « Composition » de la page → matières d'origine animale repérées (laine, cuir, soie, duvet…).
Lecture seule ; écrit un JSON de constats relus avant tout import (import_produits.py --matieres).
Les imitations (similicuir, fausse fourrure, laine polaire, peau de pêche…) sont écartées avant la
recherche : ce sont des matières synthétiques ou des finitions, pas des matières animales.

Usage : python outils_collecte/compositions.py sortie.json "slug|https://domaine/sitemap.xml|motif d'URL produit|max" …
        avec --navigateur : « slug|page catalogue|motif|max », pages rendues par un navigateur sans affichage
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import unicodedata

import httpx

sys.path.insert(0, os.path.dirname(__file__))
import ingredients as I  # noqa: E402

# Matières d'origine animale (français, puis anglais pour les sites qui ne traduisent pas la composition).
ANIMAL = [
    r"laine", r"m[ée]rinos", r"cachemire", r"mohair", r"angora", r"alpaga", r"lama", r"yacks?", r"yaks?", r"vigogne",
    r"chameau", r"poils? de \w+", r"soie", r"cuir", r"daim", r"nubuck", r"cro[ûu]te de cuir", r"peau(?:x)?(?: lain[ée]e| d.agneau| de mouton| de ch[èe]vre| de veau| de vache)?",
    r"fourrure", r"duvet", r"plumes?", r"lapin", r"vison", r"renard", r"crocodile", r"python", r"autruche", r"l[ée]zard", r"galuchat",
    r"\bcorne\b", r"nacre", r"shearling",
    r"wool", r"merino", r"cashmere", r"silk", r"leather", r"suede", r"\bdown\b", r"feathers?", r"\bfur\b",
]
ANIMAL_RE = re.compile(r"\b(?:" + "|".join(ANIMAL) + r")\b", re.I)
# Imitations et faux amis, retirés avant la recherche.
IMITATION_RE = re.compile(
    r"similicuir|simili[- ]?cuir|simili\b|cuir (?:synth[ée]tique|v[ée]g[ée]tal|vegan|recycl[ée] synth\w*)|imitation (?:cuir|daim|fourrure|laine)|"
    r"(?:fausse|fake) fourrure|fourrure (?:synth[ée]tique|artificielle|en polyester)|faux (?:cuir|daim)|daim synth[ée]tique|su[ée]dine|"
    r"laine polaire|polaire|peau de p[êe]che|effet (?:cuir|daim|fourrure|laine)|aspect (?:cuir|daim|fourrure|laine)|toucher (?:cuir|daim|soie|laine)|"
    r"fa[çc]on (?:cuir|daim|fourrure)|soie v[ée]g[ée]tale|plumetis|sans (?:laine|cuir|duvet|plumes?|fourrure|soie)(?:(?:,| ni| et| ou) (?:laine|cuir|duvet|plumes?|fourrure|soie))*|"
    r"vegan leather|faux leather|faux fur|synthetic (?:leather|fur|down)|recycled polyester down",
    re.I,
)
VEGETAL_RE = re.compile(r"\b(?:100 ?% v[ée]g[ée]tal\w*|v[ée]gan\w*|vegan|PETA[- ]approved|sans mati[èe]re animale)", re.I)

# Bloc de composition : « Composition », « Matières », « Tissu principal », « Extérieur », jusqu'à la rubrique suivante.
_BLOC = re.compile(
    r"(?:Composition(?:\s+et\s+entretien)?|Mati[èe]res?(?:\s+principales?)?|Tissu principal|Mati[èe]re ext[ée]rieure|Ext[ée]rieur|Dessus)\s*:?\s*"
    r"(.{8,600}?)(?=\s(?:\d{2}\s?°C|Instructions|Qualit[ée]s? et caract[ée]ristiques|Fiche produit|Caract[ée]ristiques|Entretien|Conseils? d.entretien|Lavage|Lavable|Ne pas|Origine|Fabriqu[ée] (?:en|au)|Pays de fabrication|R[ée]f[ée]rence|"
    r"Ajouter au panier|Livraison|Guide des tailles|Taille|Hauteur du talon|Code mod[èe]le|Coupe|Description|Avis|Retours?|Couleur)\b|$)",
    re.I,
)
# Une composition liste des pourcentages de fibres (« 80 % laine, 20 % polyamide ») ou nomme une matière.
FIBRES = re.compile(r"\d{1,3}\s?%|\b(?:coton|polyester|polyamide|[ée]lasthanne|viscose|lin|laine|cuir|soie|acrylique|nylon|lyocell|modal|chanvre|duvet|plumes?|cachemire|"
                    r"cotton|polyamide|elastane|wool|leather|silk)\b", re.I)


def bloc_composition(t: str) -> str | None:
    """Le bloc de composition le plus fourni (pourcentages et fibres) de la page, ou rien. Les titres de
    menu (« Matières » dans la navigation) et les phrases de présentation sont écartés."""
    # Sans les intitulés de rubrique restés en tête (« et entretien Matières », « Composition »).
    # « Composition du manteau court : 80 % laine… » (Chloé) : le nom de la pièce part avec l'intitulé.
    tete = re.compile(r"^(?:(?:et entretien|Composition|Mati[èe]res\b|(?:du|de la|de l’|des)\s[^:%]{3,40}?\s:)\s*:?\s*)+", re.I)
    blocs = [tete.sub("", m.group(1).strip(" :-–")) for m in _BLOC.finditer(t)]
    # Bloc ouvert sur une phrase de présentation (« la meilleure matière… ») qui contient plus loin la
    # rubrique « Composition : » (Salomon) : seule la rubrique est gardée.
    blocs = [b[m.end():].strip() if (m := re.search(r"\bComposition\s*:\s*", b)) and m.start() > 0 else b for b in blocs]
    def note(b: str) -> int:
        return 3 * len(re.findall(r"\d{1,3}\s?%", b)) + len(FIBRES.findall(b))
    blocs = [b for b in blocs if re.search(r"\d{1,3}\s?%", b) and note(b) >= 4]
    return max(blocs, key=note, default=None)


def analyse(compo: str) -> dict:
    propre = IMITATION_RE.sub(" ", compo)
    formes: dict[str, str] = {}
    for m in ANIMAL_RE.finditer(propre):
        f = m.group(0).lower()
        cle = unicodedata.normalize("NFKD", f).encode("ascii", "ignore").decode().rstrip("sx")
        formes.setdefault(cle, f)
    animaux = sorted(formes.values())
    return {"animaux": animaux, "douteux": [], "statut": "ingredient_animal" if animaux else "aucun_ingredient_animal_declare"}


def main() -> None:
    sortie, *marques = sys.argv[1:]
    navigateur = "--navigateur" in marques
    marques = [m for m in marques if m != "--navigateur"]
    nav = I.Navigateur() if navigateur else None
    c = nav or httpx.Client(verify=os.environ.get("SSL_CERT_FILE", True), timeout=40, follow_redirects=True, headers=I.UA)
    res = []
    for arg in marques:
        slug, depart, reste = arg.split("|", 2)
        motif, maxi = reste.rsplit("|", 1)
        maxi = int(maxi)
        urls = I.urls_catalogue(nav, depart, motif, maxi) if nav else I.urls_produits(c, depart, motif, maxi)
        print(f"## {slug} : {len(urls)} fiches candidates", flush=True)
        lus = refus = 0
        for u in urls:
            if lus >= maxi:
                break
            try:
                r = c.get(u)
                time.sleep(0.6)
            except Exception as e:
                print("   ", u, type(e).__name__)
                continue
            if getattr(r, "status_code", 200) in (401, 403, 429):
                refus += 1
                print("    refus", r.status_code, u)
                if refus >= 2:  # une seule nouvelle tentative : on n'insiste pas
                    break
                continue
            t = I.texte(r.text)
            compo = bloc_composition(t)
            if not compo:
                continue
            lus += 1
            titre = I.texte(m.group(1)) if (m := re.search(r"<h1[^>]*>(.*?)</h1>", r.text, re.S)) else ""
            a = analyse(compo)
            vege = sorted({m.group(0).lower() for m in VEGETAL_RE.finditer(t)})
            res.append({"slug": slug, "url": u, "produit": titre[:120], "ingredients": compo[:600], "vegetal_mentions": vege, "nature": "composition", **a})
            print(f"   {a['statut']:32} {titre[:50]:50} {','.join(a['animaux'])[:60]}", flush=True)
            json.dump(res, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(res, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if nav:
        nav.close()


if __name__ == "__main__":
    main()
