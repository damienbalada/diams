import csv, json, runpy, sys
sys.stdout.reconfigure(encoding="utf-8")
g = runpy.run_path(sys.argv[1])
with open(g["OUT"], "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=g["COLS"]); w.writeheader(); w.writerows(g["rows"])
json.dump(g["journal"], open(g["JOURNAL"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(g["rows"]), "preuves ;", len(g["journal"]), "lignes de journal")
