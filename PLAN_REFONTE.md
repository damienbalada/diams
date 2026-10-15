# Plan de refonte et de relecture complète — DIAMS

Décidé avec l'éditeur le 14/10/2026. Toute séance qui reprend ce travail suit ce document et
coche l'avancement en bas.

## Principes (décisions de l'éditeur)

1. Plus de note globale, plus de lettres, plus de seuil de publication : toutes les marques sont
   publiées, avec leurs trous.
2. Quatre états par indicateur : **documenté** (source, date, citation), **présumé** (exploitation
   animale non documentée dans un secteur à enjeu), **obligatoire mais absent** (seulement après
   lecture du rapport réglementé qui confirme l'absence), **aucune information**.
3. Fiabilité par pilier, uniquement d'après la solidité des sources utilisées (officielle,
   organisme reconnu, déclaration publique).
4. Fiche = **carte d'identité** (un fait clé par pilier), chaque ligne déroule la **chronologie** des
   sources du pilier ; dernière ligne : toutes les sources de la marque (maquette :
   `maquettes/carte-identite.html`).
5. Lobbying : l'inscription à un registre devient une information, non notée.
6. Informations de presse (ex. conflits) : affichées sans être notées ; les faits établis par des
   institutions restent des faits.
7. Russie : méthodologie alignée sur la base du KSE Institute (barème à 6 niveaux).
8. Exploitation animale : repérage par Open Food Facts, preuve sur le site officiel de la marque,
   labels vegan contrôlés pour l'inverse ; en attendant, exploitation présumée affichée comme telle.

## Partie 1 — Refonte du site

- **R1. Données** : date de l'événement sur chaque preuve (en plus de la date du relevé) ; journal de
  relecture (`indicator_reviews`) ; nature « information » (affichée, non notée).
- **R2. Moteur** : construction de la carte (faits datés, états, solidité des sources, couverture) à la
  place de la note ; suppression note globale, lettres, fiabilité globale, seuil ; tests.
- **R3. Fiches** marque et groupe au format carte d'identité, d'abord pour le téléphone.
- **R4. Pages** : accueil = recherche ; classement supprimé ; alternatives → « autres marques du même
  rayon » sans ordre de mérite ; page civique et administration inchangées.
- **R5. Méthodologie** v0.8.0 : « comment on trouve et vérifie les faits ».
- **R6. Contrôle** de 30 fiches variées, téléphone, déploiement.

## Partie 2 — Relecture complète, par vagues

Méthode pour chaque entité et chaque indicateur applicable :
- preuve existante → source relue, citation reconfirmée mot pour mot, valeur, périmètre, date de
  l'événement ;
- absent → recherche dans les sources de référence de l'indicateur ;
- obligatoire et absent → lecture du rapport réglementé, absence confirmée et consignée avant tout
  affichage en rouge ;
- chaque résultat (trouvé ou non) inscrit au journal de relecture.

| Vague | Périmètre | Groupes | Marques |
|---|---|---:|---:|
| 0 | Outillage : journal, date d'événement, relecture automatique des citations, liste de contrôle | — | — |
| 1 | Groupes soumis à la CSRD | 20 | 182 |
| 2 | Grands groupes avec LEI, au moins 5 marques | 68 | 839 |
| 3 | Grands groupes sans LEI, au moins 5 marques | 11 | 145 |
| 4 | Groupes avec LEI, moins de 5 marques | 191 | 251 |
| 5 | Petites sociétés et éditeurs de marques | 653 | 728 |
| 6 | Toutes les marques : exploitation animale, labels, transparence textile, rattachement | — | 2 145 |

En continu : sources mondiales remises à jour avec leur date d'événement (CDP 2026, SBTi, KSE,
BBFAW, KnowTheChain, Fashion Checker).

Ordre : R1 + vague 0, puis les vagues 1 à 6 d'affilée (décision de l'éditeur du 14/10/2026), puis
R2 à R6. Présentation à la presse après R6 et les vagues 1 à 3 au minimum.

## Avancement

- [x] R1 — données (15/10 : `evidence.event_date`, journal `indicator_reviews`)
- [x] Vague 0 — outillage et relecture des connecteurs (outil `python -m diams.relecture`)
  - Égapro 268/268, CDP 242/242, KSE 122/122, registre UE 205 (+2 montants mis à jour, Kellanova
    sorti du registre), SBTi 149 (+3 statuts changés au 08/10 : Ecotone, Pilot validés ; Alsace
    Lait engagement retiré), FTI 22/22, KnowTheChain 21/21 (Primark rattachée à la marque et non
    au groupe ABF), Fashion Checker 16/16, Finansol 10/10, BBFAW 16/16, sans fourrure 11/11,
    B Corp 3/3.
  - Rapports électroniques : la visionneuse « stub » de filings.xbrl.org renvoie au rapport
    complet (docSetFiles) ; le lecteur le suit désormais.
  - Activité principale (avis Sirene) : 81/81 confirmées par l'annuaire officiel ; rapports
    électroniques 34/35, dépôts américains 35/35.
  - Obligation Égapro (15/10) : croisement du fichier officiel des déclarations et de l'annuaire
    (tranche d'effectif) → 296 sociétés tenues de publier (`curated/regimes_egapro_2026-10-15.csv`,
    au lieu de 33). **Correction :** l'outil de rattachement ne lisait que les 1 000 premières
    entités ; ces obligations n'ont réellement été écrites qu'après le correctif de pagination
    (297 écrites le 15/10, Hermès compris) ; 35 sans index 2025 consignées « absence_confirmee » (12 ont cessé de déclarer,
    23 n'ont jamais déclaré) ; 18 index d'UES attribués aux sociétés membres (connecteur étendu).
- [x] Vague 1 — citations 186/186 ; 13 obligations lues dans les rapports : 4 absences déclarées
  par l'entreprise (Hermès, Carrefour, Société Générale) ou constatées (BPCE, BNP Paribas), 7
  « autre forme » (sous-périmètre, par zone ou pays, écart ajusté), H&M trouvé (en attente)
- [x] Vagues 2 à 5 — citations : 217/217, 40/41, 146/148, 52/53 (2 pages de la CNIL en erreur 503,
  à reprendre) ; aucune obligation sans preuve hors Égapro ; 4 787 absences « cherché, non
  trouvé » consignées (CDP, SBTi, KSE, registre UE, HATVP).
- [~] Vague 6 — marques
  - Appartenances : 2 129 / 2 147 confirmées mot pour mot ; 17 sites bloquants (Nestlé, Unilever…),
    Thiriet hors ligne ; Kellanova et ses 10 marques rattachées à Mars (acquisition conclue).
  - Exploitation animale : lot 97 (38 marques par leur site officiel), 35 par le code APE.
  - Reste : 714 marques alimentaires rattachées par la seule liste Nutri-Score (544 sociétés,
    dont 477 à une seule marque) sans site officiel connu ; Open Food Facts indisponible (503).
  - 15/10 : recherche des sites officiels des 714 : domaines tirés des noms, site retenu seulement
    si ses mentions légales portent le SIREN du propriétaire (écrit d'un seul tenant ou par groupes
    de trois ; 40 correspondances fortuites rejetées) → 152 sites (`curated/sites_officiels_2026-10-15.csv`).
    Lecture des pages produits, tri à la main (recettes, suggestions, marques végétales, arômes et
    sites de groupe ne nommant pas la marque écartés) → lot 98 : 35 marques, 35/35 mot pour mot.
    Reste : 80 sociétés sans SIREN, ~480 marques sans site prouvé ; Open Food Facts toujours en 503.
- [x] R2 — moteur
- [x] R3 — fiches
- [x] R4 — pages
- [x] R5 — méthodologie (v0.8.0)
- [x] R6 — contrôle et mise en ligne (15/10 : 30 fiches, tests, déploiement prêt, aucune erreur)

## Partie 3 — Collecte complète (demande de l'éditeur, 15/10/2026)

« Sourcer chaque indicateur de chaque pilier, pour chaque groupe, marque et produit. » But : sur
chaque fiche, chaque indicateur porte une preuve, ou la trace d'une recherche (où, quand), ou une
absence constatée dans le rapport qui devrait le contenir. Rien n'est inventé ; le niveau produit
couvre les faits qui ne valent que pour certains produits (pas chaque produit un à un).

- [x] C1 — listes complètes : CDP, SBTi, KSE, registre UE, HATVP (vague 0) ; indice de transparence
  de la mode, KnowTheChain, BBFAW, Fur Free Retailer, Fashion Checker, Finansol (15/10 : 11 927
  recherches consignées, groupes et marques ; contrôle des noms bruts : Helly Hansen et Jockey
  rapprochés, liens ambigus exclus — Aldi, Amazon/Whole Foods, Suntory, Axa IM, Crédit Mutuel AM).
- [x] C2 — rapports réglementés des groupes cotés (15/10) : lots 100 (ESEF, AMF, sites : ~113
  preuves, ~60 groupes), 103 (Essity, Richemont, Puig, Beiersdorf, LDC : 27 preuves) et 104
  (groupes américains : 10-K, circulaires DEF 14A, rapports de durabilité : 15 preuves) ; ~440
  lectures consignées (« rapport lu, donnée absente », « publié sous une autre forme »).
  Restent sans rapport public 2025 lisible : Casino (DEU 2025 non publié, restructuration),
  Avril, Pierre Fabre, Sodiaal, Auchan (ELO), Carambar, Cofigeo ; sites refusant les robots
  (Colgate, Hasbro, Mattel, Suntory : 403) non contournés.
- [x] C3 — exploitation animale marque par marque (15/10) : lots 98-99 puis 102 (173 sites officiels
  prouvés par SIREN ou raison sociale, liste dans `curated/sites_officiels_marques_2026-10-15.csv` ;
  66 preuves : 57 exploitations, 8 offres végétales, Tossolia entièrement végétale).
- [x] C4 — registres officiels (15/10) : Autorité de la concurrence, jeu de données officiel des
  décisions (lot 101 : 17 sanctions depuis le 15/10/2021, 914 groupes « cherché sans résultat ») ;
  Commission européenne déjà couverte (16 décisions). Nouvelle tentative (15/10) : DGCCRF
  lisible par le vérificateur identifié (lot 105 : 5 amendes pour retards de paiement) ; Légifrance
  refuse le vérificateur, la CNIL est en panne (503) ; le jeu ouvert de la CNIL ne donne que des
  totaux annuels, sans nom. Rapports retrouvés : Colgate, Coty, Sodiaal, De'Longhi (anglais) ;
  Avril et Pierre Fabre lus (rapports narratifs, consignés). Quota de l'Insee toujours atteint. Égapro fait.
