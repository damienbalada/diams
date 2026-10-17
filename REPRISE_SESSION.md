# Reprise de session — projet DIAMS (dépôt `awareness-score`)

Document de passation pour une nouvelle session de Claude. À lire en entier avant toute
action. État au **14/10/2026**, dernier enregistrement git `0e2ef11`.

---

## 1. Le projet en une minute

DIAMS note les entreprises **et leurs marques** pour orienter les achats des
consommateurs (piliers : environnement, social, chaîne d'approvisionnement, gouvernance,
impôt, influence politique, animaux, plastique, eau, investissements). Objectif de
l'utilisateur : **présenter le site à des journalistes**. Chaque chiffre publié doit être
sourcé, vérifiable et défendable. Priorité : exactitude et traçabilité avant couverture.

- Dépôt : `C:\Users\damie\Downloads\claude\awareness-score` — distant GitHub
  `damienbalada/diams`, branche de travail **et** principale :
  `claude/ethical-scoring-engine-gdm5xl`.
- Site : Next.js dans `apps/web`, hébergé sur Vercel (projet « diams »,
  `prj_UzSxj7BQA4cDXeFxUWo9JdJ3CeTs`, équipe `team_ISaAGM5v39wnVYVLKDsTlr9J`). Chaque
  envoi (push) sur la branche déclenche un déploiement de production.
- Base : Supabase, projet `wvqbvmjsqihqzmygrkwq` (outil MCP Supabase : `execute_sql`,
  `apply_migration`).
- Moteur de calcul : `supabase/functions/compute_score/scoring.ts` (même moteur côté site).
- Chaîne de données : `pipeline/` (Python, paquet `diams`).
- Méthodologie publique : `METHODOLOGY.md` (régénérer `apps/web/lib/methodology.ts` avec
  `node scripts/gen-methodology.mjs` après toute modification).

## 2. Règles de conduite NON NÉGOCIABLES

### Langue
- **Tout ce que l'utilisateur voit est en français**, y compris le champ `description`
  de chaque appel d'outil (« Lancer les tests », pas « Run tests »). Aucun mot anglais dans
  les réponses ; un nom propre anglais s'explique en français (« CDP, le questionnaire
  climat et eau »). Les messages de commit sont en français.
- Pronoms : ne jamais déduire le genre d'un prénom.

### Sécurité et accès
- **Ne jamais afficher un secret** (clé de service Supabase, `SITE_PASSWORD`, clés API).
- Identifiants : lus uniquement dans les fichiers locaux ignorés par git, jamais imprimés.
  - `apps/web/.env.local` : `NEXT_PUBLIC_SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`,
    `SITE_USER`, `SITE_PASSWORD` (authentification HTTP du site, utilisateur `diams`,
    usage **localhost seulement**).
    Lecture sans affichage : `PW=$(grep -E "^SITE_PASSWORD=" .env.local | cut -d= -f2- | tr -d '"\r')` puis `unset PW`.
  - `pipeline/.env` : `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` (lus par
    `diams/config.py`).
  - La clé publique (anon) de Supabase figure dans le script d'audit
    `audit_brands.mts` (outils de la session, § 8) : elle est publique par conception.
- Interdits : créer un compte, saisir un mot de passe ou une clé d'API (les clés Vercel
  sont l'affaire de l'utilisateur), contourner un CAPTCHA ou une protection anti-robot,
  **insister après une réponse 403, 429 ou 503** (on arrête et on reprend plus tard).
- Ne pas envoyer l'adresse électronique de l'utilisateur à un service.
- Ne pas aspirer le concurrent (Conscious Spend).
- Le mandat autorise : enregistrer (commit), envoyer (push) et déployer sans redemander.

### Données (« mode sérieux »)
- **Aucune écriture ad hoc en production** : les sociétés se créent par une migration
  versionnée (`supabase/migrations/AAAAMMJJHHMMSS_nom.sql`, appliquée avec l'outil MCP
  `apply_migration`), les marques par l'importeur, les preuves par les connecteurs ou par
  `import_curated`.
- **Après chaque écriture** : `node scripts/snapshot-db.mjs` (écrit
  `supabase/seed/99_snapshot.sql`), incrémenter la clé de cache dans
  `apps/web/lib/data.ts` (actuellement **`all-scores-v313`** → passer à v154, etc.),
  puis commit + push, puis vérifier le déploiement Vercel (outils MCP Vercel
  `list_deployments`, `get_runtime_errors`).
- SIREN et LEI : **toujours confirmés par un registre officiel** (annuaire
  `recherche-entreprises.api.gouv.fr`, GLEIF), jamais par simple ressemblance de nom.
- Preuves compilées par IA : statut `pending` ; elles ne sont approuvées que par
  vérification déterministe mot pour mot (`verify_curated --apply`). Délégation de
  l'éditeur pour les sources de niveau 3 (rapports volontaires, sites) :
  `verify_curated --apply --delegue` → relecteur `delegue-editeur:verifie-mot-pour-mot`,
  seulement si la citation est retrouvée mot pour mot.
- Wikidata, Open Food Facts, la recherche web : **découverte seulement, jamais preuve**.
  Wikidata répond 403 : ne plus l'utiliser.
- Ne jamais mettre `animal_free` sans preuve.
- Ne pas citer de noms de particuliers dans les citations (directeurs de publication…).
  Les dirigeants nommés dans les documents officiels des sociétés (rémunération du PDG dans
  une circulaire SEC, par exemple) sont admis : information publique (décision du 16/10/2026).
- Ne pas rattacher : marques sous licence au licencié ; copropriétés et coentreprises
  (Mamie Nova, Régilait, céréales CPW, Clearblue, Havana Club, Froneri, La Laitière) ;
  marques cédées (Timotei, Clan Campbell, Cinzano, Herta/Nestlé, Tropicana à 61 % PAI,
  Cîroc) ; importateurs ou distributeurs de marques étrangères ; cessions seulement
  annoncées (Bordeau Chesnel). Attention aux homonymes (DUC SAS restaurant ≠ volailles
  Duc ; Janneau menuiseries ; Krill réseau de vente ; Popote = Compass Group).
- Fichiers temporaires : dans le répertoire de brouillon de la session, pas dans `/tmp`.

## 3. Environnement technique (Windows)

- Shell : Bash (Git Bash) et PowerShell disponibles. **`rtk` n'est pas installé** dans le
  Bash : utiliser `git` directement (malgré le CLAUDE.md global).
- Python : `pipeline/.venv/Scripts/python.exe` ; lancer les modules depuis `pipeline/` :
  `python -m diams.<module>`. Scripts du brouillon : avec `-I`.
- Certificats (interception TLS par Cloudflare WARP / Avast) :
  - `export SSL_CERT_FILE="<brouillon>/ca-bundle.pem" PYTHONIOENCODING=utf-8`
  - Node : `NODE_EXTRA_CA_CERTS="<brouillon>/ca-bundle.pem"`
  - Le fichier existe à
    `C:/Users/damie/AppData/Local/Temp/claude/C--Users-damie-Downloads-claude-awareness-score/9662672c-e90b-45f5-b45c-1e8a8c04ceaf/scratchpad/ca-bundle.pem`
    (le copier dans le brouillon de la nouvelle session, ou le désigner tel quel).
- Les heredocs Bash contenant du Python ou des apostrophes cassent : **écrire les
  scripts et CSV avec l'outil Write**.
- Serveur local du site : `cd apps/web && NODE_EXTRA_CA_CERTS=... npx next dev -p 3000`
  (lancé depuis Bash, pas depuis l'outil d'aperçu, qui n'a pas le certificat).
- Tests : `pipeline/.venv/Scripts/python.exe -m pytest -q tests/` (210 tests, tous
  verts au 14/10) ; moteur : `supabase/functions/compute_score/scoring.test.ts`.

## 4. Règles de calcul à connaître (décisions de l'éditeur)

- **v0.7.0** : exploitation animale binaire (toute exploitation = pilier ANI à 0) ; sans
  preuve, exploitation **présumée** dans les secteurs à enjeu animal (note 0, fiabilité
  nulle, hors base). Mode et luxe : pilier social et environnement ×2.
- **v0.7.1** : objectif SBTi validé = engagement ; évolution réelle des émissions
  (`ENV_GHG_TREND`, ≤ −4,2 %/an = 1 ; deux ans minimum) ; rapports volontaires approuvés
  par délégation après vérification mot pour mot.
- **v0.7.2 / v0.7.3** : sanctions = décisions officielles seulement ; non-matérialité
  déclarée → table `obligation_exemptions`.
- **v0.7.4** : chaque décision officielle de moins de 5 ans retire 15 / 8 / 3 points
  (≥ 1 Md€ / ≥ 100 M€ / autre), plafond cumulé 25. Pas de crédit pour les baisses
  d'émissions dues à des cessions. Chiffres de sous-périmètre refusés. Indépendance du
  conseil : chiffre déclaré par l'entreprise.
- Énergie : pilier climat ×3. Il faut au moins 5 pairs pour classer.
- **Une marque ne reprend de sa racine que les indicateurs `group_level`.**
  `LAB_EGAPRO_INDEX` et `ANI_EXPLOITATION` ne le sont **pas** : une racine publiable n'a
  pas forcément des marques publiables. Publiable si fiabilité ≥ 0,30 et base ≥ 0,30.
- Une seule preuve est retenue par indicateur (nature, puis spécificité, puis date).
- Propriété : une acquisition conclue change le groupe ; une acquisition seulement
  annoncée, non.
- **14/10/2026, règle animale** : une fromagerie (ou toute société dont le code APE est
  élevage, pêche, viande, volaille, charcuterie, poisson, lait, beurre, fromage) exploite
  des animaux ; une biscuiterie aussi si ses produits contiennent beurre, œufs ou lait.
  Preuves : code APE (connecteur `import_ani_ape`) ou composition affichée sur le site
  officiel de la marque, vérifiée mot pour mot (pas les recettes ni les menus).

## 5. Outils du pipeline (commandes usuelles)

Depuis `pipeline/`, avec les variables du § 3 :

| Besoin | Commande |
|---|---|
| Importer des marques | `python -m diams.import_brand_portfolio --file curated/marques_X.csv` (contrôle) puis `--apply` |
| Importer des preuves curées | `python -m diams.import_curated --file curated/groupes_X.csv` puis `--apply` (statut pending) |
| Vérifier / approuver | `python -m diams.verify_curated --file curated/groupes_X.csv --apply [--delegue]` |
| Egapro | `python -m diams.import_egapro --file egapro.csv --apply` |
| SBTi | `python -m diams.import_sbti --file sbti.csv --apply` |
| Exploitation animale (APE) | `python -m diams.import_ani_ape --cache <brouillon>/ani_ape_cache.json --apply` |
| B Corp | `python -m diams.import_bcorp --discover --only slug1,slug2` puis déclarer la paire dans `connectors/bcorp.py` (`VERIFIED`) et `--apply` |
| Registre européen | `python -m diams.import_eu_register --file <brouillon>/eu_register.xml [--apply]` |
| Notes CDP | `python -m diams.import_cdp_scores --file <brouillon>/cdp_page.html [--apply]` |
| HATVP | open data `hatvp.fr/agora/opendata/agora_repertoire_opendata.json` (copie : `<brouillon>/hatvp_open/agora.json`) ; construire les lignes avec `<brouillon>/build_hatvp.py sortie.csv slug=SIREN …` puis `import_curated` + `verify_curated --apply` |
| Audit des libellés de fiche | exporter les preuves actives en JSON (champs code, unit, excerpt, value_numeric, normalized_value…) puis `node --experimental-strip-types apps/web/lib/audit-libelles.mts preuves.json [CODE…]` : libellés distincts par indicateur avec un exemple d'extrait, pour repérer ceux qui ne disent pas ce que dit la source (17/10/2026) ; même usage pour les alertes : `apps/web/lib/audit-alertes.mts` |
| Audit des citations publiées | `python -I outils_collecte/audit_citations.py <dossier de sortie>` : relit chaque source des preuves approuvées et y cherche chaque citation (une heure ; à relancer chaque semaine). Corriger par lot de remplacement + migration de retrait |
| Paradis fiscaux (groupes européens) | `diams/paradis_europe.py` (`compter(raw, 'FR')` sur le rapport ESEF ou le paquet AMF/DILA) ; le vérificateur refait le décompte. Jamais de zéro publié |
| Conventions judiciaires (eau) | liste du ministère de la Justice (`justice.gouv.fr/documentation/ressources/conventions-judiciaires-dinteret-public`), source `FR_CJIP` ; documents numérisés lus par OCR (`diams/ocr.py`), citation telle que reconnue |
| Financement politique (États-Unis) | `python -m diams.import_fec --dir <dossier cm26.zip, webk26.zip> [--apply]` |

Format du CSV de marques :
`brand_slug,brand_name,group_slug,sector_code,source_kind,source_url,doc,quote,observed_on,animal_free,display_name`
- `source_kind` : `legal` (rapport légal, communiqué réglementé) ou `website`.
- La citation doit figurer mot pour mot dans le document et **nommer la marque**.
- Un identifiant de marque égal à celui d'un groupe donne un CONFLIT ; un parent existant
  n'est jamais changé. Si une marque porte le nom de sa société, suffixe `-marque`.
- Si l'import crée moins de marques que de lignes OK (site momentanément muet),
  **réappliquer** le même fichier.

Format du CSV de preuves (`groupes_*.csv`) :
`entity_slug,indicator_code,source_code,nature,observed_on,value_type,value_numeric,value_boolean,value_text,normalized_value,confidence,source_url,excerpt,review_note`
- L'extrait doit contenir la citation entre « ».
- Codes de source utiles : `INPI_SIRENE`, `HATVP`, `EGAPRO`, `ESEF`, `AMF_BDIF`,
  `ANNUAL_REPORT`, `COMPANY_REPORT` (rapport volontaire ou site officiel), `GLEIF`,
  `PRODUCT_LABEL`.

Liens de groupe (filiale → mère) : migration `update entities set parent_id …` +
ligne `entity_ownership_sources` (relecteur `delegue-editeur:verifie-mot-pour-mot`),
après vérification (ex. relation GLEIF `IS_DIRECTLY_CONSOLIDATED_BY` au statut ACTIVE).

Mesure : `node <brouillon>/audit_brands.mts` → nombre de marques publiables.

## 6. Sources qui marchent / pièges connus

- **Meilleure source de marques** : liste officielle de Santé publique France « Entreprises
  et marques utilisant le Nutri-Score en France » (janvier 2026) :
  `https://www.santepubliquefrance.fr/sites/default/files/rdd/document/Entreprises-et-marques-engagees-en-faveur-de-nutri-score-France-20260224.pdf`
  (texte en cache : `<brouillon>/reports_txt/nutriscore-fr-2026.txt`, lignes :
  `<brouillon>/ns_rows.json`). Reste ≈ 400 déclarants français introuvables dans l'annuaire
  et ≈ 200 étrangers sans LEI (rendement désormais très faible).
- Mentions légales des sites officiels de marques : SIREN de l'éditeur sur la page, vérifié
  dans l'annuaire ; écarter hébergeur et agence web.
- Avis de situation Sirene (Insee), lisible mot pour mot :
  `https://api-avis-situation-sirene.insee.fr/identification/pdf/<SIRET du siège>` —
  **quota très serré** (≈ 10 avis puis 429 « Quota atteint ») : s'arrêter, reprendre plus
  tard (le connecteur le fait seul grâce au cache).
- GLEIF : `api.gleif.org/api/v1/lei-records?filter[entity.registeredAs]=<SIREN>`,
  `…/<LEI>/direct-parent-relationship`, `…/ultimate-parent-relationship`.
- Communiqués réglementés : `echanges.dila.gouv.fr/OPENDATA/AMF/ECO/…` ; documents AMF :
  `bdif.amf-france.org`.
- Illisibles pour le vérificateur : pages construites en JavaScript (Port Salut, Le Gall,
  annuaire-entreprises.data.gouv.fr), sites derrière un contrôle d'âge (Spirit France).
- Bloqués (ne pas réessayer) : nestle.com, unilever.com, suntory.com, pepsico.fr,
  barilla.com, Wikidata (403), Open Food Facts (503).
- La réponse REST de Supabase est limitée à 1 000 lignes : toujours paginer
  (`supabase_client.get_all`, en-tête `Range`).

- **17/10/2026 (méthode 0.8.5)** : toutes les devises converties en euros au taux annuel moyen de la
  BCE, dollar compris. Indicateurs **classés entre pairs** (emballages, eau, intensité carbone, écart
  et ratio de rémunération, taux effectif, paradis fiscaux, plastique vierge) : jamais de note
  précalculée ; indicateurs à **barème fixe** (mixité min(1, part/50), indépendance part/100,
  taxonomie part/100) : note toujours présente — le vérificateur refuse l'un et l'autre écart.
  Pertinence : la distribution a les piliers animal, plastique et eau ; la tech, l'équipement de la
  maison et le jouet ont le pilier eau ; l'abattage s'applique à l'alimentaire et à la distribution.
  La taxonomie reste réservée à l'énergie et à l'automobile (valeurs des autres secteurs en base,
  non affichées ; décision 17 du rapport de nuit). Une hausse des émissions compte dès un an, une
  baisse à partir de deux.
- **Piège de saisie** : dans un script Python passé par un « heredoc » bash, `\b` devient le
  caractère de contrôle 0x08 ; construire les expressions avec `chr(92)` et contrôler
  `grep -c $'\x08'` après chaque modification de `carte.ts` ou `verify_curated.py`.

## 7. État au 14/10/2026

- **2 145 marques en base, 968 publiables** (964 sur 1 671 avant le lot 82).
- Lots de marques 82 à 95 faits (≈ 470 marques alimentaires, propriété prouvée) ; lots de
  preuves « groupes » jusqu'au lot 81. Journal complet dans `METHODOLOGY.md` § 8.
- Exploitation animale : 84 preuves par code APE (≈ 30 sociétés à activité animale encore
  à lire, quota de l'Insee) + 92 marques par la composition affichée sur leur site.
- Migrations récentes : `supabase/migrations/20261014750000…` à `20261014910000…`.
- Déploiements Vercel prêts, aucune erreur d'exécution au dernier contrôle.

## 8. Outils de la session précédente (répertoire de brouillon, toujours sur le disque)

`C:/Users/damie/AppData/Local/Temp/claude/C--Users-damie-Downloads-claude-awareness-score/9662672c-e90b-45f5-b45c-1e8a8c04ceaf/scratchpad/`

- `db_dump.py` → `db_full.tsv` (slug, nom, nom affiché, G/M, parent) : **relancer juste
  avant chaque lot** et comparer les noms repliés (doublons du lot 85 nés d'un état périmé).
- `ml_auto.py entrees.tsv sortie.json` : sonde des mentions légales (SIREN de la page,
  contrôle dans l'annuaire, citation proposée) ; `ml_ctx.py`, `grep_page.py URL motif`,
  `ml_diag.py`, `ml_links.py`, `ml_editor.py` (diagnostics).
- `re_search.py "requête" …` : annuaire officiel ; `gleif_siren.py SIREN …` : GLEIF.
- `ns_todo.py`, `ns_resolve.py`, `ns_fuzzy.py`, `ns_fuzzy_sel.py` : reste de la liste
  Nutri-Score ; `mk_lot91.py`, `mk_lot92.py` : modèles de génération de lot.
- `ani_scan.py`, `mk_ani_lot.py` : passages de composition sur les sites de marques.
- `rayons.txt` + `rayons_diff.py` : liste de marques de rayon absentes de la base.
- `audit_brands.mts` : audit des marques publiables.
- Caches : `ani_ape_cache.json`, `hatvp_open/agora.json`, `eu_register.xml`,
  `cdp_page.html`, `ca-bundle.pem`.

## 9 bis. Réponses de l'éditeur au rapport de nuit (17/10/2026)

Validé et APPLIQUÉ le 17/10 (migrations 2026101706xxxx, lots 204-208, méthodologie 0.8.6) :
- (1) Conventions judiciaires hors eau (McDonald's France, Crédit Agricole CIB, LVMH) : affichées sur la fiche à titre d'information, sans note.
- (5) L'Oréal, écart de rémunération : traité comme non publié au périmètre groupe, avec les deux chiffres et la source.
- (10) Mixité des circulaires américaines : calcul admis quand le sexe des autres administrateurs se lit dans la même circulaire (biographies).
- (13) Emballages : séparer « recyclables » et « recyclés » en deux indicateurs du pilier plastique.
- (14) Eau : séparer « prélevée » et « consommée » en deux indicateurs du pilier eau.
- (15) Carrefour Veggie fusionné dans Carrefour Sensation.
- (16) Haleon : total du conseil obtenu par addition admis (72,7 %).
- (18) Piliers rendus applicables (distribution ; eau pour tech, équipement, jouet) : confirmé.
- (19) Filiale française sans LEI : admise si l'annexe consolidée du groupe la liste (Zara France).
- Suite : audit des citations chaque semaine ; reprendre leave-russia.org et le jugement TotalEnergies ;
  rapports des non cotés et sites de marques comme preuves.

Aussi appliqué le 17/10 sur réponse de l'éditeur : (12) écart plus haut / plus bas salaire en
indicateur d'information (La Nef 4,05 ; AB InBev 1 790,6) ; chasse et pêche (Decathlon : Solognac,
Caperlan), affiché seulement si vérifié ; table products et outils outils_collecte/ingredients.py
(lecture) et import_produits.py (relecture mot pour mot, écriture, lot ANI_EXPLOITATION) ; règlement
déforestation : notes forêts du CDP (ENV_CDP_FORESTS, 91 notes). Crédit Agricole CIB : convention
scannée (aucun texte lisible), non saisie.

Étiquettes de la communauté (17/10) : formulaire sur la fiche de marque (components/DepotEtiquette.tsx),
actions lib/etiquettes.ts, vérification /admin/etiquettes (recopie mot pour mot, analyse lib/ingredients.ts),
stockage privé « etiquettes-a-verifier » puis public « etiquettes », table label_submissions, colonnes
products.source_kind / purchase_date / purchase_place. Exige SUPABASE_SERVICE_ROLE_KEY côté serveur (comme
les signalements). Test de bout en bout fait en local le 17/10, données de test supprimées.
NumAlim : liquidée (juin 2023, clôture septembre 2025) ; activité reprise par 2JDB (ConsoTrust) et
Agdatahub (lui-même liquidé fin 2024) : piste abandonnée.

Appli mobile (17/10) : fiche en pastilles (essai, interrupteur dans les Réglages) ; en-tête au choix A, C
(étiquettes de verdict qui ouvrent le pilier) ou E (compteurs dépliables), réglage « En-tête de fiche ».
Décision de l'éditeur : le « fil de propriété » (groupe › marque › produit, maquette D) est réservé à
l'affichage sur ordinateur (site), pas au mobile ; la photo en bandeau (B) reste à éprouver sur des
produits hauts et étroits (bouteilles).

En discussion (explications données le 17/10, réponse attendue) : 2 taux atypiques, 3 LobbyMap
(pas de collecte automatisée déguisée en humain), 4 approbation sur copie, 6 périmètres partiels,
7 Heura, 8 Lancelot (la page « Nos marques » d'Agrial cite Lancelot Blanche Hermine), 9 alerte des
conventions sur l'eau, 11 plans de vigilance (et Decathlon : fournisseurs),
17 taxonomie, nouveaux indicateurs géopolitiques (sanctions OFAC, travail forcé UFLPA…).

## 9. En attente

**Décision de l'utilisateur demandée (Egapro)** — l'index Egapro reste attaché à la
société déclarante ; aucune marque n'en hérite. Options présentées :
- **A** (recommandée) : la marque reprend l'index de son **propriétaire direct** (mesurer
  l'effet avant d'appliquer) ;
- **B** : elle reprend celui de la **racine du groupe** (simulation : ≈ +58 marques
  publiables : Mousquetaires 24, Pierre Fabre 13, Avril 10, Ecotone 6, Interparfums 3,
  Boiron 1, Paul Hartmann 1 ; mais l'index d'une holding couvre souvent ses seuls
  salariés) ;
- **C** : ne rien changer.
Aucun changement appliqué. Si décision : modifier le moteur, la méthodologie (Règle 8),
les tests, puis mesurer avec `audit_brands.mts`.

**Travail en cours demandé par l'utilisateur : recherche pilier par pilier pour les
marques**, à continuer :
1. relancer `import_ani_ape --apply` (avis restants, quota) ;
2. compositions sur les sites des marques sans preuve animale (fromages, charcuterie,
   biscuits au beurre…), relues à la main, puis `import_curated` + `verify_curated
   --apply --delegue` ;
   **vêtements (17/10/2026, lots 217 et 225)** : `outils_collecte/compositions.py` puis
   `import_produits.py --matieres` ; fiches lues pour Dim, Arc'teryx, Alexander McQueen, Chloé,
   Salomon, Nike, Peak Performance, Gianvito Rossi et les marques Lidl (Esmara, Livergy,
   Crivit, Lupilu, Pepperts). Sites qui refusent le vérificateur (403 ou abandon après une
   nouvelle tentative) : Zara, H&M, Primark, Helly Hansen, Musto, Berluti, Givenchy, Kenzo,
   Rimowa, Chanel, Lee, Wrangler, Dior, Celine, Adidas, Decathlon (fiches), Louis Vuitton
   (fiches), Saint Laurent (fiches), Hermès (fiches), Bottega Veneta (navigateur), Peak
   Performance (après quelques pages ; preuve du lot 225 en attente). Sans réponse : Uniqlo,
   Carrefour, Gucci, Fendi, Loro Piana, Emilio Pucci, Rustler. Composition rendue par les
   scripts ou absente : Loewe, Marmot, Wilson (cuir cité dans la description seulement),
   Atomic (fiches en allemand). Auchan : In Extenso absent du plan du site ;
3. pour les sociétés moyennes non notées (Rians, Ermitage, Juraflore, Monbana, Jacquart,
   Camus, Cellier des Dauphins, bofrost*, Toupargel…) : Egapro, HATVP, registre européen,
   B Corp, sanctions (DGCCRF, Autorité de la concurrence), rapports et plans de vigilance
   quand ils existent ;
4. mesurer, journaliser dans `METHODOLOGY.md`, publier.

**À relire par un humain** : inscription HATVP de Michelin (déposée par la filiale MFPM
855200507) et de la holding Les Mousquetaires (SIREN 789169323, distinct d'ITM
722064102) ; évolution des émissions de Starbucks ; plan de vigilance de Decathlon.

**À faire par l'utilisateur** : `ADMIN_PASSWORD` et `SUPABASE_SERVICE_ROLE_KEY` dans
Vercel ; `ADMIN_PASSWORD` dans `apps/web/.env.local` ; fichier GOGEL ; PDF de Mercedes et
de Henkel ; décision sur l'offre Supabase Pro.

**Grandes marques encore absentes faute de source lisible** : Port Salut, Le Gall, Lou
Pérac, Étoile du Vercors, Mademoiselle Desserts, Bridor, Monin, Legal, Père Magloire,
Hépar, La Baleine, Le Saunier de Camargue.

**Non alimentaire (17/10/2026, lot 210)** : Open Products Facts est lu pour les codes-barres ;
relevé des scans non reconnus dans `/admin/scans`. Ajoutés : STABILO, Oxford, Pelikan, Herlitz,
Elba, scribzee, Unilux (Hamelin), VARTA, Opinel, Luminarc, Cristal d'Arques (Arc France), tesa
(Beiersdorf). Sur 685 marques d'Open Products Facts vendues en France, 168 étaient déjà dans l'Index
(63 % des produits). Restent absents : Canard WC, Baygon, Raid (site de SC Johnson : refus 429
deux fois), Monin (monin.com : erreur 530 deux fois), Signal (unilever.fr : refus 403 ; absent du
rapport ESEF d'Unilever), Paic (absent du 10-K et du rapport de Colgate-Palmolive), St Marc,
Staedtler, Faber-Castell, Duralex, Le Parfait, O-Cedar, Briochin, Baranne, Chanteclair (pages
introuvables). **Pyrex : décision de l'éditeur** — la marque appartient à Corning Incorporated et
est exploitée sous licence par International Cookware (Châteauroux, RCS 399 311 315), qui vend
les produits en Europe.

**Lot 211 (17/10/2026)** : Pouce, Better Life et Auchan Baby (Auchan) ; Carolin (Bolton
Solitaire, sans lien GLEIF avec le groupe Bolton) ; Étamine du Lys (Comptoir des Lys) ; Giotto, Lyra,
Canson, Daler-Rowney, DAS, Tratto (FILA) ; Castorama, Brico Dépôt (Kingfisher) ; Candy, Hoover
(Candy Hoover Group, Haier Europe) ; GiFi (Gigamarket). Couverture Open Products Facts France :
184 marques sur 685, 68 % des produits. Les marques Lidl non alimentaires (Parkside, Silvercrest…)
étaient déjà là. Refus deux fois : intermarche.com et magasins-u.com (Labell, Apta, marques U),
kiabi.com, leroymerlin.fr. **Livres (lot 212, décision de l'éditeur)** : secteur « Édition »
créé ; Hachette, Larousse, Hatier et Le Livre de Poche ajoutés (Lagardère SA, rapport ESEF 2024).
**Tabac exclu** sur demande de l'éditeur. Méthodologie 0.8.8.

**Pyrex (lot 213, décision de l'éditeur : « afficher les deux »)** : rattachée à International
Cookware (SIREN 399311315), qui l'exploite sous licence ; la preuve affichée nomme Corning
Incorporated, propriétaire de la marque. **Qualification des sociétés des lots 210-213** : Égapro
(6 index), SBTi (Kingfisher, VARTA, en attente), registre européen (Kingfisher), CDP (Kingfisher,
VARTA, Lagardère). Outil `scratchpad/restreint.py slug1,slug2 module …` : lance un import en ne lui
montrant que les entités citées (évite de réécrire toute la base).

**Lots 214-215 (17/10/2026)** : Salomon, Atomic, Wilson, Arc'teryx, Peak Performance (Amer Sports,
20-F) ; Charmin, Puffs (P&G, 10-K) ; Cottonelle, Poise, Andrex, Intimus, WypAll (Kimberly-Clark,
10-K) ; Legrand, Bticino (Legrand, ESEF) ; Whirlpool rattachée à Beko Europe, licenciée pour l'Europe
(10-K de Whirlpool, même règle que Pyrex) ; Terraillon ; Durance. Couverture Open Products Facts
France : 196 marques sur 685, 69 % des produits. Sans page lisible : Decathlon (marques propres),
Rossignol, Gigamic, Goliath, Le Creuset, Tupperware (propriétaire incertain depuis la faillite de
2024), Siemens électroménager (la page de BSH ne cite pas la marque), Motorola (lenovo.com : 403).

**Lot 216 (17/10/2026)** : Monin (Georges Monin SAS, SIREN 573721370), d'après la copie des mentions
légales transmise par l'éditeur (`pipeline/curated/copies/`). Copies des mentions légales d'Intermarché
(ITM Alimentaire International) et de magasins-u.com (Coopérative U) reçues : elles nomment l'éditeur du
site mais aucune marque propre (Labell, Apta, U Maison…) ; il faut leurs pages « nos marques ». SC
Johnson : capture d'écran seulement (texte illisible par OCR, et la page dit « Duck », pas « Canard ») ;
il faut la page enregistrée (Ctrl+S) et une page qui nomme Canard.

**Lot 218 (17/10/2026)** : pages enregistrées par l'éditeur (archivées dans `pipeline/curated/copies/`).
SC Johnson (S.C. Johnson & Son, Inc., sans LEI) : Glade, Oust, Duck, Drano, Fantastik, Mr Muscle,
Pledge, Scrubbing Bubbles, Shout, Windex, Ziploc, Saran, Babyganics, Ecover, Method, Mrs. Meyers,
Autan, Baygon, OFF!, Pyrel, Raid, Deb, Kiwi ; qualifiée (SBTi engagement, registre européen, CDP B/B-/C).
Marques U : Produits U, U de nos Régions, U Nature, U Collection, U Spécialiste, U Tout Petits.
**Canard WC** : la page de SC Johnson dit « Duck » ; il faut une page qui écrit « Canard ». La page
Intermarché « toutes les marques » ne cite ni Labell ni Apta.

**Lots 219-220 et autres noms (17/10/2026)** : Canard WC (SC Johnson, page canardwc.fr enregistrée par
l'éditeur) ; Corsair, Elgato (Corsair Gaming), Hansgrohe, Axor (Masco), Anios (Ecolab), Bostik (Arkema),
Marabout, Le Routard, Grasset, Fayard, Calmann-Lévy, JC Lattès, Didier, Foucher, Bescherelle (Lagardère).
Colonne `entities.aliases` : autres graphies pour reconnaître un code-barres (« procter-gamble »,
« papermate », « scjohnson »…), jamais affichées. **Suivi complet** :
`pipeline/curated/suivi_open_products_facts_france.csv` (692 marques d'Open Products Facts vendues en
France, chacune avec son cas : reconnue 246, à prouver 189, distributeur 33, non prioritaire 186, hors
France 20, tabac 18). Mesure avec la logique de l'appli : `scratchpad/suivi_opf.py`.

**Lots 221-223 (17/10/2026)** : 53 marques prouvées par les mentions légales ou le pied de page de leur
site (outil `scratchpad/trouve_mentions.py` : accueil → lien « mentions légales » → société éditrice ;
identité déclarée, une seule nouvelle tentative) et par les rapports de BSH (Siemens sous licence de
Siemens AG, Neff, Gaggenau) et de FDJ (FDJ, illiko, Loto). Nouvelles sociétés qualifiées (SBTi, Égapro,
CDP). **Retrait** d'une note CDP rattachée par homonymie (« Delta Corp Ltd. », Inde, sur Delta,
éditrice de Livoo) : contrôler le pays après `import_cdp_scores` pour un nom court. **Suivi** : 300
reconnues, 88 mises de côté (raison notée : refus du site, site injoignable, page sans propriétaire,
licence), 49 encore à prouver (petites marques), 33 de distributeur.

**Pages que le site refuse au vérificateur** : `import_brand_portfolio --copie URL=FICHIER` lit une
copie enregistrée par l'éditeur (page HTML par Ctrl+S, ou PDF par Imprimer) ; mêmes contrôles mot pour
mot, la trace porte « :copie-editeur ».

## 10. Méthode de travail attendue

- Travailler en autonomie, étape après étape, sans redemander entre les étapes ; donner de
  courts points d'étape en français.
- Lot type : `db_dump` → recherche → relecture humaine des citations → migration des
  sociétés → CSV → contrôle → `--apply` → Egapro/SBTi → instantané → clé de cache →
  commit → push → contrôle du déploiement → journal de méthodologie.
- Dire honnêtement ce qui n'est pas possible : une liste « de toutes les marques
  alimentaires vendues en France » n'existe dans aucune source officielle.
