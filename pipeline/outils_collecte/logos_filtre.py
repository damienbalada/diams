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
