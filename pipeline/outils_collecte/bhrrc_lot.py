"""Allégations relayées par le Business & Human Rights Resource Centre (BHRRC) : prépare un lot de
preuves (CSV, à vérifier mot pour mot) et un journal des groupes absents.

Pour chaque groupe racine : recherche dans l'API publique des entreprises du BHRRC
(/en/api/companies/?search=), rapprochement strict du nom ; puis lecture du flux public des articles
« contenant des allégations » de l'entreprise (12 plus récents au plus), dont on retient ceux des
12 derniers mois. Respect du délai de 5 secondes demandé par le fichier robots.txt du site.

Usage : bhrrc_lot.py <dossier de sortie>   (cache bhrrc_cache.json dans ce dossier, reprise possible)
"""
import csv, datetime as dt, email.utils, html, json, os, re, sys, time
import httpx
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from diams import supabase_client
from diams.normalize.names import is_strong_match

OUT = sys.argv[1]
CACHE = os.path.join(OUT, "bhrrc_cache.json")
BASE = "https://www.business-humanrights.org"
UA = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}
cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60)
w = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60, headers=UA, follow_redirects=True)
ents = supabase_client.get_all(c, "entities", {"select": "id,slug,display_name,legal_name,is_brand,parent_id"})
roots = [e for e in ents if not e["is_brand"] and not e["parent_id"]]
print(len(roots), "groupes")


def poli(url, **kw):
    time.sleep(5)
    for _ in range(3):
        r = w.get(url, **kw)
        if r.status_code != 429:
            return r
        time.sleep(30)
    return r


for n, e in enumerate(roots, 1):
    if e["slug"] in cache:
        continue
    nom = e.get("display_name") or e["legal_name"]
    nom_q = re.sub(r"\s*\((?:groupe|société|coopérative)\)\s*$", "", nom)
    try:
        res = poli(f"{BASE}/en/api/companies/", params={"search": nom_q}, headers={"Accept": "application/json"}).json().get("results", [])
    except Exception as err:
        print("  erreur", e["slug"], err); continue
    hit = next((x for x in res if is_strong_match(nom_q, x["name"]) or is_strong_match(e["legal_name"], x["name"])), None)
    if not hit:
        cache[e["slug"]] = {"trouve": False, "requete": nom_q}
    else:
        feed_url = f"{BASE}/en/feeds/latest-news/3/?companies={hit['bhrrc_id']}&contains_allegations=YES"
        xml = poli(feed_url).text
        items = []
        for it in re.findall(r"<item>(.*?)</item>", xml, flags=re.S):
            t = html.unescape(re.sub(r"<!\[CDATA\[|\]\]>", "", (re.search(r"<title>(.*?)</title>", it, re.S) or [None, ""])[1])).strip()
            d = (re.search(r"<pubDate>(.*?)</pubDate>", it) or [None, ""])[1]
            try:
                d = email.utils.parsedate_to_datetime(d).date().isoformat()
            except Exception:
                d = ""
            items.append({"titre": re.sub(r"\s+", " ", t), "date": d})
        cache[e["slug"]] = {"trouve": True, "nom_bhrrc": hit["name"], "id": hit["bhrrc_id"], "url": BASE + hit["url"],
                            "flux": feed_url, "articles": items}
    if n % 20 == 0:
        json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False); print(n, "groupes lus")
json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)

# Lot de preuves et journal
today = dt.date.today()
debut = today.replace(year=today.year - 1)
H = "entity_slug,indicator_code,source_code,nature,observed_on,value_type,value_numeric,value_boolean,value_text,normalized_value,confidence,source_url,excerpt,review_note".split(",")
rows, journal = [], []
for slug, v in cache.items():
    if not v.get("trouve"):
        journal.append({"slug": slug, "code": "SUP_BHRRC_ALLEG", "outcome": "non_trouvee", "source_url": f"{BASE}/en/companies/",
                        "detail": f"Cherché, non trouvé : aucune page entreprise au nom de « {v['requete']} » sur le site du Business & Human Rights Resource Centre (relu le {today.strftime('%d/%m/%Y')})."})
        continue
    recents = [a for a in v["articles"] if a["date"] and a["date"] >= debut.isoformat() and "»" not in a["titre"] and "«" not in a["titre"]]
    if not recents:
        journal.append({"slug": slug, "code": "SUP_BHRRC_ALLEG", "outcome": "non_trouvee", "source_url": v["flux"],
                        "detail": f"Cherché, non trouvé : aucun article relayant des allégations dans les 12 derniers mois sur la page « {v['nom_bhrrc']} » du Business & Human Rights Resource Centre (flux public relu le {today.strftime('%d/%m/%Y')})."})
        continue
    cites = " ; ".join(f"{'/'.join(reversed(a['date'].split('-')))} : « {a['titre']} »" for a in recents)
    excerpt = (f"Business & Human Rights Resource Centre, page « {v['nom_bhrrc']} », flux public des articles contenant des allégations "
               f"(12 plus récents au plus ; le site ne garantit pas l'exactitude des articles relayés), articles des 12 derniers mois : {cites}")
    rows.append([slug, "SUP_BHRRC_ALLEG", "BHRRC", "controversy", today.isoformat(), "numeric", str(len(recents)), "", "", "", "0.6",
                 v["flux"], excerpt, ""])
with open(os.path.join(OUT, "bhrrc_lot.csv"), "w", encoding="utf-8", newline="") as h:
    wr = csv.writer(h); wr.writerow(H); wr.writerows(rows)
json.dump(journal, open(os.path.join(OUT, "bhrrc_journal.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(rows), "preuves ;", len(journal), "absences")
