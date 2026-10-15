"""Logos des marques de la vitrine : icône déclarée par le site officiel (apple-touch-icon, icon,
og:image en dernier recours), téléchargée une fois dans apps/web/public/logos/<slug>.<ext>."""
import html, os, re, sys, time
from urllib.parse import urljoin
import httpx
sys.stdout.reconfigure(encoding="utf-8")
OUT = r"C:\Users\damie\Downloads\claude\awareness-score\apps\web\public\logos"
os.makedirs(OUT, exist_ok=True)
H = {"User-Agent": "Mozilla/5.0 (compatible; DIAMS verifier; +https://awareness-score.vercel.app)", "Accept": "*/*"}
SITES = {
    "nutella": "https://www.nutella.com/fr/fr", "coca-cola": "https://www.coca-cola.com/fr/fr", "president": "https://www.president.fr",
    "zara": "https://www.zara.com/fr/", "lidl": "https://www.lidl.fr", "nike": "https://www.nike.com/fr/", "kinder": "https://www.kinder.com/fr/fr",
    "evian": "https://www.evian.com/fr/", "loreal": "https://www.loreal.com/fr-fr/", "mcdonalds": "https://www.mcdonalds.fr",
    "shein": "https://fr.shein.com", "ikea": "https://www.ikea.com/fr/fr/", "carrefour": "https://www.carrefour.fr", "danone": "https://www.danone.com",
    "haribo-marque": "https://www.haribo.com/fr-fr", "amazon": "https://www.amazon.fr",
}
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=30, follow_redirects=True, headers=H)
def taille(tag):
    m = re.search(r'sizes="(\d+)x', tag)
    return int(m.group(1)) if m else (180 if "apple-touch" in tag else 32)
for slug, url in SITES.items():
    try:
        r = c.get(url)
        if r.status_code == 403:
            time.sleep(3); r = c.get(url)
        cands = []
        if r.status_code == 200:
            for tag in re.findall(r"<link[^>]+>", r.text, re.I):
                if re.search(r'rel="[^"]*(apple-touch-icon|icon)[^"]*"', tag, re.I):
                    h = re.search(r'href="([^"]+)"', tag)
                    if h: cands.append((taille(tag), urljoin(str(r.url), html.unescape(h.group(1)))))
        cands.sort(reverse=True)
        cands.append((16, urljoin(url, "/apple-touch-icon.png")))
        ok = False
        for _, u in cands:
            try:
                i = c.get(u)
            except Exception:
                continue
            ct = i.headers.get("content-type", "")
            if i.status_code == 200 and ("image" in ct or u.endswith((".png", ".svg", ".ico"))) and len(i.content) > 300:
                ext = "svg" if "svg" in ct or u.endswith(".svg") else "ico" if "icon" in ct and "png" not in ct else "png" if "png" in ct else "jpg"
                open(os.path.join(OUT, f"{slug}.{ext}"), "wb").write(i.content)
                print("✓", slug, ext, len(i.content), u[:90]); ok = True; break
        if not ok: print("✗", slug, r.status_code)
    except Exception as x:
        print("✗", slug, type(x).__name__)
    time.sleep(1)
