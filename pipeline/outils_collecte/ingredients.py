"""Lecture des ingrédients sur les fiches produits des sites de marques (essai du 17/10/2026).

Pour chaque marque : plan du site → fiches produits → bloc « Ingrédients » de la page → ingrédients
d'origine animale repérés (hors mentions de traces). Lecture seule ; écrit un JSON de constats que
l'on relit avant tout import. Une liste d'ingrédients sans matière animale visible ne prouve pas qu'un
produit est végétal (carmin, gélatine, vitamine D3, arômes…) : le statut dit seulement ce qui est lu.

Usage : python outils_collecte/ingredients.py sortie.json "slug|https://domaine/sitemap.xml|motif d'URL produit|max" …
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
import time
import unicodedata

import httpx

UA = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)"}

# Ingrédients d'origine animale certaine (français). Les mentions de traces sont retirées avant.
ANIMAL = [
    r"lait(?! (?:de |d['’] ?)(?:coco|soja|riz|amandes?|avoine|noisettes?|cajou|[ée]peautre|ch[èe]vre v[ée]g))(?!s? v[ée]g[ée]ta)", r"lactos[ée]rum", r"lactose", r"petit-lait", r"babeurre",
    r"cr[èe]me(?! de (?:marrons?|coco|riz|soja|balsamique))(?! glacée végétale)", r"beurre(?! de (?:cacao|karit[ée]|cacahu[èe]tes?|arachide|amande|noix|coco|cajou))",
    r"fromages?", r"cas[ée]ine?s?", r"cas[ée]inates?", r"prot[ée]ines? de lait", r"mati[èe]re grasse laiti[èe]re", r"yaourt",
    r"\bœufs?\b", r"\boeufs?\b", r"jaunes? d.[œo]e?ufs?", r"blancs? d.[œo]e?ufs?", r"ovoproduits?",
    r"g[ée]latine", r"\bmiel\b", r"cire d.abeille", r"gel[ée]e royale",
    r"viandes?", r"\bporc\b", r"b[œo]e?uf", r"\bveau\b", r"poulet", r"dinde", r"volaille", r"canard", r"agneau", r"jambon", r"lardons?",
    r"bacon", r"saucisses?", r"chorizo", r"\bgras de\b", r"saindoux", r"graisse (?:animale|de (?:porc|canard|b[œo]e?uf|oie))", r"suif",
    r"poissons?", r"anchois", r"\bthon\b", r"saumon", r"sardines?", r"maquereaux?", r"crevettes?", r"moules?", r"crustac[ée]s",
    r"carmin", r"cochenille", r"\bE ?120\b", r"gomme[- ]laque", r"\bE ?904\b", r"\bE ?901\b", r"\bE ?441\b", r"lanoline", r"collag[èe]ne", r"pr[ée]sure",
]
ANIMAL_RE = re.compile(r"\b(?:" + "|".join(ANIMAL) + r")", re.I)
# Ingrédients d'origine possiblement animale : signalés, jamais conclusifs.
DOUTEUX_RE = re.compile(r"\b(?:vitamine D3?|ar[ôo]mes? naturels?|ar[ôo]mes?\b|E ?542|E ?631|E ?627|E ?920|L-cyst[ée]ine|ac[ée]ides gras|mono- et diglyc[ée]rides|E ?471|st[ée]arate)", re.I)
SANS_RE = re.compile(r"\bsans (?:lait|lactose|[œo]e?ufs?|g[ée]latine|viande|ingr[ée]dients? d.origine animale)\b", re.I)
TRACES_RE = re.compile(r"(?:peut contenir|traces? (?:éventuelles? )?de|contient (?:des )?traces|fabriqué dans un atelier)[^.]*\.?", re.I)
VEGETAL_RE = re.compile(r"\b(?:100 ?% v[ée]g[ée]tal\w*|v[ée]gan\w*|vegan|v-label|v[ée]g[ée]talien\w*)", re.I)


def texte(h: str) -> str:
    h = re.sub(r"<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>", " ", h, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def bloc_ingredients(t: str) -> str | None:
    """Le texte qui suit « Ingrédients » (jusqu'à la rubrique suivante) qui ressemble le plus à une liste
    (virgules, pourcentages), ou rien. Les autres occurrences (questions, descriptions d'image) sont écartées."""
    blocs = [_FIN.split(m.group(1).strip())[0].strip() for m in _BLOC.finditer(t)]
    # Une liste d'ingrédients : au moins deux virgules dans ses 200 premiers caractères.
    # Une liste commence par une majuscule ou un chiffre (« Sucre, … », « Fruits 67,8 % … »), ou en
    # minuscule par un ingrédient suivi d'une virgule (« farine de blé*, … ») ; un texte de présentation
    # ou une description d'image finit sa première phrase avant toute virgule (« pour satisfaire… »).
    def liste(b: str) -> bool:
        if b[:1].isupper() or b[:1].isdigit():
            return True
        v, p = b.find(", "), b.find(". ")
        return v >= 0 and (p < 0 or v < p)
    # Et contient un pourcentage ou un ingrédient courant (pas une description : « Des belles airelles… »).
    courant = re.compile(r"%|\b(?:sucre|sel|eau|farine|huiles?|ar[ôo]mes?|amidon|lait|beurre|[ée]mulsifiant|conservateur|"
                         r"acidifiant|g[ée]lifiant|levure|cacao|[œo]e?ufs?|cr[èe]me|sirop|glucose|vinaigre|[ée]paississant)\b", re.I)
    blocs = [b for b in blocs if liste(b) and courant.search(b)]
    blocs = [b for b in blocs if b[:200].count(",") >= 2 and "Tableau des valeurs" not in b and not re.match(r"(?:d.un produit|sur les emballages|A conserver|comme |sélectionn|100 ?% d.origine)", b, re.I)]
    return max(blocs, key=lambda b: b.count(",") + 3 * b.count("%"), default=None)


# Fin de la liste : rubrique suivante en capitales (« UTILISATION ») ou bloc de page (recettes, liens).
_FIN = re.compile(r"(?<=\.)\s+(?=[A-ZÉÈ]{5,}\b)|\s(?:UTILISATION|CONSERVATION|Pour continuer|D[ée]couvr|Rejoignez|Des questions|Recettes?|Voir (?:le|la|les|aussi)|Ajouter au panier)\b")
_BLOC = re.compile(r"Ingr[ée]dients?(?:\s+et\s+allerg[èe]nes)?\s*:?\s*(.{20,1500}?)(?=\s(?:Valeurs? nutritionnelles?|Informations? nutritionnelles?|Conservation|Conseils?|Allerg[èe]nes|Poids net|Nutri-?Score|Origine|Mode d.emploi|Pr[ée]paration|Fabriqu[ée] (?:en|par)|Pour 100 ?g)|$)", re.I)


def analyse(ingr: str) -> dict:
    sans_traces = SANS_RE.sub(" ", TRACES_RE.sub(" ", ingr))
    # Une seule forme par ingrédient (« oeuf » et « œufs », « creme » et « crème » ne font qu'un).
    formes: dict[str, str] = {}
    for m in ANIMAL_RE.finditer(sans_traces):
        f = m.group(0).lower()
        cle = unicodedata.normalize("NFKD", f.replace("œ", "oe")).encode("ascii", "ignore").decode().rstrip("sx")
        formes.setdefault(cle, f)
    animaux = sorted(formes.values())
    douteux = sorted({m.group(0).lower() for m in DOUTEUX_RE.finditer(sans_traces)})
    statut = "ingredient_animal" if animaux else "aucun_ingredient_animal_declare"
    return {"animaux": animaux, "douteux": douteux, "statut": statut}


def urls_produits(c: httpx.Client, sitemap: str, motif: str, maxi: int) -> list[str]:
    vus, a_lire, out = set(), [sitemap], []
    while a_lire and len(out) < maxi * 4:
        u = a_lire.pop(0)
        if u in vus:
            continue
        vus.add(u)
        try:
            r = c.get(u)
        except Exception:
            continue
        for loc in re.findall(r"<loc>([^<]+)</loc>", r.text):
            loc = html.unescape(loc.strip())
            if re.search(r"sitemap[^/]*\.xml", loc) and len(vus) < 30:
                if re.search(r"product|produit|recette|recipe", loc, re.I) or "sitemap_index" in u or len(a_lire) < 5:
                    a_lire.append(loc)
            elif re.search(motif, loc):
                out.append(loc)
    return out


def main() -> None:
    sortie, *marques = sys.argv[1:]
    c = httpx.Client(verify=os.environ.get("SSL_CERT_FILE", True), timeout=40, follow_redirects=True, headers=UA)
    res = []
    for arg in marques:
        slug, sitemap, reste = arg.split("|", 2)
        motif, maxi = reste.rsplit("|", 1)
        maxi = int(maxi)
        urls = urls_produits(c, sitemap, motif, maxi)
        print(f"## {slug} : {len(urls)} fiches candidates", flush=True)
        lus = 0
        for u in urls:
            if lus >= maxi:
                break
            try:
                r = c.get(u)
                time.sleep(0.5)
            except Exception as e:
                print("   ", u, type(e).__name__)
                continue
            t = texte(r.text)
            ingr = bloc_ingredients(t)
            if not ingr:
                continue
            lus += 1
            titre = texte(m.group(1)) if (m := re.search(r"<h1[^>]*>(.*?)</h1>", r.text, re.S)) else ""
            a = analyse(ingr)
            vege = sorted({m.group(0).lower() for m in VEGETAL_RE.finditer(t)})
            res.append({"slug": slug, "url": u, "produit": titre[:120], "ingredients": ingr[:1200], "vegetal_mentions": vege, **a})
            print(f"   {a['statut']:32} {titre[:50]:50} {','.join(a['animaux'])[:60]}", flush=True)
            json.dump(res, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(res, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
