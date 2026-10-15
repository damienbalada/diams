"""gm.py : recherches ciblées (FR + EN) pour les indicateurs manquants d'un groupe, dans le texte
du rapport en cache. Usage : python gm.py <slug> [codes,...] [n=3] [ctx=130]"""
import hashlib, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
S = os.path.dirname(os.path.abspath(__file__))
M = {
    "GOV_BOARD_GENDER": r"(?:pourcentage|part|proportion|taux)[^.]{0,40}(?:femmes|administratrices)[^.]{0,80}?\d{1,2}(?:[,.]\d+)?\s?%|(?:percentage|share|proportion) of (?:women|female)[^.]{0,80}?\d{1,2}(?:\.\d+)?\s?%|(?:board|directors|conseil)[^.]{0,60}?(?:women|female|femmes)[^.]{0,40}?\d{1,2}(?:[.,]\d+)?\s?%|gender diversity ratio[^.]{0,80}",
    "GOV_BOARD_INDEP": r"ind[ée]pendan\w+[^.]{0,80}?\d{1,3}(?:[,.]\d+)?\s?%|\d{1,3}(?:[,.]\d+)?\s?%[^.]{0,40}ind[ée]pendan|independen\w+[^.]{0,80}?\d{1,3}(?:\.\d+)?\s?%",
    "LAB_CEO_PAY_RATIO": r"(?:ratio|multiple)[^.]{0,120}(?:m[ée]dian)[^.]{0,140}?\d+(?:[,.]\d+)?|(?:total remuneration ratio|annual total remuneration ratio|CEO pay ratio|ratio d.[ée]quit[ée])[^.]{0,140}?\d+",
    "LAB_GENDER_PAYGAP": r"(?:[ée]cart de r[ée]mun[ée]ration|gender pay gap|pay gap)[^.]{0,160}?-?\d+(?:[,.]\d+)?\s?%",
    "ENV_GHG_TREND": r"(?:Total des émissions de GES|Émissions totales de GES|Total GHG emissions|Total emissions)[^.]{0,40}(?:march|market)[^.]{0,200}",
    "ENV_GHG_INTENSITY": r"(?:Intensit[ée] (?:des |de )?(?:[ée]missions de )?GES|GHG (?:emissions )?intensity)[^.]{0,200}",
    "ENV_SCOPE3_DISCLOSED": r"(?:scope 3|scope III|périmètre 3)[^.]{0,40}(?:GHG|GES|emissions|émissions)[^.]{0,140}\d",
    "ENV_TAXONOMY_CAPEX": r"(?:CapEx|capital expenditure)[^.]{0,40}(?:durables sur le plan environnemental|environmentally sustainable activities)[^.]{0,60}\(A\.1\)[^.]{0,80}|Taxonomy-aligned CapEx[^.]{0,120}|CapEx align[ée]s?[^.]{0,120}\d+(?:[,.]\d+)?\s?%",
    "PLA_REDUCTION": r"(?:virgin plastic|plastiques? vierges?)[^.]{0,220}",
    "PLA_RECYCLED": r"(?:recycled content|contenu recyclé|recyclables?, réutilisables|recyclable, reusable)[^.]{0,200}?\d+(?:[,.]\d+)?\s?%",
    "WAT_INTENSITY": r"(?:Intensit[ée] hydrique|water intensity|Consommation d.eau totale en m|water consumption intensity)[^.]{0,200}",
    "LAB_LIVING_WAGE": r"(?:salaires? d[ée]cents?|living wage|adequate wage)[^.]{0,220}",
    "SUP_SUPPLIER_LIST": r"(?:liste (?:des|de nos) (?:fournisseurs|sites)|list of (?:our )?(?:tier 1 )?(?:suppliers|factories)|supplier list)[^.]{0,200}",
    "SUP_VIGILANCE_PLAN": r"Plan de vigilance[^.]{0,250}",
    "TAX_EFFECTIVE_RATE": r"(?:taux (?:d.imp[ôo]t )?effectif|effective tax rate)[^.]{0,120}?\d+(?:[,.]\d+)?\s?%",
}
TOC = re.compile(r"paragraphe \d|paragraph \d|Indicateur n|Indicator n|Annex(?:e)? I\b|\.{4,}")
slug = sys.argv[1]
dep = json.load(open(os.path.join(S, "esef_depots.json"), encoding="utf-8"))[slug]
codes = sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2] else json.load(open(os.path.join(S, "manques_esef.json")))[slug]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 3
ctx = int(sys.argv[4]) if len(sys.argv) > 4 else 130
url = dep["report_url"]
p = os.path.join(S, "cache_rapports", hashlib.sha256(url.encode()).hexdigest()[:16] + ".txt")
t = open(p, encoding="utf-8").read()
print(f"# {slug} {dep['period_end']} {url}")
for c in codes:
    if c not in M:
        continue
    print(f"=== {c}")
    k = 0
    for m in re.finditer(M[c], t, re.I):
        z = t[max(0, m.start() - ctx): m.end() + ctx]
        if TOC.search(z):
            continue
        print(f"  [{m.start()}] {z}")
        k += 1
        if k >= n:
            break
