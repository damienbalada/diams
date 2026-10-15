"""Écrit au journal de relecture les lignes d'un lot (lectures de rapports sans preuve chiffrée).
Usage : python ecrit_journal.py <fichier.json> [--apply]"""
import json, os, sys
import httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client
from diams.relecture import write_reviews
lignes = json.load(open(sys.argv[1], encoding="utf-8"))
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
g = supabase_client.get_all
ent = {e["slug"]: e["id"] for e in g(c, "entities", {"select": "id,slug"})}
ind = {i["code"]: i["id"] for i in g(c, "indicators", {"select": "id,code"})}
# Pas de doublon : une même lecture (entité, indicateur, résultat, détail) n'est écrite qu'une fois.
deja = {(r["entity_id"], r["indicator_id"], r["outcome"], r["detail"]) for r in
        g(c, "indicator_reviews", {"select": "entity_id,indicator_id,outcome,detail", "reviewer": "eq.lecture-rapport"})}
rows = []
for l in lignes:
    k = (ent[l["slug"]], ind[l["code"]], l["outcome"], l["detail"][:2000])
    if k in deja:
        continue
    rows.append({"entity_id": k[0], "indicator_id": k[1], "evidence_id": None, "outcome": l["outcome"],
                 "detail": k[3], "source_url": l.get("source_url"), "reviewer": "lecture-rapport", "wave": None})
print(len(rows), "ligne(s) à écrire,", len(lignes) - len(rows), "déjà présentes")
if "--apply" in sys.argv and rows:
    print("écrites :", write_reviews(c, rows))
