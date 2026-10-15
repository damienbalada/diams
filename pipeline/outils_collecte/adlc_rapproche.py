"""Décisions de l'Autorité de la concurrence avec amende, de moins de cinq ans, rapprochées des
entités DIAMS (noms normalisés, mots entiers). Sortie : candidats à contrôler à la main."""
import ast
import csv
import json
import os
import re
import sys
import unicodedata

import httpx

sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client  # noqa: E402

S = os.path.dirname(os.path.abspath(__file__))
csv.field_size_limit(10 ** 8)
rows = list(csv.DictReader(open(os.path.join(S, "telechargements", "adlc", "metadata.csv"), encoding="utf-8")))
sanc = [r for r in rows if (r.get("Montant sanction") or "").strip() and r["date_decision_datetime"][:10] >= "2021-10-15"]
print(len(rows), "décisions ;", len(sanc), "avec sanction depuis le 15/10/2021")


def plain(t):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower())


STOP = {"groupe", "group", "france", "sas", "sa", "sarl", "holding", "international", "societe", "company", "the", "and",
        "les", "des", "et", "de", "la", "le", "du", "services", "distribution", "industries", "industrie"}
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
ents = supabase_client.get_all(c, "entities", {"select": "slug,display_name,legal_name,is_brand,parent_id"})
cands = []
for e in ents:
    for n in {e.get("display_name"), e.get("legal_name")}:
        w = [x for x in re.findall(r"[a-z0-9]+", plain(re.sub(r"\(.*?\)", " ", n or ""))) if x not in STOP]
        if w and len("".join(w)) >= 4:
            cands.append((e, r"\b" + r"[\s\-]+".join(map(re.escape, w)) + r"\b"))
out = []
for r in sanc:
    try:
        noms = ast.literal_eval(r["entreprises_concernees"]) if r["entreprises_concernees"].startswith("[") else [r["entreprises_concernees"]]
    except (ValueError, SyntaxError):
        noms = [r["entreprises_concernees"]]
    texte = plain(" | ".join(noms) + " | " + r["sous_titre"])
    vus = set()
    for e, pat in cands:
        if e["slug"] in vus:
            continue
        if re.search(pat, texte):
            vus.add(e["slug"])
            out.append({"decision": r["id_decision"], "date": r["date_decision_datetime"][:10], "montant": r["Montant sanction"],
                        "slug": e["slug"], "marque": e["is_brand"], "titre": r["sous_titre"][:160], "entreprises": noms[:8], "url": r["url_site"]})
json.dump(out, open(os.path.join(S, "adlc_candidats.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in out:
    print(f"{x['decision']} {x['date']} {x['montant'][:20]:>20} {x['slug']:28} {'(marque)' if x['marque'] else ''} | {x['titre'][:110]}")
print(len(out), "rapprochements")
