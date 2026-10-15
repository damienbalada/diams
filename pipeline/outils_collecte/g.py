"""g.py : recherche dans le texte d'un rapport déjà téléchargé (cache de esrs_candidates).
Usage : python g.py <slug|url> "<motif regex>" [contexte=200] [max=6]"""
import hashlib, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
S = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(S, "cache_rapports")
cible, motif = sys.argv[1], sys.argv[2]
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 200
mx = int(sys.argv[4]) if len(sys.argv) > 4 else 6
if cible.startswith("http"):
    url = cible
else:
    d = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))[cible]
    url = d["report_url"]
p = os.path.join(CACHE, hashlib.sha256(url.encode()).hexdigest()[:16] + ".txt")
if not os.path.exists(p):
    sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
    os.environ.setdefault("DIAMS_CACHE", CACHE)
    from diams.esrs_candidates import fetch_text
    t = fetch_text(url, CACHE)
else:
    t = open(p, encoding="utf-8").read()
n = 0
if motif.startswith("~"):
    # Mode tolérant : texte extrait avec des espaces parasites (« Tax onomy ») ; chaque lettre
    # ou chiffre du motif peut être suivi d'espaces.
    motif = "".join(re.escape(ch) + r"\s*" if ch.isalnum() else (r"\s*" if ch == " " else re.escape(ch)) for ch in motif[1:])
for m in re.finditer(motif, t, re.I):
    print(f"[{m.start()}] …{t[max(0, m.start() - ctx): m.end() + ctx]}…\n")
    n += 1
    if n >= mx:
        break
print(f"({n} occurrence(s) affichée(s) ; url {url})")
