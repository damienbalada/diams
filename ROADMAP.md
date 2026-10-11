# Feuille de route — DIAMS

> **DIAMS** — Documented, Independent, Auditable, Multi-criteria Scoring.
> Ambition : un outil de référence **mondial**, utilisable par tous, où chaque
> point de note est traçable jusqu'à une source publique, datée et vérifiable.

## Principe directeur (à ne jamais trahir)

> **Exhaustivité des données publiques *qui existent* + honnêteté sur les manques.**

DIAMS ne vise pas « 100 % des cases remplies » (ce serait intenable : beaucoup
d'entités n'ont aucune obligation de publication, et la presse couvre de façon
inégale). Il vise à **capter tout ce qui est publiquement disponible** et à
**afficher clairement ce qui manque** via l'indice de fiabilité. Un « je ne sais
pas encore » assumé vaut mieux qu'une note fabriquée sur du vide — c'est la
condition de la crédibilité mondiale.

Deux natures de sources, deux régimes de coût :
- **Données obligatoires / structurées** (CSRD, CbCR, dépôts réglementaires,
  index officiels, benchmarks ONG) → connecteurs **déterministes, 0 token**.
- **Presse / controverses** (texte non structuré) → extraction assistée
  (traitement du langage) + **revue humaine** obligatoire. C'est le volet coûteux.

---

## État actuel (socle — v0.4)

**Acquis :**
- Moteur de scoring pur, testé (règles 1-5, gates, méta-scores, percentile intra-secteur).
- 10 piliers + résolution d'entités (marque → groupe, héritage).
- **Connecteurs déterministes par pilier** : SBTi, CDP (climat+eau), Égapro,
  Gouvernance, Fiscalité, Benchmarks (BBFAW/KnowTheChain/FTI), BFFP, Finance
  éthique, HATVP, Yale. + résolution GLEIF/SIRENE, univers OFF/Wikidata.
- Indice de fiabilité affiché séparément ; distinction non-applicable / sans-donnée / controverse hors-note.
- **Alternatives mieux notées** par fiche (même secteur, même nature, jamais une
  entité non publiable) et **signalements** de lecteurs hors calcul (Règles 6 et 7).
- Curation manuelle sourcée en cours (CDP, sanctions, controverses) — mais **plafonne** (données derrière paywall, presse inégale).

**Mesure réelle (10/10/2026, moteur exécuté sur toute la base) :**

| | |
|---|---|
| Entités | 194 (64 groupes, 130 marques) sur 16 secteurs |
| Preuves actives | 315 |
| Fiabilité médiane d'un groupe | **9 %** (max 43 %) |
| Notes | 185 E, 9 D, aucun A/B/C |
| Publiables (≥ 30 %) | 6 entités, **1 seul groupe** |

Lecture : à ce niveau de couverture, le classement mesure la **documentation**,
pas l'éthique — le seul groupe publiable est le mieux documenté, pas le plus
vertueux. Trois causes : ~4 groupes par secteur (percentile intra-secteur non
significatif) ; Règle 1 (manquant = 0) qui condamne d'avance les petits acteurs
sans obligation de publication — précisément les alternatives à recommander ;
curation manuelle qui plafonne. **Prochaine étape : une verticale complète
(≥ 15 entités à ≥ 60 % de fiabilité) plutôt que 16 secteurs à moitié.**

### Phase 1 — verticale banque (démarrée le 10/10/2026)

Pourquoi la banque : c'est l'achat qui pèse le plus (l'épargne finance ou non
l'expansion fossile), le choix est réel (réseaux, banques en ligne, coopératives),
~15 entités couvrent le marché français, et la donnée obligatoire existe (CbCR
bancaire CRD IV, CSRD, Égapro, HATVP).

**Fait :** 19 établissements (7 têtes de groupe + La Nef + filiales et marques),
SIREN/LEI vérifiés aux registres ; Égapro pour toutes les entités juridiques
(déterministe) ; régimes CSRD et CbCR rattachés aux têtes de groupe ; lot 1 de
preuves curées (financement de l'expansion fossile BOCC 2026, inscription
HATVP) ; lot 2 depuis les rapports ESEF 2025 : taux effectif d'impôt et
déclaration pays par pays (connecteur déterministe), écart salarial, ratio de
rémunération, mixité et indépendance du conseil, publication du Scope 3
(citations verbatim vérifiées par `verify_curated`) ; labels et certifications
attestés par les bases officielles (Finansol : 10 établissements ; B Corp :
BoursoBank, innocent) ; base ONU (HCDH) des entreprises liées aux colonies
(A/HRC/63/20 : aucune entité DIAMS listée) ; lot 3 La Nef depuis son rapport
annuel 2025 (3 preuves en revue humaine : rapport d'entreprise, tier 3). Fiche :
résumé « En bref » (points forts, points de vigilance, certifications), extrait
de chaque preuve.

**Mesure au 11/10/2026 : 6 banques publiables** — La Banque Postale B (78 %),
Crédit Mutuel Arkéa B (73 %), BNP Paribas B (66 %), Crédit Agricole C (60 %),
Société Générale C (59 %), BPCE C (58 %) ; fiabilité 32 à 47 %.

**Critère de sortie :** ≥ 15 banques publiables (fiabilité ≥ 60 %), notes
étalées de A à E, une alternative mieux notée pour chaque grande banque, écarts
avec les classements ONG (Oxfam, Amis de la Terre…) documentés.

**Collecte restante, par ordre d'impact :**
1. Données **obligatoires** restantes (comptent 0 tant qu'absentes) : intensité
   carbone (seul Arkéa la publie ; Société Générale écrit qu'elle ne la publie
   pas), ratio de rémunération groupe de BNP Paribas (publié par pays seulement),
   indépendance du conseil d'Arkéa (présentation ambiguë), et tout Crédit Mutuel
   Alliance Fédérale (pas de dépôt ESEF 2025 indexé).
2. Plans de vigilance (régime FR_VIGILANCE à rattacher, avec le plan lui-même).
3. Petits acteurs (La Nef, Crédit Coopératif, néobanques) : labels faits ;
   restent les politiques d'exclusion (La Nef en revue ; celle du Crédit
   Coopératif introuvable en ligne) et la publication des financements. Sans
   obligation CSRD, ils restent sous le seuil de fiabilité : limite structurelle.
4. Exposition fossile réglementaire (Pillar 3 ESG, CRR art. 449a) en complément
   de BOCC.

**Limite structurelle identifiée :** la curation manuelle ne passe pas à
l'échelle. La suite passe par l'**ingestion par fichiers/API** via les connecteurs
(bloquée aujourd'hui par la politique réseau de l'environnement).

---

## Axe A — Couverture des données **obligatoires**, juridiction par juridiction

Chaque régime réglementaire = un connecteur déterministe. Ordre proposé (du plus
riche/structuré au plus marginal) :

| Phase | Régime | Apporte | Piliers |
|---|---|---|---|
| A1 | **UE — CSRD / ESRS** | reporting durabilité normalisé (climat, eau, social, gouvernance) | ENV, WAT, LAB, GOV, SUP |
| A1 | **UE — CbCR** | reporting fiscal pays-par-pays | TAX |
| A1 | **FR — devoir de vigilance, Égapro, HATVP** | plans de vigilance, égalité F/H, lobbying | SUP, LAB, GEO |
| A2 | **US — SEC** (10-K, climate disclosure) | émissions, risques, gouvernance | ENV, GOV |
| A2 | **UK — SECR / modern slavery act** | énergie, travail forcé | ENV, SUP |
| A3 | **Japon, Canada, Australie…** | équivalents locaux | variable |

> Réalité : le périmètre CSRD a été *réduit* (omnibus 2025). Les entités hors
> grands régimes (PME, non-cotées, Sud global) resteront **sans donnée
> obligatoire** — fiabilité basse assumée, pas un défaut.

---

## Axe B — Couverture **presse / controverses** (le volet coûteux)

Objectif : ne manquer **aucune controverse documentée** (travail forcé, pollution,
évasion fiscale, lobbying, sanctions).

- **Sources structurées d'abord** (déterministes, 0 token) : décisions de
  régulateurs (CNIL/EDPB, Commission européenne concurrence, AMF), bases ONG
  (BHRRC, InfluenceMap, Reclaim Finance). *Déjà commencé (RGPD, antitrust, lobbying).*
- **Presse non structurée ensuite** (coût réel) : extraction de faits d'articles
  via traitement du langage → **toujours en `pending`**, jamais publié sans revue.
  Encadré par : source datée obligatoire, règle de corroboration (Règle 4),
  distinction allégation / fait tranché.

> C'est ici que le « 0 token » ne tient plus. À cadrer : budget, garde-fous
> anti-hallucination, priorisation (grandes entités d'abord).

---

## Axe C — Passage à l'échelle (millions de marques)

1. **Univers de marques** : Open Food Facts + Wikidata (déjà scaffoldé) →
   ingestion massive, marque → groupe.
2. **Le scoring est gratuit** (code pur, 0 token) : le coût est borné par le
   nombre de **groupes** curés, pas de marques (héritage).
3. **Goulet = la revue humaine → TRANCHÉ** (voir [`REVIEW_MODEL.md`](./REVIEW_MODEL.md)) :
   confiance graduée par tier de source. Auto-publication des tiers 1-2
   (regulatory + ONG auditée, connecteurs déterministes) ; revue humaine
   concentrée sur les tiers 3/crowd (presse, contributif). La revue ne croît
   qu'avec le volume presse/crowd, pas avec le volume total.
4. **Contribution par le bas — amorcée** : formulaire de signalement sur chaque
   fiche → file `/admin/corrections`. Un signalement n'entre dans aucun calcul
   (Règle 7) ; il ne fait qu'ouvrir une revue. Le volume ne fait pas la vérité.
5. **Limite de calcul à lever** : les notes sont recalculées à chaque affichage
   (un appel `compute_score_input` par entité). Tenable à ~200 entités, pas à
   l'échelle du million : il faudra **matérialiser les scores** en base, avec
   invalidation sur écriture d'evidence. C'est aujourd'hui le bloc le plus
   sensible au volume, avant même le coût d'ingestion.

---

## Axe D — Accessibilité mondiale (produit)

### Langue : FR aujourd'hui → EN à terme (décidé)

**Aujourd'hui : interface en français.** Cohérent avec les sources actuelles,
massivement françaises (Égapro, HATVP, plans de vigilance, Assemblée nationale,
loi de 1995) et avec le public de départ.

**À terme : bascule en anglais**, pilotée par un déclencheur clair — **le
périmètre des sources**. Quand elles deviennent européennes (Axe A1 : CSRD, CbCR)
puis mondiales (Axe A2-A3 : SEC, UK, Japon…), le français devient un plafond :
il exclut la majorité des utilisateurs comme des contributeurs de la revue
(Axe C). L'anglais devient alors la langue par défaut, le français une locale.

Séquence : **FR seul** → **FR + EN** (le temps de la transition européenne) →
**EN par défaut** + locales.

Déjà acquis : la glose de l'acronyme est **déjà en anglais** (*Documented,
Independent, Auditable, Multi-criteria Scoring*) et DIAMS se lit à l'identique
dans les deux langues — la bascule ne coûtera aucun rebranding.

Reste à faire, le jour J : extraire les libellés dans des fichiers de traduction
(aucune chaîne en dur), traduire `METHODOLOGY.md` (le plus gros volume), et
décider du sort des `excerpt` d'evidence — rédigés en français aujourd'hui, et
qui ne sont pas de l'interface mais de la **donnée** (donc à traiter par langue
de source, pas par simple traduction).

- **Internationalisation** (i18n) : extraction des libellés, FR + EN d'abord.
- **Recherche** — ✅ par nom, slug et **groupe propriétaire** (« Unilever »
  remonte ses marques). Filtrage client sur la liste complète : instantané à
  ~200 entités, à remplacer par une recherche plein texte en base (index
  trigramme) au-delà de quelques milliers. Reste à faire : le **code-barres**
  (scan en magasin), qui suppose l'univers Open Food Facts (Axe C1).
  L'état « aucun résultat » dit explicitement que l'absence d'une marque n'est
  pas un jugement, et ouvre un signalement (Règle 7).
- **API publique** ouverte (la traçabilité est un argument de confiance).
- **Accessibilité** (a11y) et mobile-first (déjà entamé).
- Neutralité éditoriale : aucune monétisation qui compromette l'indépendance.

---

## Jalons

| Version | Contenu | État |
|---|---|---|
| **v0.4** (actuel) | socle moteur + connecteurs + curation manuelle amorcée | ✅ en cours |
| **v0.5** | déblocage réseau → ingestion réelle CSV (CDP, SBTi, benchmarks) | ⏳ nécessite accès environnement |
| **v1.0** | Axe A1 complet (UE + FR) sur les grands groupes ; presse structurée (régulateurs/ONG) ; i18n FR/EN | à venir |
| **v1.5** | Axe A2 (US/UK) ; ingestion massive marques (Axe C) ; recherche/scan | à venir |
| **v2.0** | presse non structurée à l'échelle + revue communautaire ; API publique | à venir |

---

## Ce qui restera *toujours* partiel (et c'est assumé)

- Les entités **sans obligation légale** et **sans couverture presse** : fiabilité
  basse, affichée honnêtement.
- Les données **derrière paywall** (scores CDP détaillés, etc.) : ingérées via
  fichiers officiels quand accessibles, sinon absentes.
- **On n'invente jamais.** Une case vide reste vide. La force de DIAMS n'est pas
  de tout savoir, mais de ne dire que ce qui est vrai, sourcé et daté.

---

*Document vivant. À réviser à chaque franchissement de jalon. Voir aussi
[`METHODOLOGY.md`](./METHODOLOGY.md) (règles de calcul) et
[`pipeline/CONNECTORS.md`](./pipeline/CONNECTORS.md) (connecteurs).*
