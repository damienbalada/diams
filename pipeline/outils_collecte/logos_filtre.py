import json, re, sys, unicodedata
from urllib.parse import urlparse, parse_qs
sys.stdout.reconfigure(encoding="utf-8")
P = r"C:\Users\damie\Downloads\claude\awareness-score\apps\web\lib\logos.json"
logos = json.load(open(P, encoding="utf-8"))
G = "https://www.google.com/s2/favicons?domain={}&sz=128"
C = "https://commons.wikimedia.org/wiki/Special:FilePath/{}?width=160"
# Marques au nom du groupe : le logo commun est le bon.
for slug, src, dom in [
    ("champagne-taittinger", G.format("www.taittinger.com"), "www.taittinger.com"), ("lunor", G.format("www.lunor.fr"), "www.lunor.fr"),
    ("badoz", G.format("www.fromagerie-badoz.com"), "www.fromagerie-badoz.com"), ("alpina-savoie-marque", G.format("www.alpina-savoie.com"), "www.alpina-savoie.com"),
    ("charles-christ-marque", G.format("www.charles-christ.fr"), "www.charles-christ.fr"), ("brioche-pasquier", G.format("www.pasquier.fr"), "www.pasquier.fr"),
]:
    logos[slug] = {"src": src, "origine": f"icône du site {dom}"}
logos["ritter-sport"] = {"src": C.format("Ritter%20Sport%20logo.svg"), "origine": "Wikimedia Commons"}
logos["charal"] = {"src": C.format("LogoCharal2019.png"), "origine": "Wikimedia Commons"}

def plain(t):
    return re.sub(r"[^a-z0-9]+", "", unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower())

# Icône de site partagée par plusieurs entités : gardée seulement si le nom de l'entité contient
# le nom du site (« Carrefour City » et carrefour.fr), sinon écartée (Loué et ldc.fr).
par_src = {}
for k, v in logos.items():
    par_src.setdefault(v["src"], []).append(k)
n = 0
for src, ks in par_src.items():
    if len(ks) < 2 or "google.com/s2" not in src:
        continue
    dom = parse_qs(urlparse(src).query)["domain"][0].lower().removeprefix("www.")
    radical = plain(dom.split(".")[0])
    for k in ks:
        if radical not in plain(k):
            print("écarté :", k, "←", dom); del logos[k]; n += 1
json.dump(logos, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(n, "écartés ;", len(logos), "logos")

# Règle 3 (16/10/2026) : l'icône d'un site n'est gardée pour une MARQUE que si son nom figure dans
# l'adresse du site (Wanchai Ferry sur generalmills.com, Ajax sur colgatepalmolive.fr : écartés).
import csv as _csv
noms = {}
for l in open(r"C:\Users\damie\AppData\Local\Temp\claude\C--Users-damie-Downloads-claude-awareness-score\42ef682f-dd00-400c-91de-21ba754a28c1\scratchpad\db_full.tsv", encoding="utf-8"):
    p = l.rstrip("\n").split("\t")
    noms[p[0]] = (p[2] or p[1], p[3])
n3 = 0
for k in list(logos):
    v = logos[k]
    if not v["origine"].startswith("icône du site") or k not in noms or noms[k][1] != "M":
        continue
    dom = plain(v["origine"].split("icône du site", 1)[1].strip())
    mots = [m for m in re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKD", noms[k][0]).encode("ascii", "ignore").decode().lower()) if len(m) >= 3]
    # Le nom dans l'adresse, ou l'adresse dans le nom (rebelle.co pour « Rebellesnacks »).
    racine = re.sub(r"^www", "", dom)
    racine = re.split(r"(?:com|fr|ch|co|bzh|be|de|es|it|net|org|eu|uk)$", racine)[0]
    nom_colle = "".join(mots)
    if mots and not any(m in dom for m in mots) and not (len(racine) >= 5 and racine in nom_colle):
        print("écarté (site d'un autre nom) :", k, "←", dom); del logos[k]; n3 += 1
json.dump(dict(sorted(logos.items())), open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(n3, "écartés par la règle 3 ;", len(logos), "logos")
