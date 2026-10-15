"""ajoute_doc.py <clé> <slug> <url> <source> "<intitulé>" [période] : document secondaire d'un groupe."""
import json, sys
k, slug, url, src, doc = sys.argv[1:6]
pe = sys.argv[6] if len(sys.argv) > 6 else "2025-12-31"
e = json.load(open("esef_depots.json", encoding="utf-8"))
e[k] = {"slug": slug, "period_end": pe, "date_added": "2026-10-15", "report_url": url, "source": src, "doc": doc}
json.dump(e, open("esef_depots.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", k)
