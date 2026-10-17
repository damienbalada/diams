"""Audit groupé : chaque source des preuves approuvées (avec citations) est téléchargée une fois,
et chaque citation y est recherchée mot pour mot (espaces de mise en page ignorés). Rien n'est écrit en base."""
import sys, os, re, json, hashlib, httpx, concurrent.futures as cf
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:/Users/damie/Downloads/claude/awareness-score/pipeline")
from diams.supabase_client import get_all
from diams.verify_curated import document_text, _canon
OUT = sys.argv[1]; CACHE = os.path.join(OUT, "textes"); os.makedirs(CACHE, exist_ok=True)
with httpx.Client(timeout=120) as db:
    ev = get_all(db, "evidence_active", {"select": "id,source_url,excerpt,reviewer,entity_id,indicator_id", "excerpt": "like.*«*"})
ev = [e for e in ev if e.get("source_url") and (e.get("reviewer") or "").startswith(("auto:verify_curated", "delegue"))]
par_url = {}
for e in ev: par_url.setdefault(e["source_url"], []).append(e)
print(len(ev), "preuves,", len(par_url), "sources", flush=True)
def texte(url):
    p = os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest() + ".txt")
    if os.path.exists(p): return open(p, encoding="utf-8").read()
    with httpx.Client(timeout=240, verify=os.environ["SSL_CERT_FILE"], follow_redirects=True,
                      headers={"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)"}) as c:
        t = document_text(url, c)
    open(p, "w", encoding="utf-8").write(t or ""); return t or ""
def controle(url):
    try: t = texte(url)
    except Exception as ex: return url, "ECHEC", f"{type(ex).__name__}: {str(ex)[:120]}", []
    ct = _canon(t); bare = re.sub(r"\s", "", ct); manq = []
    for e in par_url[url]:
        for q in re.findall(r"«\s?(.+?)\s?»", e["excerpt"]):
            cq = _canon(q)
            if cq not in ct and re.sub(r"\s", "", cq) not in bare: manq.append((e["id"], q[:160]))
    return url, "OK" if not manq else "MANQUE", len(t), manq
res = []
with cf.ThreadPoolExecutor(6) as pool:
    for i, r in enumerate(pool.map(controle, list(par_url)), 1):
        res.append(r)
        if r[1] != "OK": print(r[1], r[0], r[2], r[3][:3], flush=True)
        if i % 50 == 0: print("…", i, flush=True)
json.dump(res, open(os.path.join(OUT, "audit.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("FINI", sum(r[1] == "OK" for r in res), "OK,", sum(r[1] == "MANQUE" for r in res), "manques,", sum(r[1] == "ECHEC" for r in res), "échecs")
