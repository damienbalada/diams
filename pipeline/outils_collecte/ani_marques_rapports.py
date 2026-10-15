"""ani_marques_rapports.py : pour les marques dont l'exploitation animale n'est que présumée, cherche
dans les rapports déjà téléchargés de leur groupe (cache_rapports) une phrase qui nomme la marque
ET une matière ou un produit d'origine animale (cuir, laine, soie, cachemire, fourrure, plumes,
lait, fromage, viande…). Sortie : candidats à relire à la main (ani_marques_candidats.json), jamais
écrits tels quels : la phrase retenue doit attribuer la matière à la marque elle-même."""
import hashlib, json, os, re, sys
import httpx
sys.path.insert(0, r"C:\Users\damie\Downloads\claude\awareness-score\pipeline")
sys.stdout.reconfigure(encoding="utf-8")
from diams import supabase_client

S = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))
SECTEURS = set((sys.argv[2] if len(sys.argv) > 2 else "fashion_leather,watches_jewelry").split(","))
MAT = {
    "cuir": r"cuirs?|leathers?|maroquinerie|peaux?|skins?|python|crocodile|alligator|autruche|ostrich|lizard|l[ée]zard",
    "laine": r"laines?|wool|merino|m[ée]rinos|mohair|alpaga|alpaca|angora|cachemire|cashmere|vicu[ñn]a",
    "soie": r"soie|silk",
    "fourrure": r"fourrures?|furs?\b|shearling|peau lain[ée]e",
    "plumes": r"duvet|down\b|plumes?|feathers?",
    "nacre et corne": r"nacre|mother[- ]of[- ]pearl|corne|horn\b|ivoire|perles? fines?",
    "lait": r"lait|milk|dairy|laitiers?|fromages?|cheese|beurre|butter|yaourts?|yogh?urts?|cr[èe]me",
    "viande": r"viandes?|meat|poulet|chicken|b[œo]euf|beef|porc|pork|jambon|ham\b|volailles?|poultry",
    "poisson": r"poissons?|fish|thon|tuna|saumon|salmon|crevettes?|shrimp",
    "œufs": r"œufs?|oeufs?|eggs?",
    "miel": r"miel|honey",
}
c = httpx.Client(verify=os.environ["SSL_CERT_FILE"], timeout=120)
g = supabase_client.get_all
sect = {s["id"]: s["code"] for s in g(c, "sectors", {"select": "id,code"})}
ind = {i["code"]: i["id"] for i in g(c, "indicators", {"select": "id,code"})}
ents = g(c, "entities", {"select": "id,slug,display_name,legal_name,is_brand,parent_id,sector_id,animal_free"})
by_id = {e["id"]: e for e in ents}
doc = {x["entity_id"] for x in g(c, "evidence_active", {"select": "entity_id,indicator_id"})
       if x["indicator_id"] in (ind["ANI_EXPLOITATION"], ind["ANI_ANIMAL_FREE"])}
txt = {}
def textes(slug):
    out = []
    for k, d in DEP.items():
        if d.get("slug", k.split("#")[0]) != slug:
            continue
        p = os.path.join(S, "cache_rapports", hashlib.sha256(d["report_url"].encode()).hexdigest()[:16] + ".txt")
        if os.path.exists(p):
            if p not in txt:
                txt[p] = re.sub(r"\s+", " ", open(p, encoding="utf-8").read())
            out.append((k, d, txt[p]))
    return out
res = []
for e in ents:
    if not e["is_brand"] or e["id"] in doc or e.get("animal_free") or sect.get(e["sector_id"]) not in SECTEURS:
        continue
    nom = (e.get("display_name") or e["legal_name"]).split(" (")[0]
    cur, anc = e, []
    while cur.get("parent_id") in by_id:
        cur = by_id[cur["parent_id"]]; anc.append(cur["slug"])
    trouves = []
    for a in anc:
        for k, d, t in textes(a):
            for m in re.finditer(r"(?<![\w])" + re.escape(nom) + r"(?![\w])", t):
                a0 = max(t.rfind(". ", 0, m.start()) + 2, m.start() - 300)
                b0 = t.find(". ", m.end()); b0 = min(len(t) if b0 < 0 else b0 + 1, m.end() + 300)
                phr = t[a0:b0]
                for mat, rx in MAT.items():
                    if re.search(r"(?<![\w])(" + rx + r")(?![\w])", phr, re.I):
                        trouves.append({"cle": k, "url": d["report_url"], "doc": d.get("doc"), "matiere": mat, "phrase": phr.strip()})
                        break
    res.append({"slug": e["slug"], "nom": nom, "secteur": sect.get(e["sector_id"]), "groupes": anc, "candidats": trouves[:60]})
json.dump(res, open(os.path.join(S, "ani_marques_candidats.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(res), "marques ;", sum(1 for r in res if r["candidats"]), "avec au moins une phrase candidate")
for r in res:
    print("•", r["slug"], "←", ",".join(r["groupes"][:2]), ":", len(r["candidats"]), "phrase(s)")
