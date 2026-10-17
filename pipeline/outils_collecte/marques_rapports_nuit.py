"""Candidats « exploitation animale » de marques, cherchés dans les rapports de groupe lus cette nuit.
Une phrase candidate nomme la marque (mot entier) et contient un mot de matière animale du vérificateur.
Sortie : liste à relire à la main ; rien n'est écrit."""
import glob
import json
import os
import re
import sys

import httpx

sys.path.insert(0, r"C:/Users/damie/Downloads/claude/awareness-score/pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams.supabase_client import get_all  # noqa: E402
from diams.verify_curated import ESEF_KEYWORDS as KEYWORDS  # noqa: E402

SC = sys.argv[1]
DOCS = {  # groupe -> (fichier texte, adresse publique)
    "danone": (f"{SC}/amf/danone.txt", "https://bdif.amf-france.org/back/api/v1/documents/2026/D.26-0063/89708FA20E711C6B82CFEDF5FF402C4B8E7375F3418569A7831FA88A50CB0872.zip"),
    "carrefour": (f"{SC}/amf/carrefour.txt", "https://bdif.amf-france.org/back/api/v1/documents/2026/D.26-0143/7A3CB233AA8727B6F5EE7B409F80D8CBC4ECFCF43ACB2FA1B88354B4090AB39A.zip"),
    "lvmh": (f"{SC}/amf/lvmh.txt", "https://bdif.amf-france.org/back/api/v1/documents/2026/D.26-0195/CA8A1E35A6C70FC2DE6B35F0939523887728C2FE2C11DFAC7F9B5F7675629928.zip"),
    "kering": (f"{SC}/amf/kering.txt", "https://bdif.amf-france.org/back/api/v1/documents/2026/D.26-0266/C309289F82AEED2F9E217E7AF66A2CCF745595BC227F5C9D01AAFA76630CF737.zip"),
    "hermes": (f"{SC}/amf/hermes.txt", "https://bdif.amf-france.org/back/api/v1/documents/2026/D.26-0114/CBBDE3794700DA7CCD45B4EF4EC18BC78AFEB3BC39486E92A101A56035A54D24.zip"),
    "mondelez": (f"{SC}/sec/mdlz-10k.txt", "https://www.sec.gov/Archives/edgar/data/1103982/000162828026005345/mdlz-20251231.htm"),
    "nomad-foods": (f"{SC}/sec/nomad-20f.txt", "https://www.sec.gov/Archives/edgar/data/1651717/000165171726000006/nomd-20251231.htm"),
    "general-mills": (f"{SC}/sec/gis-10k.txt", "https://www.sec.gov/Archives/edgar/data/40704/000162828026046466/gis-20260531.htm"),
    "thai-union": (glob.glob(f"{SC}/conseils/docs/tu-or*")[0], "https://www.thaiunion.com/uploads/tu-or2025-en-2.pdf"),
    "savencia": (glob.glob(f"{SC}/conseils/docs/savencia-rfa*")[0], "https://savencia.com/wp-content/uploads/2026/04/Savencia-FD_RFA-2025.pdf"),
    "henkel": (glob.glob(f"{SC}/conseils/docs/henkel-ar*")[0], "https://www.henkel.com/resource/blob/2131544/eae43b38b5da9c89268a532af1dfbe4f/data/2025-annual-report.pdf"),
}
KW = re.compile(KEYWORDS["ANI_EXPLOITATION"][0], re.I)
with httpx.Client(timeout=120) as c:
    ents = get_all(c, "entities", {"select": "id,slug,display_name,parent_id,is_brand,animal_free"})
    ind = {i["code"]: i["id"] for i in get_all(c, "indicators", {"select": "id,code"})}
    ani = {e["entity_id"] for e in get_all(c, "evidence_active", {"select": "entity_id", "indicator_id": f"eq.{ind['ANI_EXPLOITATION']}"})}
by_id = {e["id"]: e for e in ents}


def racine(e):
    while e.get("parent_id"):
        e = by_id[e["parent_id"]]
    return e["slug"]


out = []
for slug, (path, url) in DOCS.items():
    t = re.sub(r"\s+", " ", open(path, encoding="utf-8").read())
    phrases = re.split(r"(?<=[.!?])\s+", t)
    marques = [e for e in ents if e["is_brand"] and not e.get("animal_free") and e["id"] not in ani and racine(e) == slug]
    for m in marques:
        nom = m["display_name"]
        if len(nom) < 3:
            continue
        rx = re.compile(r"(?<![\w])" + re.escape(nom) + r"(?![\w])")
        for p in phrases:
            if len(p) < 600 and rx.search(p) and KW.search(p):
                out.append({"groupe": slug, "marque": m["slug"], "nom": nom, "url": url, "phrase": p.strip()})
                break
json.dump(out, open(f"{SC}/marques_candidats.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for o in out:
    print(f"{o['groupe']:12} {o['marque']:24} {o['phrase'][:260]}")
print(len(out), "candidats")
