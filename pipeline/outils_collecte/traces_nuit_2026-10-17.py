"""Constats de la nuit du 17/10/2026 à consigner au journal de relecture (indicator_reviews)."""
import json
import sys

L = []


def a(slug, code, outcome, detail, url=None):
    L.append({"slug": slug, "code": code, "outcome": outcome, "detail": detail, "source_url": url})


MICH = "https://filings.xbrl.org/549300SOSI58J6VIW052/2025-12-31/ESEF/FR/0/549300SOSI58J6VIW052-2025-12-31-1-fr/reports/549300SOSI58J6VIW052-2025-12-31-1-fr.xhtml"
for c in ("LAB_GENDER_PAYGAP", "LAB_CEO_PAY_RATIO"):
    a("michelin", c, "absence_confirmee", "Rapport financier annuel 2025 (ESEF) relu le 17/10/2026 : l'exigence ESRS S1-16 (écart de rémunération et rémunération totale) est déclarée « Non matériel » ; aucune donnée publiée.", MICH)
LOR = "https://filings.xbrl.org/529900JI1GG6F7RKVI53/2025-12-31/ESEF/FR/0/loreal-2025-12-31-1-fr/reports/loreal-2025-12-31-1-fr.xhtml"
a("loreal", "LAB_GENDER_PAYGAP", "autre_forme", "Écart brut publié en deux populations (2025) : 2,5 % hors conseiller(ère)s de beauté, −1,6 % pour les seul(e)s conseiller(ère)s de beauté ; pas de chiffre pour l'ensemble du groupe (relu le 17/10/2026).", LOR)
a("loreal", "LAB_CEO_PAY_RATIO", "autre_forme", "Ratio publié par zone seulement (2025 : Europe 196, Amérique latine 71, Amérique du Nord 45, Asie du Nord 80, SAPMENA et Afrique subsaharienne 82) ; pas de ratio groupe (relu le 17/10/2026).", LOR)
TTE = "https://filings.xbrl.org/529900S21EQ1BO4ESM68/2025-12-31/ESEF/FR/0/529900S21EQ1BO4ESM68-2025-12-31-1-fr/reports/529900S21EQ1BO4ESM68-2025-12-31-1-fr.xhtml"
a("totalenergies", "LAB_CEO_PAY_RATIO", "autre_forme", "Ratios publiés au titre de la loi PACTE pour TotalEnergies SE (72 à la médiane) et pour le périmètre France représentant 80 % de la masse salariale (116) ; pas de ratio pour l'ensemble du groupe (relu le 17/10/2026).", TTE)
a("totalenergies", "LAB_GENDER_PAYGAP", "autre_forme", "Seul l'écart ajusté global est publié (2,9 % en faveur des hommes en 2025) ; l'écart non corrigé exigé par l'ESRS S1-16 n'a pas été trouvé (relu le 17/10/2026).", TTE)
a("seb", "LAB_CEO_PAY_RATIO", "autre_forme", "Ratios publiés pays par pays pour les principales zones (66 % des effectifs) ; le groupe juge le chiffre consolidé non pertinent (relu le 17/10/2026).",
  "https://filings.xbrl.org/969500WP61NBK098AC47/2025-12-31/ESEF/FR/0/969500WP61NBK098AC47-2025-12-31-1-FR/reports/969500WP61NBK098AC47-2025-12-31-1-FR.xhtml")
SAV = "https://savencia.com/wp-content/uploads/2026/04/Savencia-FD_RFA-2025.pdf"
a("savencia", "LAB_CEO_PAY_RATIO", "autre_forme", "Rapport financier annuel 2025 : indicateurs S1-16 publiés séparément pour la France et le monde hors France (ratio à la médiane France : 25,4 pour le président, 32,2 pour le directeur général) ; pas de ratio groupe (relu le 17/10/2026).", SAV)
a("savencia", "LAB_GENDER_PAYGAP", "autre_forme", "Rapport financier annuel 2025 : écart publié pour le périmètre France seulement (écart de rémunération moyenne de 3 %) ; pas de chiffre groupe (relu le 17/10/2026).", SAV)
a("campari", "GOV_BOARD_GENDER", "autre_forme", "Part de femmes publiée par catégorie d'administrateurs (2025 : non exécutifs 36,4 %, exécutifs 0 %) ; pas de part pour l'ensemble du conseil (relu le 17/10/2026).",
  "https://filings.xbrl.org/213800ED5AN2J56N6Z02/2025-12-31/ESEF/NL/0/davidecamparimilano-2025-12-31-0-en/reports/davidecamparimilano-2025-12-31-0-en.xhtml")
a("lotus-bakeries", "GOV_BOARD_INDEP", "autre_forme", "Liste nominative des administrateurs indépendants (« Onafhankelijke bestuurders »), sans part publiée ; non calculée par l'Index (relu le 17/10/2026).",
  "https://filings.xbrl.org/5493004C0K34IFI67I03/2025-12-31/ESEF/BE/0/5493004C0K34IFI67I03-2025-12-31-1-nl/reports/5493004C0K34IFI67I03-2025-12-31-1-nl.xhtml")
a("ab-inbev", "WAT_INTENSITY", "autre_forme", "Intensité publiée en milliers de m³ par million de dollars (1,15 en 2025 et en 2024), dans un texte découpé ; non convertie (relu le 17/10/2026).",
  "https://filings.xbrl.org/5493008H3828EMEXB082/2025-12-31/ESEF/BE/0/5493008H3828EMEXB082-2025-12-31-1-en/reports/5493008H3828EMEXB082-2025-12-31-1-en.xhtml")
a("societe-generale", "ENV_GHG_INTENSITY", "absence_confirmee", "Le rapport financier annuel 2025 (ESEF) déclare « Non publié » pour l'ESRS E1-6 § 53 à 55 (intensité des émissions de GES brutes) (relu le 17/10/2026).",
  "https://filings.xbrl.org/O2RNE8IBXP4R0TD8PU41/2025-12-31/ESEF/FR/0/O2RNE8IBXP4R0TD8PU41-2025-12-31-1-FR/reports/O2RNE8IBXP4R0TD8PU41-2025-12-31-1-FR.xhtml")
for slug, code, d, u in [
    ("unilever", "TAX_CBCR_PUBLISHED", "unilever.com et unilever.es refusent l'identité déclarée du vérificateur (403, deux tentatives, 17/10/2026) ; rapports fiscaux par pays non lus, aucune conclusion.", "https://www.unilever.com/files/unilever-tax-paid-by-country-2024.pdf"),
    ("starbucks", "ENV_SCOPE3_DISCLOSED", "Tableaux de données du rapport d'impact 2025 : accès refusé à l'identité déclarée (403, deux tentatives, 17/10/2026) ; non lus.", "https://about.starbucks.com/uploads/2026/06/Starbucks-Fiscal-2025-Global-Impact-Report-Data-Tables.pdf"),
    ("sony", "ENV_SCOPE3_DISCLOSED", "Données environnementales de Sony : accès refusé (403, 17/10/2026) ; non lues.", "https://www.sony.com/en/SonyInfo/csr_report/environment/data/"),
    ("tesla", "ENV_SCOPE3_DISCLOSED", "Rapport d'impact : accès refusé (403, 17/10/2026) ; non lu.", "https://www.tesla.com/ns_videos/2024-extended-version-tesla-impact-report.pdf"),
    ("3m", "ENV_SCOPE3_DISCLOSED", "Rapport d'impact mondial 2025 : connexion coupée par le site (deux tentatives, 17/10/2026) ; non lu.", "https://multimedia.3m.com/mws/media/2589589O/3m-2025-global-impact-report.pdf"),
    ("kraft-heinz", "ENV_SCOPE3_DISCLOSED", "Document « Basis of Reporting » 2025 : erreur du serveur (503, 17/10/2026) ; non lu.", "https://dev.kraftheinzcompany.com/sustainability/pdf/Basis_of_Reporting_for_key_ESG_Environmental_Indicators_2025.pdf"),
    ("mercedes-benz", "GOV_BOARD_GENDER", "Page « equal participation » du groupe : accès refusé (403, 17/10/2026) ; non lue.", "https://group.mercedes-benz.com/sustainability/people/diversity/equal-participation-executive-positions.html"),
    ("la-belle-iloise", "ANI_EXPLOITATION", "Page produits citée disparue (404) et site rendu en JavaScript (17/10/2026) : preuve retirée, exploitation présumée.", "https://www.labelleiloise.fr/fr/les-produits-de-saison-0126"),
]:
    a(slug, code, "source_inaccessible", d, u)
for ligne in open(sys.argv[2], encoding="utf-8"):
    slug, url = ligne.split()
    if slug == "amazon":
        a(slug, "GOV_BOARD_GENDER", "autre_forme", "Circulaire de procuration 2026 : « of our nine independent director nominees, four are women » ; part pour l'ensemble des onze candidats non publiée (relu le 17/10/2026).", url)
    else:
        a(slug, "GOV_BOARD_GENDER", "non_trouvee", "Circulaire de procuration 2026 (DEF 14A) relue le 17/10/2026 : ni part ni nombre de femmes au conseil publiés.", url)
for slug in ("danone", "hermes", "carrefour", "kering"):
    a(slug, "TAX_HAVEN_PRESENCE", "autre_forme", "Document d'enregistrement universel 2025 relu le 17/10/2026 : pas de tableau exploitable de toutes les sociétés consolidées (Danone : seulement les principales sociétés) ; aucun décompte publié par l'Index.")
for slug in ("leclerc", "tereos", "avril", "sodiaal", "cooperl", "cristal-union"):
    a(slug, "SUP_VIGILANCE_PLAN", "non_trouvee", "Aucun plan de vigilance publié trouvé (recherche web et site de l'entreprise, 17/10/2026).")
a("mars", "SUP_SUPPLIER_LIST", "non_trouvee", "Les listes d'huileries de palme publiées en 2022-2023 ne sont plus en ligne (le lien renvoie vers une page du site, 17/10/2026) ; aucune liste plus récente trouvée.")
a("alpro", "GOV_BCORP", "non_trouvee", "Fiche B Lab « alpro-alpro-sca » introuvable (404) sur l'annuaire actuel (17/10/2026) ; certification non confirmée.", "https://www.bcorporation.net/en-us/find-a-b-corp/company/alpro-alpro-sca/")
a("maison-pommery", "ENV_GHG_TREND", "non_verifiable", "Totaux 2022 et 2025 publiés (76 000 puis 40 923 tCO2e) ; la baisse vient surtout du poste raisins (−85 %), probable changement de méthode : tendance non calculée (17/10/2026).",
  "https://filings.xbrl.org/969500M5EQJVDASURW53/2025-12-31/ESEF/FR/0/vrankenpommery-2025-12-31-1-fr/reports/vrankenpommery-2025-12-31-1-fr.xhtml")
a("totalenergies", "GEO_LOBBYING_ALIGN", "ecart", "Fiche LobbyMap relue le 17/10/2026 : note D+ (et non plus C-) ; preuve retirée, non remplacée (collecte sur LobbyMap en attente de décision, robots.txt).", "https://lobbymap.org/company/Total-5a9f086d9a2ce300529ea4eb020d1aa3")
json.dump(L, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(L), "constats")
