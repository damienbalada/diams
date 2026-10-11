// ⚠️ Généré automatiquement depuis METHODOLOGY.md (racine du dépôt).
// Ne pas éditer à la main : régénérer via `node scripts/gen-methodology.mjs`.
export const METHODOLOGY_MD = `# Méthodologie — DIAMS

> **DIAMS** — **D**ocumented, **I**ndependent, **A**uditable, **M**ulti-criteria
> **S**coring. Score éthique multi-critères et **traçable** : chaque point de note
> renvoie à une preuve sourcée et datée. La méthodo est publique et versionnée :
> c'est la condition de la confiance.

Version : \`0.5.1\` — périmètre : **Luxe/Mode, agroalimentaire/FMCG, hygiène-beauté,
tech, automobile, restauration, énergie, banque** (France + international).

---

## 1. Principes fondateurs

1. **Résolution d'entités d'abord.** Une marque n'est pas une entreprise.
   Bottega → Kering, Dior → LVMH. Sans table marque → filiale → groupe avec les
   % de détention, on ne sait pas à qui va l'argent. C'est le socle. Une marque
   reprend les données de son groupe pour ce qui relève du groupe (gouvernance,
   fiscalité, climat, lobbying…) et reste notée sur ses propres preuves pour ce
   qui relève du produit (Règle 8) ; la chaîne de détention s'affiche à côté de
   la note.
2. **Chaque point de score = une evidence sourcée et datée.** Jamais une opinion.
3. **Décroissance à 5 ans + fraîcheur affichée.** Un fait de 2014 ne plombe pas
   une entreprise à vie : une evidence n'est « active » que pendant 5 ans après
   sa date d'observation. La fiche affiche la **dernière mise à jour** de
   l'entité, et toute preuve de **plus de 3 ans** porte un badge « donnée
   ancienne » (rappel qu'elle expirera à 5 ans).

   **\`observed_on\` = date de VÉRIFICATION, pas date de l'événement.** Distinction
   essentielle pour les faits *structurels* toujours valables (une loi en vigueur,
   une interdiction permanente) : les dater de leur promulgation les ferait
   expirer à tort. On les date du jour où l'on a constaté qu'ils s'appliquent
   toujours, et l'\`excerpt\` mentionne la date d'origine. *(Corrigé en 07/2026 :
   19 entités françaises perdaient à tort le fait « financement politique
   interdit — loi de 1995 », pourtant toujours en vigueur.)*
4. **Faits séparés des jugements.** On stocke des indicateurs factuels
   normalisés ; la pondération est appliquée *après*, via des profils de valeurs
   configurables. Pas de score « one-size-fits-all ».
5. **Indice de confiance séparé du score.** On affiche « Note : B / Fiabilité :
   40 % ». La donnée manquante fait toujours baisser la fiabilité ; elle compte 0
   dans la note quand sa publication est obligatoire (Règle 1), et sous le seuil
   de fiabilité aucune note n'est affichée (Règle 5) : l'opacité ne produit
   jamais une bonne note visible.
6. **Normalisation intra-secteur.** Comparer une banque et un maroquinier sur le
   bien-être animal n'a pas de sens.
7. **Anti-greenwashing.** Un engagement (promesse) pèse beaucoup moins qu'un
   résultat mesuré. On les distingue explicitement.
8. **Tout est daté, versionné, auditable.** Chaque point est cliquable vers sa
   source datée.

---

## 2. Les règles de calcul (tranchées, gravées en base)

Ces règles sont stockées **en base** (\`source_tier_config\`,
\`evidence_nature_config\`, \`scoring_params\`) pour être datées, auditables et
modifiables sans redéploiement de code.

### Règle 1 — Donnée manquante : pénalisante si la publication est obligatoire

*(Révisée en v0.5.0, octobre 2026.)* Une donnée manquante fait **toujours**
baisser la fiabilité. Dans la **note**, tout dépend de l'obligation :

| Situation de l'indicateur manquant | Effet sur la note | Effet sur la fiabilité |
|---|---|---|
| Publication **légalement obligatoire** pour cette entité | compté **0** (\`missing_data_score\`) | baisse |
| **Aucune obligation** de publier | **exclu** de la note | baisse |

Un pilier sans aucune preuve **ni** obligation n'est **pas noté** : il sort de la
note globale mais tire la fiabilité vers le bas.

Exceptions : un **label ou une certification tiers** absent, ou un **indicateur
complémentaire** absent, ne baisse pas la fiabilité (voir « Labels et
certifications » et « Socle d'indicateurs », section 3) — sauf, pour le second,
si la loi impose de le publier.

**Pourquoi.** Ne pas publier ce que la loi impose est un choix, pas une excuse :
l'opacité est punie. Mais ne pas publier ce que rien n'impose n'en est pas un —
une coopérative, une PME ou une marque n'ont pas d'obligation CSRD. Pénaliser leur
silence condamnerait d'avance les petits acteurs, précisément les alternatives
qu'un consommateur cherche.

**Comment l'obligation est établie.** Un **régime** (texte légal :
\`disclosure_regimes\`) rend obligatoires certains indicateurs
(\`indicator_regimes\`), et une entité y est **soumise** par un fait sourcé et daté
(\`entity_regimes\` : base légale, URL, date) — exactement comme une preuve. Régimes
en vigueur au 10/10/2026 :

| Régime | Base légale | Indicateurs rendus obligatoires |
|---|---|---|
| Index Égapro | C. trav. art. L1142-8, D1142-4 (≥ 50 salariés) | index égalité F/H |
| Déclaration pays par pays (banques) | directive CRD IV art. 89 ; CMF art. L511-45 | CbCR publié, taux effectif d'imposition |
| CSRD — 1re vague | directive (UE) 2022/2464 + ESRS | mixité et indépendance du conseil (ESRS 2), Scope 3 et intensité carbone (E1), écart salarial F/H et ratio de rémunération (S1) |
| Devoir de vigilance | loi n° 2017-399 ; C. com. art. L225-102-4 | plan de vigilance |
| Copé-Zimmermann | loi n° 2011-103 ; C. com. art. L225-18-1 | mixité du conseil |
| Ratio PDG / salarié médian (États-Unis) | Dodd-Frank Act art. 953(b) ; Reg. S-K Item 402(u) | ratio de rémunération |

**Rattachement après lecture complète.** *(Depuis v0.5.1.)* L'obligation CSRD
n'est rattachée à une entreprise qu'une fois ses six données obligatoires lues
dans son état de durabilité : trouvées, ou constatées non publiées au niveau du
groupe (par exemple un écart salarial donné seulement par périmètre). DIAMS ne
compte jamais 0 un chiffre publié qu'il n'a pas encore lu. Hors de France,
l'obligation n'est rattachée qu'une fois la transposition nationale sourcée.
Chaque donnée écartée est justifiée dans un journal versionné
(\`pipeline/curated/*_notes.md\`).

**Limite assumée.** Un manquant obligatoire compte 0, que l'entreprise n'ait pas
publié **ou** que DIAMS n'ait pas encore collecté l'information. Dans les deux cas
la fiabilité reste basse et la note n'est pas affichée sous le seuil (Règle 5) ;
c'est aussi pourquoi la collecte commence par les données obligatoires.

**Se conformer à la loi ne rapporte pas de points** *(depuis v0.6.0, pendant de
la Règle 1)*. Pour un indicateur de **publication** (plan de vigilance, émissions
de scope 3, déclaration pays par pays), quand la loi impose à l'entreprise de
publier : publié en entier, c'est une obligation respectée — comptée dans la
fiabilité, pas dans la note ; publié en partie, c'est un manquement partiel,
compté ; absent, il compte 0. Quand la publication est **volontaire**, elle reste
un plus. Sans cette règle, un groupe français serait récompensé d'obéir à la loi
française face à un groupe américain qui n'y est pas soumis.

### Règle 2 — Solidité des sources : pondérée et plafonnée

Le \`tier\` de la source conditionne le poids ET le plafond d'impact d'une
evidence :

| Tier | Exemples | Poids | Plafond confiance | Peut pénaliser seule ? |
|------|----------|------:|------:|:--:|
| \`regulatory\`  | CSRD, devoir de vigilance, AMF, CbCR | 1.00 | 1.00 | oui |
| \`audited_ngo\` | FTI, KnowTheChain, BBFAW, CDP, SBTi | 0.80 | 0.85 | oui |
| \`press\`       | presse, allégations (BHRRC) | 0.35 | 0.45 | non (plancher 0.30) |
| \`crowd\`       | militant non audité (PETA) | 0.20 | 0.30 | non (plancher 0.40) |

Une source peu fiable **compte un peu, mais ne peut pas, seule, faire chuter un
indicateur sous son plancher** tant qu'aucune source fiable ne confirme. C'est
ce qui protège des erreurs façon « 99 % Républicain sans justification ».

### Règle 3 — Promesse vs preuve (anti-greenwashing)

La \`nature\` de l'evidence module sa valeur et plafonne l'indicateur :

| Nature | Multiplicateur | Plafond sans \`result\` |
|--------|------:|------:|
| \`result\` (résultat mesuré) | 1.00 | aucun |
| \`policy\` (politique formalisée) | 0.70 | 0.60 |
| \`commitment\` (promesse) | 0.40 | 0.50 |
| \`controversy\` (controverse) | 1.00 (pénalité) | — |

**Une promesse rapporte peu, une preuve rapporte plein.** Tant qu'aucune
evidence \`result\` ne confirme, l'indicateur est plafonné.

### Règle 4 — Corroboration des controverses (anti-parti-pris)

Une controverse **n'affecte la note que si elle est corroborée**. Sinon elle
est **affichée** (transparence) mais **exclue du calcul** (\`display_only\`) :

| Situation de la controverse | Effet sur la note |
|---|---|
| Source \`regulatory\` (justice / régulateur : décision, sanction) | ✅ pénalise (fait adjudiqué) |
| Corroborée par **≥ 2 sources distinctes** | ✅ pénalise |
| **Source unique** non réglementaire (une ONG, un rapport isolé, une allégation presse) | 🟡 affichée « hors note », n'affecte pas le score |

On ne laisse **jamais une source unique contestée piloter un score**. Le fait
reste visible sur la fiche, sourcé et daté, mais il ne devient scorant que s'il
est confirmé par une décision officielle ou recoupé par une autre source. Cela
protège le label du reproche de parti pris tout en préservant la transparence.

> Exemple : les entreprises citées par le seul rapport d'une Rapporteuse
> spéciale de l'ONU (source contestée, non recoupée par la base « consensus »
> OHCHR) sont **affichées mais non comptées** tant qu'aucune source consensus
> ou décision de justice ne corrobore.

### Règle 5 — Seuil de publication (classement)

Une entité dont la **fiabilité est sous le seuil** (\`min_confidence_to_publish\`,
30 %) n'est **pas classée** : elle apparaît dans une section « données
insuffisantes », sans note ni rang, et **sa fiche n'affiche aucune lettre**
(depuis v0.5.0). Une note bâtie sur trop peu de preuves ne doit être lue ni comme
un mauvais résultat, ni — maintenant que les manquants non obligatoires sont
exclus — comme un bon. Note, fiabilité et fraîcheur sont les **trois axes de
confiance** affichés séparément.

**Base de la note** *(depuis v0.6.0)*. La fiabilité dit ce qu'on sait d'une
entité ; la **base** dit sur quelle part du socle sa note repose réellement
(indicateurs documentés et comparables, plus les obligatoires manquants comptés
0). Une donnée connue peut ne pas entrer dans la note (obligation respectée, rang
impossible faute de pairs) : base et fiabilité diffèrent alors. Deux seuils :

- **publication** : base d'au moins **30 %** (\`min_basis_to_publish\`), en plus
  de la fiabilité ;
- **note A** : base d'au moins **50 %** (\`min_basis_for_top_grade\`) ; en
  dessous, la note est **plafonnée à 79** (B), et la fiche le dit. Être bien noté
  sur le peu qu'on sait ne suffit pas pour une note excellente — même logique
  que la Règle 3 pour les promesses. Avant cette règle, un brasseur qui ne
  publiait rien sur son conseil ni sur ses salaires obtenait 100/100 sur trois
  indicateurs favorables.

Un mauvais résultat n'est pas plafonné symétriquement : il repose, le plus
souvent, sur des obligations légales non tenues (Règle 1).

### Règle 6 — Comparaison à périmètre égal (alternatives)

Chaque fiche propose les entités **mieux notées** du même secteur. Trois bornes,
parce qu'une suggestion est un acte plus engageant qu'une note :

1. **Même secteur, même nature.** Les indicateurs applicables varient d'un
   secteur à l'autre (§ 4, pertinence sectorielle) : deux notes issues de
   périmètres différents ne mesurent pas la même chose. Et un *groupe* n'est pas
   une alternative d'achat à une *marque*.
2. **Jamais de suggestion non publiable.** Une entité sous le seuil de la
   Règle 5 est écartée. Recommander une marque sur laquelle on n'a presque rien
   reviendrait à récompenser l'absence de données — le travers exact des
   comparateurs qui font passer l'opacité pour une vertu.
3. **Fiabilité de l'alternative affichée**, et **appartenance au même groupe
   propriétaire signalée** : changer de marque au sein d'un même groupe ne change
   pas le destinataire de l'argent.

L'écart est exprimé en **points de note**, comme un fait de comparaison — sans
couleur de jugement (§ 1, neutralité).

### Règle 7 — Un signalement n'est pas une preuve

Les fiches acceptent des **signalements** de lecteurs (donnée manquante, donnée
fausse, lien mort). Un signalement :

- **n'entre dans aucun calcul**, jamais, à aucun poids ;
- ouvre une **revue humaine** (\`/admin/corrections\`) ;
- s'il est fondé, doit être **converti en \`evidence\`** avec sa propre source et
  son propre tier. La parole d'un lecteur, seule, vaut \`crowd\` (0,30) : c'est une
  piste, pas une preuve.

La note ne bouge donc **jamais** du fait d'un signalement — seulement du fait de
l'evidence sourcée qu'il a permis de créer. C'est la contribution ouverte sans
la vulnérabilité du vote : le nombre de personnes qui affirment une chose ne
change pas sa véracité.

### Règle 8 — Ce qui relève du groupe, ce qui relève de la marque

*(Révisée en v0.6.0.)* Certains indicateurs relèvent **par nature du groupe** :
une marque n'a ni conseil d'administration, ni taux d'impôt, ni registre de
lobbying, ni plan de vigilance à elle — c'est le groupe qui les publie, et c'est
lui qui reçoit l'argent. Le critère : **ce que mesure la source**. Pour les
indicateurs dont la source ne mesure que le groupe (drapeau \`group_level\` :
gouvernance, fiscalité, lobbying et influence politique, climat et eau,
rémunérations et pratiques sociales internes, devoir de vigilance, liste
fournisseurs, allégations, financements, mais aussi plastique — Break Free From
Plastic attribue les déchets audités au groupe propriétaire, le Global Commitment
évalue ses engagements — et politique de bien-être animal évaluée par le BBFAW),
la marque **reprend
les preuves de son groupe**, signalées « donnée du groupe » sur la fiche, et ses
obligations de publication (Règle 1). Une valeur reprise est classée parmi les
pairs du **secteur du groupe** : la marque porte exactement le rang de son
groupe. Une preuve propre à la marque passe toujours devant.

Restent propres à la marque les indicateurs qui relèvent du **produit** ou que la
source mesure marque par marque : matières animales (fourrure, cuir, peaux
exotiques, laine, duvet) et plafond d'exploitation animale, transparence textile
(Fashion Transparency Index), matières (Textile Exchange), labels, et l'index
Égapro (dû par chaque société employeuse). Une marque de mode qui n'utilise ni
cuir ni fourrure ne porte pas le plafond « exploitation animale » de son
propriétaire, une marque 100 % végétale sort du pilier animal de son groupe, et
la certification d'un groupe ne labellise pas ses marques. *(De v0.5.0 à v0.6.0, une marque n'héritait de rien :
presque aucune n'atteignait le seuil de publication, faute de données propres.)*

La fiche d'une marque affiche **toujours** son groupe propriétaire — avec un lien
vers sa fiche et sa note — parce que c'est lui qui reçoit l'argent. Une marque
nettement mieux notée que son groupe porte une alerte : votre achat bénéficie
tout de même au groupe.

---

## 3. Du fait au score (pipeline de calcul)

\`\`\`
evidence (faits sourcés, datés, typés)
   │  filtre : evidence_active  (approuvée + < 5 ans)
   ▼
normalisation INTRA-SECTEUR  →  valeur [0,1] par indicateur
   │  applique : poids de tier (règle 2) + nature (règle 3)
   ▼
agrégation par DIMENSION  (manquant obligatoire → 0, sinon hors note ; règle 1)
   │  applique : poids du PROFIL de valeurs choisi
   ▼
score global  +  INDICE DE CONFIANCE (séparé) = entity_coverage
\`\`\`

### Lecture de la fiche : « En bref »

*(Depuis v0.5.1.)* La fiche s'ouvre sur un résumé **mécanique**, tiré des seuls
résultats du moteur (code public \`apps/web/lib/flags.ts\`). Il n'ajoute ni donnée
ni avis :

- **Point fort** : indicateur compté dans la note, de nature *résultat* (jamais
  une promesse, Règle 3), valeur ≥ 0,7.
- **Point de vigilance** : indicateur compté à ≤ 0,3 (controverse et plafond
  compris), controverse signalée hors note (Règle 4), ou publication
  **obligatoire** absente, comptée 0 (Règle 1). Une donnée facultative absente
  n'est **jamais** un point de vigilance.
- **Certification** : label tiers attesté par la base officielle de l'organisme,
  affiché à part et jamais doublé en point fort.

Trois points au plus par colonne, chacun avec l'extrait de la source, son lien et
sa date. Une valeur **relative** (rang de la valeur publiée parmi les entreprises
du secteur) n'y figure qu'avec au moins 5 pairs : sur deux ou trois entreprises,
un écart minime suffit à classer « dernier ». La fiche indique, pour chaque
valeur relative, le nombre d'entreprises comparées. Le résumé reste affiché sous le seuil de publication : ce sont des faits
sourcés, pas une note (Règle 5).

### Labels et certifications

*(Depuis v0.5.1.)* Un label tiers compte comme **résultat** dans son pilier quand
la base officielle de l'organisme l'atteste :

- **Finansol** (INV, banque) : au moins un placement labellisé **distribué par
  l'établissement lui-même**. Les sociétés de gestion filiales et les fédérations
  régionales ne transmettent pas le label à la tête de groupe.
- **B Corp** (GOV) : certification présente dans l'annuaire B Lab, rattachée
  seulement après vérification du **domaine du site** déclaré. Un homonyme est
  écarté, jamais deviné.

Personne ne doit un label : son absence n'est **jamais** comptée 0, et elle ne
baisse pas non plus la fiabilité. L'indicateur n'existe tout simplement pas pour
l'entité (drapeau \`presence_only\` en base). Sinon la fiabilité de chaque entité
dépendrait du nombre de labels que DIAMS suit, pas de ce qu'on sait d'elle.

### Socle d'indicateurs

*(Depuis v0.6.0.)* La fiabilité mesure ce qu'on sait d'une entité **par rapport à
ce qu'on peut savoir**. Un indicateur pour lequel aucune source publique
systématique n'existe aujourd'hui (salaire décent, taux de contentieux, présence
en paradis fiscaux, part recyclée…) ou qui **recense des controverses**
(sanctions, allégations, liens avec des conflits) est **complémentaire** (drapeau
\`complementary\`) : documenté, il compte dans la note comme les autres ; absent, il
ne baisse ni la note ni la fiabilité — *sauf* si la loi impose de le publier
(Règle 1 : compté 0). L'absence de controverse recensée n'est pas une preuve de
vertu : elle ne rapporte rien non plus.

**Benchmarks à périmètre fermé.** KnowTheChain (travail forcé : 60 sociétés en
alimentation & boissons, 65 en habillement, 45 en technologies) et le BBFAW
(bien-être animal : 149 entreprises alimentaires) n'évaluent qu'une liste fermée
de sociétés. Leurs listes **complètes** sont chargées par des connecteurs
déterministes, qui lisent les données publiées par ces organismes : une
entreprise absente n'a pas été évaluée, ce n'est pas une donnée manquée. Ces
indicateurs sont donc complémentaires.

Le **socle**, ce sont tous les autres indicateurs applicables : publications
obligatoires (CSRD, Égapro, plan de vigilance, ratio de rémunération),
évaluations ouvertes à toutes les grandes entreprises (CDP, SBTi,
InfluenceMap…), registres publics. C'est sur lui que la fiabilité est calculée.
Un pilier dont le socle est vide pour une entité (et dont le plafond éventuel
n'est pas documenté) n'existe pas pour elle : il n'entre ni dans la note, ni
dans la fiabilité.

---

## 4. Dimensions

| Code | Dimension | Note |
|------|-----------|------|
| ENV | Environnement | climat, émissions, matières |
| PLA | Plastique | pollution plastique (Break Free From Plastic), emballages recyclés, réduction du plastique vierge — *pertinent selon le secteur* |
| WAT | Eau | note CDP Water, intensité de prélèvement, stress hydrique et controverses — *pertinent selon le secteur* |
| LAB | Travail & Rémunération | bien-être des **animaux humains**, en interne |
| SUP | Chaîne d'appro & Droits humains | bien-être des **animaux humains**, en amont |
| ANI | Bien-être animal (non-humain) | élevage, cuirs, laine, duvet, fourrure, tests, abattage |
| GEO | Géopolitique & Prises de position | conflits/occupations (ONU, CIJ), position Russie (Yale), lobbying (registre UE, OpenSecrets), **alignement du lobbying climat (InfluenceMap)**, financement politique |
| TAX | Fiscalité | reporting pays-par-pays (CbCR), taux effectif d'imposition, juridictions à faible imposition |
| GOV | Gouvernance | mixité et indépendance du conseil, sanctions |
| INV | Investissements & Finance éthique | finance durable, désinvestissement fossile, participations controversées — *pertinent selon le secteur* |

### Pertinence sectorielle (non-applicabilité ≠ absence de donnée)

Tous les piliers ne s'appliquent pas à tous les secteurs. Trois états distincts,
affichés clairement sur la fiche :

- ✅ **noté** — des preuves existent, le pilier compte.
- ⬜ **aucune donnée** — pilier applicable mais rien de publié : **non noté**
  (hors note globale) et la fiabilité baisse ; ses indicateurs dont la
  publication est obligatoire comptent 0 (Règle 1, l'opacité n'est pas
  récompensée).
- ➖ **non applicable au secteur** — pilier **exclu** du calcul (ni bonus, ni
  malus).

Exemples : **Plastique** (emballages grand public) ne s'applique pas à
l'automobile ; **Eau** industrielle s'applique à l'auto et l'énergie ; **Bien-être
animal** est retiré pour la banque ou les boissons ; **Investissements** ne
concerne que banque/assurance. La pertinence est pilotée par des drapeaux de
secteur (\`animal_relevant\`, \`plastic_relevant\`, \`water_relevant\`, \`inv_relevant\`).

Un indicateur peut aussi ne valoir que pour une **liste de secteurs** (table
\`indicator_sectors\`, depuis v0.6.0) : la part des investissements alignés sur la
taxonomie verte de l'UE ne s'applique qu'à l'énergie et à l'automobile, où elle
mesure la transition du cœur de métier ; ailleurs (luxe, mode, banque…) la
taxonomie couvre trop peu d'activités pour dire quoi que ce soit de la conduite
de l'entreprise. Pour un indicateur de groupe, c'est le secteur du groupe qui
compte.

### Pertinence géographique (dispositif national)

*(Depuis v0.5.1.)* Certains indicateurs mesurent le respect d'un instrument
national : l'index Égapro et le plan de vigilance sont français. Une société
américaine ne peut pas publier un index Égapro ; compter ce manque abaissait la
fiabilité de toute entité non française pour rien. Un tel indicateur ne
s'applique qu'aux entités de son pays (\`indicators.jurisdiction\`). La filiale
française d'un groupe étranger, qui publie elle-même son index, reste concernée.

### Règle ANI — Plafond d'exploitation animale (gate)

Principe antispéciste : **l'exploitation animale est la base**. S'il y a
exploitation (matières animales : cuir, laine, soie, duvet, fourrure, peaux…),
la note du pilier ANI est **plafonnée** — le bien-être ne fait que positionner
la note *sous* ce plafond, il ne le lève pas. Seules des matières non-animales
le lèvent.

| Niveau d'exploitation (\`ANI_EXPLOITATION\`) | Plafond ANI | Note max |
|---|---:|:--:|
| \`animal_free\` (aucune matière animale) | 1.00 | A |
| \`limited\` (animal marginal) | 0.55 | C |
| \`extensive\` (cuir/laine au cœur) | 0.40 | D |
| inconnu (défaut secteur mode) | 0.40 | D |

Mécanisme générique (\`dimension_gates\`) : un indicateur « gate » borne le score
d'une dimension sans entrer dans sa moyenne. Si le niveau est inconnu, on
suppose l'exploitation (plafond 0.40) — anti-opacité.

**Cas d'une marque 100 % végétale (\`animal_free\`).** Une marque sans aucun
intrant animal (ex : Alpro) n'exploite pas d'animaux : le postulat d'exploitation
ne s'applique pas. Le pilier ANI n'est alors **pas plafonné** ; il est au
contraire noté positivement sur l'indicateur « gamme sans intrant animal », car
ne causer aucun tort à un animal est le **meilleur** résultat possible sur ce
pilier. À l'inverse, un secteur sans enjeu animal (ex : boissons) voit le pilier
ANI simplement **retiré** (ni noté, ni plafonné).

### Règle PLA — Plafond « gros pollueur plastique »

Symétrique de la règle animale : un indicateur *gate* (\`PLA_POLLUTER\`, alimenté
par les audits *Break Free From Plastic*) **plafonne** la note du pilier
Plastique selon la gravité du classement — un pollueur mondial majeur ne peut pas
obtenir une bonne note plastique, même avec de beaux engagements (la preuve prime
sur la promesse). Contrairement à l'animal, l'absence de classement **ne
présume pas** le pire (plafond par défaut 1.0) : seules les marques explicitement
classées sont plafonnées.

### Méta-score « Bien-être du vivant »

Philosophie : **les humains sont des animaux**. On couvre tout le vivant. Le
calcul reste séparé par dimension (pour une normalisation intra-sujet correcte),
mais un **méta-score « Bien-être du vivant »** agrège bien-être animal
non-humain (\`ANI\`) + travail (\`LAB\`) + chaîne d'appro/droits humains (\`SUP\`).

---

## 5. Profils de valeurs (pondération)

- **Équilibré** (défaut) — toutes les dimensions comptent de façon comparable.
- **Écologie d'abord** — priorité à l'environnement.
- **Bien-être du vivant** — priorité aux animaux humains et non-humains.
- **Transparence & probité** — priorité fiscalité / gouvernance / prises de position.

Le profil appliqué par défaut est **Équilibré**. La pondération est fixée côté
serveur (pas de réglage libre côté visiteur, pour garder des notes comparables et
non « bricolables »).

**Matérialité sectorielle** *(depuis v0.6.0, décision de l'éditeur)*. Le poids
d'un pilier, fixé par le profil, est multiplié par un coefficient propre au
secteur quand l'impact du secteur s'y concentre (table
\`sector_dimension_weights\`, affichée sur la fiche). Aujourd'hui : **énergie,
pilier climat ×3** — production et vente d'énergies fossiles. Sans ce
coefficient, une major pétrolière exemplaire sur ses obligations de publication
obtenait B malgré un impact climatique de premier ordre.

---

## 6. Sources et tiers de fiabilité

Voir \`supabase/seed/99_snapshot.sql\` (section « Sources ») pour le registre complet. Règle d'or :
**CSRD / devoir de vigilance = tier 1 ; presse / PETA = tier 3.**

---

## 7. Ingestion — connecteurs déterministes

Les faits n'entrent jamais « à la main » à l'échelle. Chaque source institutionnelle
est ingérée par un **connecteur** : du code **pur et déterministe** (parsing +
normalisation + matching de noms), donc **0 token de modèle** — le coût ne dépend
pas du nombre de marques. Trois garde-fous invariants :

1. **Matching conservateur.** Un fait n'est rattaché à une entité que si les noms
   correspondent nettement (\`is_strong_match\`). En cas de doute : on saute, on ne
   devine pas.
2. **Publication graduée par tier** (voir \`REVIEW_MODEL.md\`). Les sources de
   tier 1-2 ingérées par un connecteur déterministe sont publiées directement
   (reviewer \`auto:<connecteur>\`, audit par échantillon) ; tier 3, crowd ou tier
   inconnu restent en \`pending\` jusqu'à la **revue humaine**.
3. **Niveau de rattachement explicite.** Gouvernance, fiscalité et note climat sont
   rattachées au **groupe** ; les benchmarks peuvent noter une **marque** (ex. FTI
   note Gucci). Depuis v0.6.0, une marque reprend les preuves de son groupe pour
   les seuls indicateurs de groupe (Règle 8).

| Connecteur | Pilier | Indicateur(s) | Source | Niveau |
|---|---|---|---|---|
| GLEIF / SIRENE | — | résolution d'entités (LEI/SIREN) | GLEIF, INSEE | — |
| OpenFoodFacts / Wikidata | — | univers de marques + chaînes de détention | OFF, Wikidata | — |
| HATVP | GEO | lobbying (France) | HATVP | groupe |
| Yale | GEO | position Russie | Yale CELI | groupe |
| SBTi | ENV | objectifs climat validés (anti-greenwashing) | SBTi | groupe |
| CDP | ENV, WAT | notes climat & eau A..D- (barème canonique A=1.00 … D-=0.13, F=0) | CDP | groupe |
| BFFP | PLA | classement pollueurs plastique — sévérité (gate) qui plafonne la note | Break Free From Plastic | groupe ou marque |
| Égapro | LAB | index égalité F/H (/100), rapprochement par SIREN exact | Ministère du Travail | groupe |
| Gouvernance | GOV | mixité (parité=1.0) + indépendance du conseil | déclarations CSRD/ESRS | groupe |
| Fiscalité | TAX | CbCR (oui/non), taux effectif (%), nb d'entités en paradis fiscaux | CbCR, états financiers, Tax Justice Network | groupe |
| Benchmarks | ANI, SUP | BBFAW (Tier 1→1.0 … 6→0.10), KnowTheChain (/100), FTI (%) | BBFAW, BHRRC, Fashion Revolution | groupe ou marque |
| Finance éthique | INV | politique responsable & finance durable (statut) ; financement fossile & participations controversées (valeur brute) | UN PRI, Reclaim Finance | groupe |
| Finansol | INV | label de finance solidaire (oui seulement) : distributeur nommé dans la liste officielle | FAIR (Finansol) | établissement distributeur |
| B Corp | GOV | certification B Corp (oui seulement), domaine du site vérifié | annuaire B Lab | entité certifiée |
| ONU — HCDH | GEO | présence dans la base des entreprises liées aux colonies (controverse), nom exact | Conseil des droits de l'homme (A/HRC/63/20) | entité listée |

Les quantitatifs (taux effectif, présence en paradis fiscaux) sont chargés en
**valeur brute** : c'est le moteur qui calcule le percentile intra-secteur et
applique la direction (\`higher_better\` / \`lower_better\`, ou \`closer_to_zero\` quand
l'objectif est zéro quel que soit le signe : l'écart de salaire femmes-hommes,
dont l'égalité est le meilleur rang, qu'il soit en faveur des hommes ou des
femmes). Normaliser à la main
fausserait la comparaison sectorielle.

**Au moins 5 pairs** *(depuis v0.6.0)*. Un rang n'est noté que face à au moins
cinq entreprises du même secteur ayant publié la même donnée
(\`min_peers_for_rank\`). En dessous, il ne dit rien — dans l'énergie, TotalEnergies,
Engie et Shell seuls se partageaient les rangs 83, 50 et 17 en fiscalité : la
valeur est affichée et compte dans la fiabilité, pas dans la note. Les rangs
reviennent à mesure que la collecte élargit le secteur.

---

## 8. Statut

Document vivant (v\`0.6.0\`, octobre 2026). Toute modification des paramètres de
calcul (tables de config) doit être datée et justifiée ici.

**Journal :**
- **0.6.0 (11/10/2026)** — Règle 8 révisée : une marque reprend les preuves et
  obligations de son groupe pour les indicateurs qui relèvent du groupe
  (critère : ce que mesure la source — gouvernance, fiscalité, lobbying, climat,
  eau, rémunérations, vigilance, plastique, politique animale BBFAW,
  financements), signalées « donnée du groupe » et classées parmi les pairs du
  secteur du groupe ; les indicateurs liés au produit (matières animales,
  transparence textile, labels, Égapro) restent propres à la marque. Socle d'indicateurs : un
  indicateur complémentaire (pas de source systématique, ou recensement de
  controverses) absent ne pèse ni sur la note ni sur la fiabilité, sauf
  publication obligatoire. Lobbying climat (InfluenceMap) compté dans la note
  (poids 0,8). Accueil : une seule entité par groupe sur chaque podium.
  Benchmarks à périmètre fermé (KnowTheChain, BBFAW) chargés en entier par des
  connecteurs déterministes et rendus complémentaires ; les 16 lignes saisies à
  la main avant ces connecteurs sont retirées (plusieurs contredisaient la donnée
  publiée : KnowTheChain Coca-Cola 58/100 au lieu de 29). Impact sectoriel :
  part des investissements alignés sur la taxonomie verte de l'UE
  (\`ENV_TAXONOMY_CAPEX\`, obligation \`EU_TAXONOMY_ART8\`), énergie et automobile
  seulement (pertinence sectorielle par liste), valeur absolue sur le périmètre
  réglementaire. Matérialité sectorielle (énergie : climat ×3). Se conformer à
  la loi ne rapporte pas de points (publication obligatoire faite : fiabilité
  seulement). Rang noté seulement face à 5 pairs au moins. Base de la note :
  publication à partir de 30 % du socle, note A à partir de 50 % (sinon plafond
  à 79).
- **0.5.1 (11/10/2026)** — Labels et certifications tiers (Finansol, B Corp)
  comptés comme résultats quand ils sont attestés ; leur absence ne pèse ni sur
  la note ni sur la fiabilité ; base de données ONU
  (HCDH) des entreprises liées aux colonies ; résumé « En bref » de la fiche
  (règles publiées section 3) ; extrait de chaque preuve affiché sur la fiche.
  Correctif : le pilier Investissements n'est appliqué qu'aux secteurs où il est
  pertinent (drapeau \`inv_relevant\`), comme le prévoyait la section 4.
  Pertinence géographique : Égapro et plan de vigilance ne s'appliquent qu'aux
  entités françaises. Écart de salaire femmes-hommes classé par l'écart à zéro
  (l'égalité est le meilleur rang, quel que soit le sens de l'écart). Obligation américaine du ratio PDG / salarié médian
  (Reg. S-K Item 402(u)) ajoutée à la Règle 1.
- **0.5.0 (10/10/2026)** — Règle 1 conditionnée aux obligations légales de
  publication (régimes sourcés) ; Règle 8 : chaque marque notée sur ses propres
  preuves ; Règle 5 : aucune lettre affichée sous le seuil de fiabilité.
- 0.4.0 (07/2026) — connecteurs déterministes, gates, méta-scores.
`;
