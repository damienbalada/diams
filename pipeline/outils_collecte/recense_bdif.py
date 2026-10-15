"""Recense, pour les groupes français (SIREN) sans rapport sur filings.xbrl.org, le document
d'enregistrement universel (DEU) de l'exercice 2025 déposé à l'AMF (BDIF). L'émetteur déclaré au
dépôt est affiché pour contrôle : il doit être la société du groupe (pas une homonyme)."""
import json, os, sys, time
import httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client
from diams.connectors import bdif
S = os.path.dirname(os.path.abspath(__file__))
esef = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=60, follow_redirects=True)
ents = supabase_client.get_all(c, "entities", {"select": "slug,legal_name,display_name,siren,lei,parent_id,is_brand,country"})
cibles = [e for e in ents if not e["is_brand"] and not e.get("parent_id") and e.get("siren") and e["slug"] not in esef]
out = {}
for e in cibles:
    nom = e.get("display_name") or e.get("legal_name")
    try:
        r = bdif.find_urd(nom, 2025, c)
    except httpx.HTTPError as x:
        print("erreur", e["slug"], x); time.sleep(2); continue
    r = [u for u in r if u.esef_url]
    if r:
        u = r[0]
        out[e["slug"]] = {"nom": nom, "emetteur": u.issuer, "numero": u.number, "depose": u.filed, "url": u.esef_url,
                          "legal_name": e.get("legal_name")}
        print(f"{e['slug']:28} {nom[:30]:30} → {u.issuer[:45]:45} {u.number} {u.filed}")
    time.sleep(0.3)
json.dump(out, open(os.path.join(S, "bdif_depots.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(cibles), "groupes français sans rapport ESEF ;", len(out), "avec un DEU 2025 trouvé")
