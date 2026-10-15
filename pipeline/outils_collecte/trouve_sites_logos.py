"""trouve_sites_logos.py : site officiel des marques et des groupes encore sans logo, pour en tirer
l'icône (logos_wikidata.py). Même règle que trouve_sites2.py : un domaine candidat, tiré du nom
(« nom.fr », « nom.com », avec ou sans tiret), n'est retenu que si sa page d'accueil ou ses
mentions légales portent :
  (a) le SIREN d'une société de la chaîne de propriété (pour un groupe : le sien), ou
  (b) la raison sociale du propriétaire direct, du groupe racine (ou, pour un groupe, la sienne),
      dans un passage de mentions légales ou de droits d'auteur (« éditeur », « RCS », « © »…).
Le nom de la marque seul ne prouve rien : n'importe quel site peut l'écrire.
Sortie : pipeline/curated/sites_officiels_logos_2026-10-16.csv (slug, site, page de preuve, type, extrait)."""
import csv
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

RACINE = r"C:\Users\damie\Downloads\claude\awareness-score"
SORTIE = os.environ.get("SORTIE") or os.path.join(RACINE, "pipeline", "curated", "sites_officiels_logos_2026-10-16.csv")
UA = "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)"
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
ents = supabase_client.get_all(c, "entities", {"select": "id,slug,display_name,legal_name,siren,is_brand,parent_id"})
by_id = {e["id"]: e for e in ents}
logos = json.load(open(os.path.join(RACINE, "apps", "web", "lib", "logos.json"), encoding="utf-8"))
connus = set()
for f, col in (("sites_officiels_2026-10-15.csv", "brand_slug"), ("sites_officiels_marques_2026-10-15.csv", "marque")):
    with open(os.path.join(RACINE, "pipeline", "curated", f), encoding="utf-8") as fh:
        connus |= {r[col] for r in csv.DictReader(fh)}


def plain(t):
    return unicodedata.normalize("NFKD", (t or "").replace("’", "'")).encode("ascii", "ignore").decode().lower()


STOP = {"groupe", "group", "france", "sas", "sa", "sarl", "sca", "snc", "holding", "international", "societe", "company", "the",
        "and", "les", "des", "inc", "ltd", "llc", "plc", "corp", "corporation", "ag", "gmbh", "nv", "spa", "se", "co", "marque"}


def mots(n):
    return [x for x in re.findall(r"[a-z0-9]+", plain(re.sub(r"\(.*?\)", " ", n or ""))) if x not in STOP]


def nom_fort(e):
    n = " ".join(mots(e.get("legal_name") or e.get("display_name")))
    return n if len(n.replace(" ", "")) >= 5 else None


def chaine(e):
    out, cur = [], e
    for _ in range(20):
        if not cur.get("parent_id") or cur["parent_id"] not in by_id:
            break
        cur = by_id[cur["parent_id"]]
        out.append(cur)
    return out


def domaines(e):
    w = mots(e.get("display_name") or e.get("legal_name"))
    out = []
    for n in ("".join(w), "-".join(w)):
        if len(n) >= 3:
            for t in (".fr", ".com"):
                if n + t not in out:
                    out.append(n + t)
    return out


LEGAL = re.compile(r"[ée]dit[ée]? par|[ée]diteur|publisher|operated by|exploit[ée] par|soci[ée]t[ée]|RCS|SIREN|SIRET|registered|"
                   r"capital|©|copyright|all rights reserved|tous droits r[ée]serv[ée]s|trademark", re.I)


def texte(h):
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h)))


def preuve(t, preuves):
    for s in [x.get("siren") for x in preuves if x.get("siren")]:
        m = re.search(r"(?<!\d)" + r"[\s\u00a0.]?".join([s[0:3], s[3:6], s[6:9]]) + r"(?!\d)", t)
        if m:
            return "siren", t[max(0, m.start() - 160): m.end() + 40]
    pt = plain(t)
    for x in preuves:
        n = nom_fort(x)
        if not n:
            continue
        pat = r"\b" + r"[\s\-]+".join(map(re.escape, n.split())) + r"\b"
        for m in re.finditer(pat, pt):
            ctx = t[max(0, m.start() - 160): m.end() + 120]
            if LEGAL.search(ctx):
                return "nom", ctx
    return None, None


PAGES = ["mentions-legales", "mentions-legales/", "fr/mentions-legales", "legal", "legal-notice", "fr/legal", "informations-legales"]


def essaie(e):
    ch = chaine(e)
    preuves = ch if e["is_brand"] else [e] + ch
    if not preuves:
        return None
    with httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=8, follow_redirects=True, headers={"User-Agent": UA, "Accept": "*/*"}) as w:
        for d in domaines(e):
            racine = acc = None
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
            k, ctx = preuve(texte(acc), preuves)
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
                        k, ctx = preuve(texte(p.text), preuves)
                        if k:
                            page = str(p.url)
                            break
            if k:
                return {"slug": e["slug"], "site": racine, "page_de_preuve": page, "preuve": k, "extrait": ctx.strip()[:400]}
    return None


# Toutes les entités sans site prouvé : le site sert au logo et à la preuve d'exploitation animale.
cibles = [e for e in ents if e["slug"] not in connus]
if os.environ.get("CIBLES"):  # relance ciblée : slugs séparés par des virgules
    voulus = set(os.environ["CIBLES"].split(","))
    cibles = [e for e in ents if e["slug"] in voulus]
deja = {}
if os.path.exists(SORTIE):
    with open(SORTIE, encoding="utf-8") as fh:
        deja = {r["slug"]: r for r in csv.DictReader(fh)}
cibles = [e for e in cibles if e["slug"] not in deja]
print(len(cibles), "entités sans site prouvé", flush=True)
out = list(deja.values())


def ecrire():
    with open(SORTIE, "w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=["slug", "site", "page_de_preuve", "preuve", "extrait"])
        wr.writeheader()
        wr.writerows(sorted(out, key=lambda r: r["slug"]))


# Peu de connexions à la fois, et écriture au fil de l'eau (un arrêt ne perd rien).
with ThreadPoolExecutor(16) as ex:
    for n, r in enumerate(ex.map(essaie, cibles), 1):
        if r:
            out.append(r)
        if n % 100 == 0:
            ecrire()
            print(n, "essayées ;", len(out), "sites prouvés", flush=True)
ecrire()
print(len(out), "sites prouvés ;", sum(r["preuve"] == "siren" for r in out), "par SIREN,", sum(r["preuve"] == "nom" for r in out), "par raison sociale")
