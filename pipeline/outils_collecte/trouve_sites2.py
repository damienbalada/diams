"""trouve_sites2.py : sites officiels des marques encore sans preuve animale (secteurs où le pilier
s'applique). Un site n'est retenu que si sa page d'accueil ou ses mentions légales portent :
  (a) le SIREN d'une société de la chaîne de propriété de la marque (écrit d'un seul tenant ou par
      groupes de trois), ou
  (b) la raison sociale du propriétaire direct ou du groupe racine (mot entier, au moins 5 lettres
      significatives), dans un passage de mentions légales (« éditeur », « édité par », « société »,
      « RCS », « publisher », « operated by »…).
Le passage est relevé pour la traçabilité (curated/sites_officiels_marques_2026-10-15.csv)."""
import html
import json
import os
import re
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor

import httpx

sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client  # noqa: E402

S = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(S, "sites_marques.json")
SECTEURS = {"Agroalimentaire", "Animalerie & Petfood", "Beauté & Parfums", "Entretien & Maison", "Grande consommation",
            "Horlogerie & Joaillerie", "Hygiène & Soin grand public", "Mode & Maroquinerie", "Restauration & Fast-food",
            "Vins & Spiritueux"}
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
g = supabase_client.get_all
sect = {s["id"]: s["name"] for s in g(c, "sectors", {"select": "id,name"})}
ents = g(c, "entities", {"select": "id,slug,display_name,legal_name,siren,is_brand,parent_id,sector_id,animal_free"})
by_id = {e["id"]: e for e in ents}
ind = {i["code"]: i["id"] for i in g(c, "indicators", {"select": "id,code"})}
doc = {x["entity_id"] for x in g(c, "evidence_active", {"select": "entity_id,indicator_id"})
       if x["indicator_id"] in (ind["ANI_EXPLOITATION"], ind["ANI_ANIMAL_FREE"])}
deja = {}
if os.path.exists(SORTIE):
    deja = {r["slug"]: r for r in json.load(open(SORTIE, encoding="utf-8"))}
connus = {r["slug"] for r in json.load(open(os.path.join(S, "sites_trouves.json"), encoding="utf-8")) if r.get("strict")}


def chaine(e):
    out, cur = [], e
    for _ in range(20):
        if not cur.get("parent_id") or cur["parent_id"] not in by_id:
            break
        cur = by_id[cur["parent_id"]]
        out.append(cur)
    return out


def plain(t):
    return unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()


STOP = {"groupe", "group", "france", "sas", "sa", "sarl", "holding", "international", "societe", "company", "the", "and", "les", "des"}


def noms_forts(e):
    w = [x for x in re.findall(r"[a-z0-9]+", plain(re.sub(r"\(.*?\)", " ", (e.get("legal_name") or e.get("display_name") or ""))))
         if x not in STOP]
    n = " ".join(w)
    return n if len(n.replace(" ", "")) >= 5 else None


cibles = []
for e in ents:
    if not e["is_brand"] or e["id"] in doc or e.get("animal_free") or e["slug"] in connus:
        continue
    if sect.get(e.get("sector_id")) not in SECTEURS:
        continue
    ch = chaine(e)
    if not ch:
        continue
    cibles.append((e, ch))
print(len(cibles), "marques à chercher", flush=True)

LEGAL = re.compile(r"[ée]dit[ée]? par|[ée]diteur|publisher|operated by|exploit[ée] par|soci[ée]t[ée]|RCS|SIREN|SIRET|registered|capital", re.I)


def texte(h):
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h)))


def domaines(e):
    w = [x for x in re.findall(r"[a-z0-9]+", plain(re.sub(r"\(.*?\)", " ", e.get("display_name") or e.get("legal_name") or "")))]
    out = []
    for n in ("".join(w), "-".join(w)):
        if len(n) >= 3:
            for t in (".fr", ".com"):
                if n + t not in out:
                    out.append(n + t)
    return out


def preuve(t, ch):
    for s in [x.get("siren") for x in ch if x.get("siren")]:
        m = re.search(r"(?<!\d)" + r"[\s\u00a0.]?".join([s[0:3], s[3:6], s[6:9]]) + r"(?!\d)", t)
        if m:
            return "siren", t[max(0, m.start() - 160): m.end() + 40]
    for x in ch:
        n = noms_forts(x)
        if not n:
            continue
        pat = r"\b" + r"[\s\-]+".join(map(re.escape, n.split())) + r"\b"
        for m in re.finditer(pat, plain(t)):
            ctx = t[max(0, m.start() - 160): m.end() + 120]
            if LEGAL.search(ctx):
                return "nom", ctx
    return None, None


PAGES = ["mentions-legales", "mentions-legales/", "fr/mentions-legales", "legal", "legal-notice", "fr/legal", "informations-legales"]


def essaie(args):
    e, ch = args
    if e["slug"] in deja:
        return deja[e["slug"]]
    res = {"slug": e["slug"], "nom": e.get("display_name"), "groupe": ch[-1]["slug"], "site": None}
    with httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=8, follow_redirects=True,
                      headers={"User-Agent": "Mozilla/5.0 (DIAMS, recherche de mentions legales)"}) as w:
        for d in domaines(e):
            racine = None
            for pref in ("https://www.", "https://"):
                try:
                    p = w.get(pref + d + "/")
                except Exception:
                    continue
                if p.status_code < 400:
                    racine, acc = str(p.url).rstrip("/"), p.text
                    break
            if not racine:
                continue
            k, ctx = preuve(texte(acc), ch)
            page = racine + "/"
            if not k:
                liens = re.findall(r'href="([^"]*(?:mentions|legal|imprint|impressum)[^"]*)"', acc, re.I)[:4]
                for l in liens + PAGES:
                    u = l if l.startswith("http") else racine + "/" + l.lstrip("/")
                    try:
                        p = w.get(u)
                    except Exception:
                        continue
                    if p.status_code < 400:
                        k, ctx = preuve(texte(p.text), ch)
                        if k:
                            page = str(p.url)
                            break
            if k:
                res.update(site=racine, preuve=page, type=k, extrait=ctx.strip())
                return res
    return res


with ThreadPoolExecutor(24) as ex:
    out = list(ex.map(essaie, cibles))
json.dump(out, open(SORTIE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
ok = [r for r in out if r.get("site")]
print(len(ok), "sites prouvés ;", sum(1 for r in ok if r["type"] == "siren"), "par SIREN,", sum(1 for r in ok if r["type"] == "nom"), "par raison sociale")
