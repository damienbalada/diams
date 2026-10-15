"""Délibérations de sanction de la CNIL publiées sur Légifrance (source officielle) : retrouve
la page de chaque numéro, relève le dispositif (montant de l'amende)."""
import html, json, os, re, sys, time
import httpx
sys.stdout.reconfigure(encoding="utf-8")
S = os.path.dirname(os.path.abspath(__file__))
H = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60, follow_redirects=True, headers=H)
NUM = ["SAN-2021-023", "SAN-2021-024", "SAN-2022-023", "SAN-2022-025", "SAN-2023-021"]
def get(u):
    r = c.get(u)
    if r.status_code == 403:
        time.sleep(3); r = c.get(u)
    time.sleep(1.5)
    return r
def texte(h):
    h = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h)))
out = {}
for n in NUM:
    r = get(f"https://www.legifrance.gouv.fr/search/cnil?query={n}&searchField=ALL&tab_selection=cnil")
    ids = list(dict.fromkeys(re.findall(r"/cnil/id/CNILTEXT\d+", r.text)))[:6]
    for i in ids:
        p = get("https://www.legifrance.gouv.fr" + i)
        t = texte(p.text)
        if re.search(rf"Délibération\s+(?:de la formation restreinte\s+)?n°\s*{n}\b", t) or (n in t[:3000]):
            m = [x.group(0) for x in re.finditer(r"[^.]{0,250}amende administrative d[’'][^.]{0,200}\.", t)][:3]
            out[n] = {"url": "https://www.legifrance.gouv.fr" + i, "titre": t[t.find("Délibération"):t.find("Délibération") + 300], "amendes": m}
            print("##", n, out[n]["url"]); print(out[n]["titre"][:300]); [print("  -", x.strip()[:400]) for x in m]
            break
    else:
        print("##", n, "non trouvée", ids)
json.dump(out, open(os.path.join(S, "cnil_deliberations.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
