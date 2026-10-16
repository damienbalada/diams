// ⚠️ Généré automatiquement depuis METHODOLOGY.md (racine du dépôt).
// Ne pas éditer à la main : régénérer via `node scripts/gen-methodology.mjs`.
export const METHODOLOGY_MD = `# Méthodologie — Index général des marques

> Depuis la version 0.8.0 (15/10/2026), **l'Index général des marques ne note plus** : il
> publie la **carte d'identité** de chaque marque et de chaque groupe, faite de faits
> sourcés, datés et vérifiés mot pour mot, et dit ce qu'il ne sait pas. La méthode
> est publique et versionnée : c'est la condition de la confiance.

Version : \`0.8.4\` — périmètre : **Luxe/Mode, agroalimentaire/FMCG, hygiène-beauté,
tech, automobile, restauration, énergie, banque** (France + international).

---

## 0. La carte d'identité (version 0.8.0, depuis le 15/10/2026)

**Décision de l'éditeur.** La note globale, les lettres A à E, la fiabilité globale et le
seuil de publication sont abandonnés. Toute note additionne des faits selon des choix de
pondération qui restent des opinions ; l'Index publie les faits eux-mêmes et laisse chacun se
faire un avis. Toutes les marques sont publiées, avec leurs trous.

**Ce que montre une fiche.** Une ligne par pilier, avec un fait clé et le nombre
d'informations documentées (« 3/6 ») ; chaque ligne se déplie en **chronologie** des faits du
pilier, chacun avec sa valeur dans l'échelle de sa source (« 92/100 », « note A », « sortie
effective »), sa date, la solidité de sa source et la citation exacte. La dernière ligne
rassemble toutes les sources de la fiche. En tête : le propriétaire, qui reçoit l'argent des
achats, avec les preuves de l'appartenance.

**Cinq états, et seulement cinq :**

| État | Quand | Ce qu'affiche la fiche |
|---|---|---|
| Documenté | une preuve vérifiée existe | la valeur, la source, la date, la citation |
| Présumé | exploitation animale non documentée dans un secteur où elle est la règle (Règle ANI) | « non documentée, présumée dans ce secteur » |
| Obligatoire, non publié | la loi impose la donnée **et** la lecture du rapport officiel confirme son absence (journal de relecture) | l'obligation, le constat, la citation quand l'entreprise s'en explique |
| Publié sous une autre forme | publiée, mais pas sous la forme que la loi exige (sous-périmètre, par zone ou par pays, écart ajusté…) | ce qui est publié, et en quoi cela diffère |
| Aucune information | rien de publié, rien d'obligatoire | « aucune information » et, quand on a cherché dans une liste complète, où et quand |

Une donnée obligatoire absente n'est jamais affichée comme telle sans lecture du rapport qui
devrait la contenir.

**Trois niveaux : groupe, marque, produits (version 0.8.1).** Dans chaque pilier, la fiche
range les faits selon ce qu'ils couvrent :

- **groupe** : ce que publie le groupe (climat, eau, plastique, gouvernance, fiscalité, lobbying,
  Russie, sanctions, plan de vigilance…) ; la marque le reprend, signalé « donnée de … ». L'index
  Égapro vient de la société propriétaire directe ;
- **marque** : ce qui est prouvé pour la marque elle-même (exploitation animale : un seul produit
  d'origine animale suffit ; marque entièrement végétale seulement si une page officielle le dit pour
  toute la marque ; politiques animales ; indice de transparence de la mode ; B Corp) ;
- **produits** : ce qui ne vaut que pour certains produits et ne s'étend pas à la marque (produits
  100 % végétaux proposés, épargne labellisée Finansol).

Un fait documenté est rangé au niveau marque quand sa preuve porte sur la marque elle-même, au
niveau groupe quand il est repris du groupe. La fiche d'un groupe montre ses propres faits, puis,
pilier par pilier, celles de ses marques qui ont une information propre ; pour le bien-être
animal, l'état de chacune (exploitation documentée, entièrement végétale, non documentée). Sans
preuve propre au groupe, ce résumé devient le fait clé de son pilier animal.

**Solidité des sources, pilier par pilier.** Elle ne dépend que des sources utilisées :
**officielle** (loi, régulateur, registre public, rapport réglementé), **organisme reconnu**
(questionnaire CDP, SBTi, classements d'ONG publiés), **déclarative** (site de l'entreprise,
presse). Une donnée manquante ne la change pas : elle est affichée comme manquante.

**Dates.** Chaque fait porte la date de l'événement quand elle est connue (décision,
publication, validation), sinon la date de notre relevé, signalée comme telle.

**Journal de relecture public.** Chaque passage sur un indicateur (preuve reconfirmée,
corrigée, trouvée, absence confirmée, recherche sans résultat) est consigné, daté, avec sa
source (table \`indicator_reviews\`).

**Règles qui gardent un effet sur la fiche :** Règle 7 (un signalement n'est pas une preuve),
Règle 8 (ce que la marque reprend de son groupe, et l'index Égapro de son propriétaire
direct), Règle ANI (présomption d'exploitation animale), pertinence sectorielle et
géographique, sanctions limitées aux décisions officielles, refus des chiffres présentés comme
ceux du groupe quand ils ne couvrent qu'une partie. Les informations de presse sont affichées
pour ce qu'elles sont, sans être converties en verdict ; l'inscription à un registre de
lobbying est un fait (inscrit, montant déclaré), pas un mérite. Sortie de Russie : base du KSE
Institute, à six niveaux (activité poursuivie, investissements gelés, activité réduite,
suspendue, sortie annoncée, sortie effective).

<a id="seuils"></a>

### Seuils d'alerte (version 0.8.3, depuis le 15/10/2026)

La fiche ne note pas, elle signale. Quand un fait documenté franchit un seuil, il est marqué
**⚠️ alerte** (rouge) ou **🟠 point de vigilance** (orange), en tête de fiche et sur la ligne de
son pilier, avec la règle qui le déclenche. Chaque seuil s'appuie sur une référence qu'on peut
citer (loi, directive, moyenne publiée du classement) ; quand il n'en existe pas, le tableau
l'indique : « choix de l'Index ». Deux cas s'ajoutent : une donnée obligatoire dont la lecture du
rapport confirme l'absence est une alerte ; une exploitation animale présumée est un point de
vigilance. Pas de seuil pour les données qui dépendent trop du secteur (intensité carbone,
intensité d'eau) ni pour les données de contexte (dépenses de lobbying).

Certains repères sont des règles françaises : loi Copé-Zimmermann (femmes au conseil), code
Afep-Medef (administrateurs indépendants). Pour une entreprise dont le siège est hors de France,
le seuil reste celui de l'Index, mais la fiche précise que la règle française ne s'applique pas à
elle ; pour un siège dans l'Union européenne, elle rappelle l'objectif de la directive de 2022 sur
les conseils des sociétés cotées. L'index Égapro n'existant qu'en France, celui d'un groupe
étranger est celui de sa filiale française, soumise à la loi française : la fiche le dit.

**Femmes dans les instances dirigeantes (loi Rixain).** *(Décision de l'éditeur du
16/10/2026.)* Indicateur distinct de la mixité du conseil : les instances dirigeantes sont le
comité exécutif ou de direction, pas le conseil d'administration. La donnée vient des
déclarations publiques de la représentation équilibrée (export du site Égapro du ministère du
Travail), rapprochées par SIREN : part de femmes parmi les membres des instances dirigeantes,
la part parmi les cadres dirigeants étant citée à côté. Comme l'index Égapro, elle est déclarée
par chaque société employeuse d'au moins 1 000 salariés en France ; une marque reprend celle de
son propriétaire direct, et un groupe étranger celle de sa filiale française.

**Filiale française d'un groupe étranger.** *(Décision de l'éditeur du 16/10/2026.)* L'index
Égapro et la déclaration Rixain sont dus par chaque société employeuse en France ; pour un groupe
étranger, c'est sa filiale française qui les publie. Les filiales sont retenues sur trois registres :
le lien de contrôle déclaré au registre mondial des identifiants d'entités (GLEIF, lien publié et mis
à jour depuis 2025 ; un lien périmé est écarté), le SIREN actif dans le répertoire Sirene, et la
présence dans l'export Égapro ou Rixain. Une filiale principale par groupe, la plus grande d'après la
tranche d'effectif de Sirene, transmet ces données à la fiche du groupe et de ses marques, signalées
« donnée de la filiale française … ».

| Indicateur | ⚠️ Alerte | 🟠 Vigilance | Référence |
|---|---|---|---|
| Exploitation animale | un produit issu de l'exploitation animale est documenté | exploitation non documentée dans un secteur où elle est la règle | choix de l'Index |
| Bien-être animal (BBFAW) | niveau 6 sur 6 | niveau 5 sur 6 | échelle du classement BBFAW : niveau 6, aucun signe que le bien-être animal soit à l'ordre du jour ; niveau 5, à l'ordre du jour mais peu de preuves de mise en œuvre |
| Note climat CDP | note F | note D ou D- | échelle du CDP : F, l'entreprise n'a pas répondu alors qu'elle y était invitée ; D, plus bas niveau pour une entreprise qui répond |
| Note eau CDP | note F | note D ou D- | échelle du CDP : F, l'entreprise n'a pas répondu alors qu'elle y était invitée ; D, plus bas niveau pour une entreprise qui répond |
| Évolution des émissions | émissions en hausse | baisse de moins de 4,2 % par an | 4,2 % par an : rythme minimal de baisse des objectifs alignés sur 1,5 °C de la SBTi |
| Objectifs climat (SBTi) | — | engagement retiré | export de la SBTi : l'entreprise s'était engagée à fixer un objectif et ne l'a pas fait dans le délai |
| Allégations environnementales trompeuses | décision d'une autorité | — | décision publique d'une autorité |
| Pollueur plastique | parmi les dix plus gros pollueurs plastique | — | audit mondial des marques de Break Free From Plastic |
| Plastique vierge | plastique vierge en hausse | — | choix de l'Index : toute hausse |
| Transparence de la mode (FTI) | moins de 10 % des points | moins de 26 % des points | Fashion Transparency Index 2023 : moyenne des 250 marques, 26 % ; 28 % des marques sont entre 0 et 10 % |
| Salaire vital chez les fournisseurs | note E | note D | échelle du Fashion Checker : E, la marque ne verse ni ne prétend verser de salaire vital |
| Travail forcé (KnowTheChain) | moins de 10 sur 100 | moins de 20 sur 100 | KnowTheChain 2023, alimentation et boissons : moyenne 16 sur 100, la moitié des entreprises sous 10 ; seuil de vigilance : choix de l'Index |
| Index Égapro | moins de 75 sur 100 | moins de 85 sur 100 | code du travail : sous 75, l'entreprise doit prendre des mesures de correction ; sous 85, elle doit fixer des objectifs de progression |
| Écart de salaire femmes-hommes | écart de 15 % ou plus | écart de 5 % ou plus | directive européenne 2023/970 : à partir de 5 %, l'employeur doit évaluer l'écart avec les représentants du personnel ; alerte : trois fois ce seuil, choix de l'Index |
| Écart dirigeant / salarié médian | 300 fois ou plus | 100 fois ou plus | choix de l'Index : 100 fois, le dirigeant gagne en un an ce que le salarié médian gagne en un siècle |
| Sanctions d'une autorité | sanction d'une autorité | — | décision publique d'une autorité |
| Femmes dans les instances dirigeantes | moins de 15 % de femmes | moins de 30 % de femmes | loi Rixain : depuis le 1er mars 2026, au moins 30 % de chaque sexe parmi les membres des instances dirigeantes des entreprises d'au moins 1 000 salariés en France (40 % au 1er mars 2029) ; alerte : la moitié de ce minimum |
| Femmes au conseil | moins de 20 % de femmes | moins de 40 % de femmes | loi Copé-Zimmermann : 40 % au minimum dans les conseils des sociétés cotées en France ; alerte : la moitié de ce minimum |
| Administrateurs indépendants | — | moins d'un tiers d'indépendants | code Afep-Medef : au moins un tiers d'indépendants, même dans une société contrôlée |
| Taux d'impôt effectif | — | taux effectif sous 15 % | impôt minimum mondial de l'OCDE : 15 % ; un taux bas une année peut aussi venir de pertes ou de crédits d'impôt |
| Présence en Russie | activité poursuivie en Russie | activité réduite ou investissements gelés | statuts de la base Leave Russia (KSE Institute) |
| Conflit ou occupation | implication documentée | — | choix de l'Index : toute implication documentée par une source publique |

> **Historique.** Les sections 2 à 5 décrivent le calcul de la note utilisé de la version 0.1
> à la version 0.7.5. Il ne s'applique plus ; ces sections restent publiées pour la
> traçabilité des décisions passées.

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

**Ce qui compte comme « publié »** *(v0.7.3)*. La loi demande un chiffre pour
le groupe. Un chiffre publié pour l'essentiel du groupe est retenu, périmètre
écrit sur la fiche (LVMH : ratio de rémunération sur 99 % des salariés en CDI) ;
des chiffres seulement par pays, par zone ou par sous-périmètre choisi ne le
remplacent pas (BNP Paribas et L'Oréal : ratio par pays ou par zone ;
TotalEnergies : ratios sur la France seule ; BPCE : écart salarial séparé pour
Natixis ; L'Oréal : écart salarial hors conseillères de beauté, la population
la moins payée et à 90 % féminine). Une donnée **déclarée non matérielle** par
l'entreprise dans son état de durabilité audité n'est pas imposée : elle n'est
pas comptée 0, et la fiche l'indique, citation à l'appui (LVMH : écart salarial
non corrigé). Une donnée simplement « non publiée » ou « non chiffrée » reste
comptée 0 (Société Générale, intensité carbone ; Hermès, écart salarial).
Enfin, « non trouvée » doit vouloir dire « non publiée » : Crédit Mutuel Alliance
Fédérale avait 7 données comptées 0 parce que son rapport n'avait pas été lu ;
elles sont désormais relevées.

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
| Représentation équilibrée (loi Rixain) | loi n° 2021-1774, art. 14 ; C. trav. art. L1142-11 à L1142-13 (≥ 1 000 salariés) | femmes dans les instances dirigeantes |
| Ratio PDG / salarié médian (États-Unis) | Dodd-Frank Act art. 953(b) ; Reg. S-K Item 402(u) | ratio de rémunération |

**Rattachement après lecture complète.** *(Depuis v0.5.1.)* L'obligation CSRD
n'est rattachée à une entreprise qu'une fois ses six données obligatoires lues
dans son état de durabilité : trouvées, ou constatées non publiées au niveau du
groupe (par exemple un écart salarial donné seulement par périmètre). L'Index ne
compte jamais 0 un chiffre publié qu'il n'a pas encore lu. Hors de France,
l'obligation n'est rattachée qu'une fois la transposition nationale sourcée.
Chaque donnée écartée est justifiée dans un journal versionné
(\`pipeline/curated/*_notes.md\`).

**Limite assumée.** Un manquant obligatoire compte 0, que l'entreprise n'ait pas
publié **ou** que l'Index n'ait pas encore collecté l'information. Dans les deux cas
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

**Un objectif, même validé, est une promesse** *(v0.7.1, décision de
l'éditeur)*. Les objectifs climat validés par la SBTi sont des engagements sur
l'avenir : comptés à 40 % (objectif aligné sur 1,5 °C), 24 % (autre objectif
validé) ou 20 % (engagement à en fixer un). La preuve est ailleurs :
l'**évolution réelle des émissions** (indicateur \`ENV_GHG_TREND\`), le résultat
du pilier climat. Avant cette règle, Shein, dont les émissions augmentent,
obtenait 100 sur l'environnement grâce à son seul objectif validé.

### Évolution réelle des émissions (\`ENV_GHG_TREND\`)

Rythme annuel moyen d'évolution des émissions totales publiées par
l'entreprise (scopes 1, 2 et 3), entre l'année de référence et la dernière année
publiée dans un même tableau : r = (E dernière / E référence)^(1/années) − 1.

| Rythme annuel | Note |
|---|---:|
| baisse de 4,2 % par an ou plus (trajectoire 1,5 °C de la SBTi) | 1 |
| baisse plus lente | proportionnelle |
| pas de baisse, ou hausse | 0 |

- Poids 1,5, le plus lourd du pilier climat : c'est son résultat.
- **Une baisse ne compte que sur deux ans au moins** (sur une seule année, elle
  peut tenir aux ventes, aux prix ou à la météo) ; une hausse compte quelle que
  soit la durée : elle montre que les émissions ne baissent pas.
- Ne s'applique pas à la banque et à l'assurance : leurs émissions sont surtout
  financées, sur un périmètre qui change d'une année à l'autre.
- **Une baisse due aux cessions ne compte pas** *(validé par l'éditeur le
  13/10/2026)* : quand les émissions d'un pétrolier baissent surtout parce qu'il a
  vendu des actifs ou moins d'énergie (Shell, TotalEnergies), les émissions changent
  de propriétaire sans disparaître ; aucune baisse n'est retenue.
- Sources : le rapport réglementé (état de durabilité CSRD, rapport annuel
  légal) ; hors de l'Union, le rapport volontaire de l'entreprise (niveau 3).
- Les deux totaux sont cités mot pour mot ; le rythme et la note sont recalculés
  par la vérification automatique.

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

### Décisions d'autorités : sanctions et allégations trompeuses

*(v0.7.2)* Deux indicateurs de controverse ne retiennent **que des décisions
officielles** de moins de 5 ans, citées mot pour mot depuis le communiqué de
l'autorité ; jamais un article de presse ou un recensement d'ONG.

| Indicateur | Décision retenue | Gravité |
|---|---|---:|
| Sanctions d'une autorité (\`GOV_SANCTIONS\`, gouvernance) | amende d'au moins 1 Md€ | 0,9 |
| — concurrence, marchés numériques, données personnelles | de 100 M€ à 1 Md€ | 0,7 |
| | moins de 100 M€, ou infraction constatée sans amende (immunité de clémence) | 0,5 |
| Allégations environnementales trompeuses (\`ENV_GREENWASHING\`) | amende d'une autorité de protection des consommateurs | 0,8 |
| | engagements de retrait obtenus après enquête, sans sanction | 0,5 |

- La note de l'indicateur est 0,5 × (1 − gravité) : 0,05 pour une amende d'au
  moins 1 Md€, 0,25 pour une amende de moins de 100 M€.
- **Plusieurs décisions : la plus grave compte** dans l'indicateur, et c'est elle
  que la fiche affiche.
- **Retrait de points sur la note globale** *(v0.7.4, décision de l'éditeur du
  13/10/2026 : « une règle plus sévère »)*. Une condamnation n'est pas une affaire
  de gouvernance parmi d'autres : en plus de l'indicateur, **chaque décision**
  retire des points à la note globale (sur 100), selon l'amende — **15 points** à
  partir de 1 milliard d'euros, **8** à partir de 100 millions, **3** sinon
  (amende moindre, infraction constatée, immunité de clémence). Les décisions
  s'additionnent, dans la limite de **25 points**. Avant la v0.7.4, une amende d'un
  milliard ne coûtait que 5 à 7 points ; Apple (cinq décisions, dont 1,8 Md€ de la
  Commission européenne en 2024), Google ou Meta en perdent désormais 25. La fiche affiche le retrait et
  chaque décision, avec sa source.
- La sanction est rattachée à **l'entité nommée par la décision** : la marque
  Gucci (prix de revente imposés), pas tout le groupe Kering ; une sanction du
  groupe (Stellantis) vaut pour ses marques.
- **Une infraction constatée compte, même sans amende** : Mercedes-Benz, qui a
  dénoncé l'entente sur le recyclage des véhicules (2002-2017) et n'a donc pas
  été condamnée à payer, y a participé pendant quinze ans.
- Indicateurs complémentaires : une entreprise jamais sanctionnée n'est pas
  pénalisée, mais n'en tire aucun point.
- **Autorités couvertes** (relevé systématique des groupes suivis depuis
  octobre 2021) : Commission européenne (concurrence, marchés et services
  numériques ; tous ses communiqués d'amende), Commission irlandaise de
  protection des données (autorité chef de file des géants du numérique en
  Europe), CNIL (tant qu'elle publie le nom de l'entreprise sanctionnée : ses
  anciennes décisions sont anonymisées et ne peuvent plus être citées),
  Autorité de la concurrence française, autorité italienne de la concurrence
  et des consommateurs (AGCM). Pas encore couvertes : les autorités
  américaines (FTC, ministère de la Justice, SEC) et les autres autorités
  nationales européennes. Légifrance, qui publie les délibérations de la CNIL,
  bloque les programmes : seules les actualités de la CNIL sont lues.
- La vérification automatique retrouve chaque citation dans le communiqué
  officiel (Commission européenne : texte servi par l'interface publique du
  « press corner », sa salle de presse en ligne), relit le montant cité et
  recalcule la gravité ; une gravité qui ne correspond pas au montant bloque
  l'approbation.
- **Limite connue.** Comme tout indicateur, une sanction pèse d'autant plus que
  le pilier gouvernance compte peu d'autres données : chez Toyota, Mercedes-Benz,
  Apple, Meta ou Mondelez, la composition du conseil n'est pas encore relevée
  (publiée en graphique ou dans des rapports non téléchargeables par un
  programme), si bien que la sanction fait seule la note du pilier, avec une
  fiabilité de 33 %. À même amende, BMW (conseil documenté) perd 6 points,
  Toyota 15.

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
(Fashion Transparency Index), matières (Textile Exchange) et labels. Une marque de mode qui n'utilise ni
cuir ni fourrure ne porte pas le plafond « exploitation animale » de son
propriétaire, une marque 100 % végétale sort du pilier animal de son groupe, et
la certification d'un groupe ne labellise pas ses marques. *(De v0.5.0 à v0.6.0, une marque n'héritait de rien :
presque aucune n'atteignait le seuil de publication, faute de données propres.)*

**Index Égapro : celui du propriétaire direct** *(v0.7.5, décision de l'éditeur du
14/10/2026)*. L'index est dû par chaque société employeuse d'au moins 50 salariés :
il ne relève pas du groupe, car l'index d'une holding ne couvre que ses propres
salariés. Mais une marque est fabriquée et vendue par la société qui la détient
directement : la marque reprend donc l'index, l'obligation de le publier et le
pays de **son propriétaire direct**, et non ceux de la racine du groupe (drapeau
\`indicators.owner_level\`). Exemples : les marques des Mousquetaires reprennent
l'index d'ITM Entreprises, celles d'Orangina Schweppes l'index d'Orangina
Schweppes France, et non celui de Suntory. La fiche nomme la société dont
l'index est repris ; un index propre à la marque passe devant. Une société
filiale (qui n'est pas une marque) reste notée sur son propre index.

La fiche d'une marque affiche **toujours** son groupe propriétaire — avec un lien
vers sa fiche et sa note — parce que c'est lui qui reçoit l'argent. Une marque
nettement mieux notée que son groupe porte une alerte : votre achat bénéficie
tout de même au groupe.

**Propriétaire à jour.** Un rachat ou une scission achevés changent le groupe
dont une marque relève, à la date de réalisation et sur la foi d'une source
officielle : Kellogg's (Kellanova) relève de **Mars** depuis le 11/12/2025 ;
Magnum et Ben & Jerry's relèvent de **The Magnum Ice Cream Company**, séparée
d'Unilever le 06/12/2025. Une opération annoncée mais non réalisée ne change
rien (Kenvue, dont le rachat par Kimberly-Clark n'était pas conclu au 13/10/2026).

**Appartenance prouvée.** Une marque n'est rattachée à un groupe que sur une
citation, retrouvée mot pour mot, d'un document officiel du propriétaire : rapport
annuel légal (document d'enregistrement universel, rapport 10-K ou 20-F, rapport
au format ESEF), registre public (nom commercial déclaré au répertoire SIRENE), ou,
à défaut, page « nos marques » ou rapport volontaire du groupe. La fiche de chaque
marque affiche cette preuve (« Pourquoi ce groupe ? »). Le contrôle est
automatique : la citation doit figurer dans le document et nommer la marque ; une
marque déjà rattachée à un autre groupe n'est jamais déplacée sans décision
motivée. Une source légale est validée d'office ; une page web ou un rapport
volontaire l'est par délégation de l'éditeur, sous la même condition de citation
exacte. Deux cas particuliers :

- **Licences.** Une marque exploitée sous licence n'est pas rattachée au
  licencié : Coty fabrique les parfums Hugo Boss ou Gucci, Puig ceux de Christian
  Louboutin, Interparfums ceux de Montblanc, mais ces marques appartiennent à
  d'autres. Seules les marques que le groupe déclare détenir en propre sont
  rattachées.
- **Homonymes.** Deux marques de même nom chez deux propriétaires sont
  distinguées à l'affichage : Lotus (papier, Essity) et Lotus (biscuits, Lotus
  Bakeries) ; Lustucru (riz, Ebro Foods). Le contrôle porte toujours sur le nom
  tel qu'il est écrit dans la source.

Les enseignes de distribution (Intermarché, Monoprix, Carrefour Market…) et les
marques propres des distributeurs (Reflets de France, Simpl…) sont rattachées
de la même façon à leur groupe.

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
dépendrait du nombre de labels que l'Index suit, pas de ce qu'on sait d'elle.

### Socle d'indicateurs

*(Depuis v0.6.0.)* La fiabilité mesure ce qu'on sait d'une entité **par rapport à
ce qu'on peut savoir**. Un indicateur pour lequel aucune source publique
systématique n'existe aujourd'hui (salaire décent, taux de contentieux, présence
en paradis fiscaux, part recyclée…) ou qui **recense des controverses**
(sanctions, allégations, liens avec des conflits) est **complémentaire** (drapeau
\`complementary\`) : documenté, il compte dans la note comme les autres ; absent, il
ne baisse ni la note ni la fiabilité — *sauf* si la loi impose de le publier
(Règle 1 : compté 0). L'absence de controverse recensée n'est pas une preuve de
vertu : elle ne rapporte rien non plus. *(v0.7.3)* Documenté, il ne peut pas
non plus **baisser** la fiabilité du pilier : une donnée tirée d'un rapport
volontaire (fiabilité plafonnée) s'ajoute à la note, mais la fiabilité retenue
est au moins celle qu'aurait le pilier sans elle. Savoir davantage ne rend
jamais une fiche « moins fiable ».

**Benchmarks à périmètre fermé.** KnowTheChain (travail forcé : 60 sociétés en
alimentation & boissons, 65 en habillement, 45 en technologies) et le BBFAW
(bien-être animal : 149 entreprises alimentaires) n'évaluent qu'une liste fermée
de sociétés. Leurs listes **complètes** sont chargées par des connecteurs
déterministes, qui lisent les données publiées par ces organismes : une
entreprise absente n'a pas été évaluée, ce n'est pas une donnée manquée. Ces
indicateurs sont donc complémentaires.

**Indicateurs nés d'une obligation légale.** L'écart de rémunération non ajusté,
l'intensité carbone et les émissions de scope 3 (CSRD), la part verte des
investissements (taxonomie de l'UE) et le ratio de rémunération (CSRD ; Reg. S-K
aux États-Unis) n'ont qu'une source systématique : l'obligation de les publier.
Ils ne sont au socle que pour les entreprises qui y sont soumises — là, un
manquant compte 0 (Règle 1). Ailleurs, publiés volontairement, ils comptent ;
absents, ils ne pèsent ni sur la note ni sur la fiabilité : rien n'oblige un
groupe américain ou japonais à les publier.

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

Principe antispéciste : **l'exploitation animale est la base**, et elle ne
se mesure pas au degré : *« si une marque utilise et exploite des animaux, sa
note est au plus bas dans cette catégorie »* (décision de l'éditeur, v0.7.0).
Toute exploitation — matières animales (cuir, laine, soie, duvet, fourrure,
peaux), ingrédients d'origine animale (lait, viande, œufs, miel), tests sur
animaux — met le pilier ANI à **0**, même marginale : il n'y a pas d'excuse de
marginalité. Le bien-être animal (labels, classements) ne lève pas ce plancher ;
seule une gamme sans intrant animal le lève.

| Niveau d'exploitation (\`ANI_EXPLOITATION\`) | Note du pilier ANI |
|---|---:|
| aucun intrant animal (\`animal_free\`) | notée sur ses indicateurs, jusqu'à 100 |
| exploitation, même marginale | 0 |
| inconnu (secteur à enjeu animal) | 0 — exploitation présumée |

Mécanisme générique (\`dimension_gates\`) : un indicateur « gate » borne le score
d'une dimension sans entrer dans sa moyenne. Si le niveau est inconnu, on
suppose l'exploitation — anti-opacité. Cette présomption s'applique à **toute**
entité d'un secteur à enjeu animal (alimentation, restauration, hygiène-beauté,
mode, luxe, horlogerie, vins et spiritueux…), qu'on sache quelque chose d'autre
sur elle ou non *(v0.6.1, étendue à tous ces secteurs en v0.7.0)* : sans cela,
une enseigne sans aucun label échappait au pilier animal, quand celle qui
affichait le label « sans fourrure » y était plafonnée — un label faisait
baisser la note. Le pilier noté par présomption a une fiabilité nulle et n'entre
pas dans la base de la note, jusqu'à ce que l'exploitation soit documentée (ou
exclue). Les plafonds qui valent 1 par défaut (lobbying, plastique) ne présument
rien.

**Documenter l'exploitation (décision de l'éditeur, 14/10/2026).** Une fromagerie
exploite des animaux par définition ; une biscuiterie aussi, si ses produits
contiennent du beurre, des œufs ou du lait. Deux preuves en découlent :
- **activité officielle** : la société dont l'activité principale (code APE, lu mot pour
  mot dans l'avis de situation Sirene de l'Insee) est d'élever ou de pêcher des
  animaux, ou de transformer ou commercialiser viande, volaille, charcuterie, poisson,
  lait, beurre ou fromage, a l'exploitation documentée, ainsi que ses marques directes
  (sauf une marque \`animal_free\`). Codes exclus à dessein : glaces et sorbets (10.52Z),
  commerce de gros mêlant produits laitiers et huiles (46.33Z), plats préparés
  (10.85Z) ;
- **présentation des produits par la marque** : un passage du site officiel qui nomme
  la marque et un ingrédient ou produit animal (« pur beurre », « 98 % de lait »,
  « saucisson », « foie gras »…), vérifié mot pour mot. Les recettes et les menus du
  site ne comptent pas : seule compte la composition de ce que la marque vend.

La note du pilier ne change pas (elle était déjà à 0 par présomption) ; sa fiabilité,
elle, devient celle de la preuve, et le pilier entre dans la base de la note.

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

**Évolution réelle du plastique vierge** (\`PLA_REDUCTION\`, *v0.7.3*). Sous ce
plafond, le pilier est noté sur le résultat : l'évolution du tonnage de
plastique vierge publiée par l'entreprise, ramenée à un rythme annuel moyen
(r = (1 + variation)^(1/années) − 1), puis classée entre pairs du secteur (la
baisse la plus rapide obtient la meilleure note). Tonnage absolu seulement :
une baisse « par unité vendue » ne dit rien du plastique mis sur le marché. Une
baisse ne compte que sur deux ans au moins. Premières données (2025) : L'Oréal
−37 % depuis 2019, Unilever −29 % depuis 2019, Nestlé −28 % depuis 2018,
Danone −17,7 % depuis 2019, PepsiCo −5 % puis −6 % (2024, 2025), Procter &
Gamble −14 % depuis l'exercice 2017-18, Mondelez −11,5 % depuis 2020, Coca-Cola
2,83 millions de tonnes en 2023, 2,71 en 2025. Avant la v0.7.3, l'indicateur
notait la signature de l'engagement de la Fondation Ellen MacArthur, une
promesse : aucune preuve n'avait été approuvée.

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
obtenait B malgré un impact climatique de premier ordre. **Mode et luxe,
chaîne d'approvisionnement ×2 et environnement ×2** *(v0.7.0)* : la fabrication
est sous-traitée (salaires, conditions de travail chez les fournisseurs) et
l'impact environnemental tient aux matières et aux volumes produits. Sans ce
coefficient, le groupe le plus transparent de la mode jetable obtenait A.

---

## 6. Sources et tiers de fiabilité

Voir \`supabase/seed/99_snapshot.sql\` (section « Sources ») pour le registre complet. Règle d'or :
**CSRD / devoir de vigilance = tier 1 ; presse / PETA = tier 3.**

**Rapports volontaires des entreprises (niveau 3).** Hors de l'Union, aucun
rapport de durabilité n'est imposé : les émissions d'Apple, Microsoft, Shein ou
PepsiCo ne figurent que dans leurs rapports volontaires (source
\`COMPANY_REPORT\`) ; une société non cotée comme Lactalis publie aussi son plan de
vigilance dans un rapport volontaire. Ce sont des déclarations de l'entreprise, à
confiance plafonnée. Seul un rapport légal (rapport annuel, document
d'enregistrement universel, déclaration non financière imposée par la loi du pays)
est classé « rapport annuel légal ». L'éditeur a délégué leur validation (11/10/2026), à une condition :
la citation est retrouvée **mot pour mot** dans le document, et les calculs sont
refaits par la vérification automatique. Ces preuves portent l'étiquette de
relecture \`delegue-editeur:verifie-mot-pour-mot\`.

---

## 7. Ingestion — connecteurs déterministes

Les faits n'entrent jamais « à la main » à l'échelle. Chaque source institutionnelle
est ingérée par un **connecteur** : du code **pur et déterministe** (parsing +
normalisation + matching de noms), donc **0 token de modèle** — le coût ne dépend
pas du nombre de marques. Trois garde-fous invariants :

1. **Matching conservateur.** Un fait n'est rattaché à une entité que si les noms
   correspondent nettement (\`is_strong_match\`). En cas de doute : on saute, on ne
   devine pas. Une société identifiée par son SIREN n'est rapprochée que par son SIREN.
   Les sigles sont conservés (« H&M » ≠ « B&S », « AT&T ») ; un nom réduit à des mots
   génériques (« Group ») ne correspond à rien ; deux noms qui portent des lettres
   isolées différentes (« Bio-D », « U BIO ») restent distincts (audit du 16/10/2026).
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
| Information réglementée | — | rapports financiers annuels et documents d'enregistrement universels des sociétés cotées en France (paquets ESEF) | info-financiere.gouv.fr (DILA), base BDIF de l'AMF, filings.xbrl.org | groupe |
| Annuaire des entreprises | — | SIREN et noms commerciaux déclarés (preuve d'appartenance d'une marque) | recherche-entreprises.api.gouv.fr (données INSEE) | groupe |
| OpenFoodFacts / Wikidata | — | univers de marques + chaînes de détention | OFF, Wikidata | — |
| HATVP | GEO | lobbying (France) | HATVP | groupe |
| Yale | GEO | position Russie | Yale CELI | groupe |
| SBTi | ENV | objectifs climat validés (anti-greenwashing) | SBTi | groupe |
| CDP | ENV, WAT | notes climat & eau A..D- (barème canonique A=1.00 … D-=0.13, F=0) | CDP | groupe |
| BFFP | PLA | classement pollueurs plastique — sévérité (gate) qui plafonne la note | Break Free From Plastic | groupe ou marque |
| Égapro | LAB | index égalité F/H (/100), rapprochement par SIREN exact | Ministère du Travail | société (repris par ses marques) |
| Gouvernance | GOV | mixité (parité=1.0) + indépendance du conseil | déclarations CSRD/ESRS | groupe |
| Fiscalité | TAX | CbCR (oui/non), taux effectif (%), nb d'entités en paradis fiscaux | CbCR, états financiers, Tax Justice Network | groupe |
| Benchmarks | ANI, SUP | BBFAW (Tier 1→1.0 … 6→0.10), KnowTheChain (/100), FTI (%) | BBFAW, BHRRC, Fashion Revolution | groupe ou marque |
| Finance éthique | INV | politique responsable & finance durable (statut) ; financement fossile & participations controversées (valeur brute) | UN PRI, Reclaim Finance | groupe |
| Finansol | INV | label de finance solidaire (oui seulement) : distributeur nommé dans la liste officielle | FAIR (Finansol) | établissement distributeur |
| B Corp | GOV | certification B Corp (oui seulement), domaine du site vérifié | annuaire B Lab | entité certifiée |
| ONU — HCDH | GEO | présence dans la base des entreprises liées aux colonies (controverse), nom exact | Conseil des droits de l'homme (A/HRC/63/20) | entité listée |

**Présence dans les paradis fiscaux** (top 10 de l'indice du Tax Justice Network, édition du
2 décembre 2025) : pour un groupe américain, lignes de l'annexe 21 de son rapport 10-K ; pour un
groupe européen, lignes des tableaux des sociétés consolidées de son rapport annuel (ESEF ou paquet
AMF). Une ligne compte si c'est une société détenue à 50 % au moins, immatriculée (premier pays de la
ligne) dans l'une des dix juridictions ; succursales, mises en équivalence, coentreprises, lignes
d'emprunts, doublons et pays du siège sont exclus. Le vérificateur refait le décompte depuis le
rapport original. Un rapport peut ne lister que ses principales sociétés : la valeur est un minimum,
et un zéro issu d'un tableau illisible n'est jamais publié (17/10/2026).

Les quantitatifs (taux effectif, présence en paradis fiscaux) sont chargés en
**valeur brute** : c'est le moteur qui calcule le percentile intra-secteur et
applique la direction (\`higher_better\` / \`lower_better\`, ou \`closer_to_zero\` quand
l'objectif est zéro quel que soit le signe : l'écart de salaire femmes-hommes,
dont l'égalité est le meilleur rang, qu'il soit en faveur des hommes ou des
femmes). Normaliser à la main
fausserait la comparaison sectorielle.

Le **taux effectif d'impôt** est celui des comptes consolidés : charge d'impôt
rapportée au résultat avant impôt, tel que le groupe le publie, ou recalculé à
partir de ces deux lignes (le calcul est écrit sur la fiche). Il est retenu tel
quel, même déformé, et la cause publiée est citée (Kering, 78,2 % en 2025 :
impôts différés non reconnus sur les pertes d'Alexander McQueen). Un exercice
**en perte avant impôt** n'a pas de taux interprétable : aucune preuve n'est
créée (Renault, Stellantis et Kraft Heinz en 2025), et la donnée reste manquante.

**Au moins 5 pairs** *(depuis v0.6.0)*. Un rang n'est noté que face à au moins
cinq entreprises du même secteur ayant publié la même donnée
(\`min_peers_for_rank\`). En dessous, il ne dit rien — dans l'énergie, TotalEnergies,
Engie et Shell seuls se partageaient les rangs 83, 50 et 17 en fiscalité : la
valeur est affichée et compte dans la fiabilité, pas dans la note. Les rangs
reviennent à mesure que la collecte élargit le secteur.

---

## 8. Statut

Document vivant (v\`0.8.4\`, octobre 2026). Toute modification des paramètres de
calcul (tables de config) doit être datée et justifiée ici.

**Journal :**
- **0.8.4 (15/10/2026)** — Présentation, sans effet sur les faits. Logos : icône officielle du
  site de la marque, sinon logo de Wikimedia Commons retrouvé sur Wikidata par identifiant
  officiel (LEI, SIREN) ou par le groupe propriétaire, sinon icône du site officiel ; un logo
  sert à reconnaître l'entreprise et ne prouve rien (outil \`logos_wikidata.py\`). Une marque ne
  reprend jamais le logo de son groupe, et une icône partagée par des marques de noms différents
  est écartée. Produits d'une marque alimentaire : les plus scannés en France d'après Open Food
  Facts (base collaborative sous licence ouverte), présentés comme repères, pas comme preuves.
  Chaque indicateur d'un pilier s'affiche, même vide, avec la raison de son absence. « Rayon »
  devient « secteur ».
- **0.8.3 (15/10/2026)** — Seuils d'alerte : chaque indicateur qui s'y prête a un seuil
  d'alerte et, le plus souvent, un seuil de vigilance, appuyés sur une référence citée ou
  annoncés comme choix de l'Index (section 0, « Seuils d'alerte »). Bandeau des alertes en tête de
  fiche.
- **0.8.2 (15/10/2026)** — Collecte complète (aucun paramètre de calcul modifié). Rapports
  réglementés et volontaires lus groupe par groupe (lots 100, 103, 104 : environ 155 preuves) ;
  chaque lecture sans résultat est consignée au journal (« rapport lu, donnée absente », « publiée
  sous une autre forme »). Règles appliquées : l'intensité en eau retenue est celle de l'ESRS E3-4,
  fondée sur la **consommation** d'eau rapportée au chiffre d'affaires (une intensité par litre
  produit ou fondée sur les seuls prélèvements est consignée, non reprise) ; une baisse d'émissions
  n'est retenue que sur deux ans au moins ; les conversions d'unités (kt/M€, t/k€, kg/€) et de
  devises (taux annuels moyens de la BCE) sont écrites en toutes lettres et recontrôlées ; une part
  d'écart salarial publiée par pays est signalée comme telle. Sites de marques (lot 102) : le
  propriétaire est attesté par son SIREN **ou** sa raison sociale dans les mentions légales (173
  sites, liste publiée) ; 66 faits du pilier animal. Sanctions : jeu de données officiel des
  décisions de l'Autorité de la concurrence (lot 101) et sanctions publiées par la DGCCRF (lot 105 :
  127 pages lues sur le plan du site officiel, 5 sociétés de la base retrouvées par leur SIRET, toutes
  pour retards de paiement aux fournisseurs ; publications temporaires, donc aucune ligne « cherché sans
  résultat »). Les outils s'identifient comme vérificateur de l'Index (identité « DIAMS verifier ») : certains sites refusent l'en-tête
  générique d'un navigateur mais acceptent cette identité déclarée. Sources écartées : Légifrance et la
  CNIL (refus au vérificateur, panne), jeu ouvert de la CNIL (totaux sans nom), sites refusant le
  vérificateur (Hasbro, Newell, Suntory, Unilever : 403), pages sans texte lisible (Mattel).
- **0.8.1 (15/10/2026)** — Décision de l'éditeur : trois niveaux, groupe, marque et produits, pour
  tout le site (section 0). Nouvel indicateur « Produits 100 % végétaux proposés »
  (\`ANI_OFFRE_VEGETALE\`, niveau produit) ; \`ANI_ANIMAL_FREE\` devient « Marque entièrement
  végétale ». Lots 98 et 99 : 152 sites officiels identifiés par le SIREN du propriétaire dans
  leurs mentions légales ; exploitation animale de 36 marques, produits 100 % végétaux chez 16,
  Yumgo et Holibelly entièrement végétales — toutes les citations vérifiées mot pour mot.
- **0.8.0 (15/10/2026)** — Décision de l'éditeur : fin de la note globale. La fiche devient
  une carte d'identité de faits sourcés (section 0) : cinq états par indicateur, solidité des
  sources par pilier, chronologie des sources, journal de relecture public, toutes les marques
  publiées. Le classement est retiré ; les « alternatives mieux notées » deviennent « autres
  marques du même rayon », par ordre alphabétique. Correctifs de données relevés en route :
  SIREN et LEI de Carrefour, Rémy Cointreau, Hermès et AXA (confirmés dans l'annuaire officiel et
  GLEIF ; Hermès reçoit son index Égapro 2025, 99/100) ; l'outil de rattachement des obligations
  ne lisait que les 1 000 premières entités : les 297 obligations Égapro sont désormais écrites.
- **15/10/2026 (relecture complète, PLAN_REFONTE.md)** — Sans changement de calcul, hors
  rattachement d'obligations. Chaque preuve a été relue contre sa source, et chaque passage est
  consigné dans un journal public (\`indicator_reviews\`) :
  - preuves des connecteurs relues sur leurs sources téléchargées à nouveau : Égapro 268/268,
    CDP 242/242, KSE 122/122, registre de l'UE (2 montants mis à jour, Kellanova sorti), SBTi
    (export du 08/10 : objectifs validés pour Ecotone et Pilot, engagement retiré pour Alsace
    Lait), classements (FTI, KnowTheChain, Fashion Checker, BBFAW, Finansol, sans fourrure,
    B Corp) tous confirmés, codes APE 81/81 confirmés par l'annuaire officiel ;
  - citations curées relues mot pour mot : 651 confirmées, aucun écart ;
  - obligations des 20 groupes soumis à la CSRD lues dans leurs rapports : absences déclarées
    par l'entreprise (Hermès, Carrefour, Société Générale), constatées (BPCE, BNP Paribas), ou
    publication sous une autre forme (sous-périmètre, par zone ou pays, écart ajusté) ;
  - obligation Égapro rattachée à 296 sociétés (fichier officiel des déclarations croisé avec la
    tranche d'effectif de l'annuaire) au lieu de 33 ; 35 sociétés tenues de publier n'ont pas
    d'index 2025 ; les index d'UES sont attribués aux sociétés membres ;
  - absences recherchées dans les listes complètes (CDP, SBTi, KSE, registre de l'UE, HATVP) :
    4 787 « cherché, non trouvé » datés ;
  - appartenances marque → groupe relues : 2 129 confirmées mot pour mot ; Kellanova (Kellogg's,
    Pringles…) rattachée à Mars (acquisition conclue le 11/12/2025, 8-K et communiqué de Mars) ;
  - exploitation animale : 38 marques de plus documentées par leur site officiel (lot 97), 35
    par le code APE ; vocabulaire du vérificateur complété par « produits carnés » et « produits
    de la mer ».
- **0.7.5 (14/10/2026)** — Décision de l'éditeur (option A) : une marque reprend
  l'index Égapro de **son propriétaire direct** (Règle 8). Avant, l'index restait
  attaché à la société déclarante et aucune marque n'en héritait. Effet mesuré par
  simulation avant application, marque par marque : 580 marques concernées,
  **+83 marques publiables, aucune perdue, aucune note en baisse** (Mousquetaires 24,
  Pierre Fabre 13, Avril 10, Sodiaal 7, Orangina Schweppes France 6, Ecotone 6,
  Maison Pommery 6, Interparfums 3, Fleury Michon 2, Alsace Lait 2, Boiron,
  Panzani, Maîtres Laitiers du Cotentin, Paul Hartmann 1 chacun). L'option B
  (index de la racine du groupe) a été écartée : l'index d'une holding couvre
  souvent ses seuls salariés. Contrôle fait : les index transmis sont ceux des
  sociétés qui exploitent les marques (ITM Entreprises pour Les Mousquetaires, et
  non la holding). Migration \`20261014950000_egapro_proprietaire_direct\`.
- **14/10/2026 (recherche par pilier pour les marques alimentaires)** — Sans changement
  de calcul. Décision de l'éditeur : une fromagerie, ou une biscuiterie qui utilise du
  beurre, des œufs ou du lait, exploite des animaux ; l'exploitation se documente donc
  (Règle ANI, « Documenter l'exploitation »).
  - Nouveau connecteur \`import_ani_ape\` : code APE lu dans l'avis de situation Sirene de
    l'Insee (source réglementaire). Le quota de lecture de l'Insee est respecté : arrêt au
    premier refus, reprise à l'exécution suivante grâce au cache.
  - 92 marques documentées par la présentation de leurs produits sur leur site officiel,
    passages relus puis vérifiés mot pour mot (Babybel, Kinder, Lustucru, St Michel,
    Cochonou, Rougié, fromages de Savencia…).
  - Lot 96 : 7 marques de Sodiaal (Candia, Viva, GrandLait, Candy'Up, Yoplait, Perle de
    Lait, Entremont), seules marques du groupe encore bloquées par l'absence de preuve
    animale ; citations extraites telles quelles de candia.fr, yoplait.fr et
    entremont.com, vérifiées mot pour mot. Les 7 deviennent publiables (1 058 au total).
    Le code APE ajoute aussi 17 preuves (fromageries, volailles, pêche).
  - Restent sans source lisible : le rattachement d'ALDI France au groupe ALDI Nord (sites
    construits en JavaScript, aucune relation de consolidation dans GLEIF), Panzani (seule
    mention trouvée : un nom de produit).
  - Mots-clés du vérificateur élargis à l'alimentation (fromage, beurre, charcuterie,
    poisson, foie gras, élevage, pêche…), « beurre de cacahuète / karité / cacao » exclu.
  - Autres piliers relancés sur les nouvelles sociétés : registre des représentants
    d'intérêts (Biocoop, Eat4Good France), certification B Corp (Isigny Sainte-Mère).
- **14/10/2026 (marques alimentaires vendues en France, lots 82 à 95)** — Sans changement
  de calcul. Environ 470 marques ajoutées : la base compte 2 145 marques, dont 968
  publiables. Les nouvelles marques appartiennent surtout à de petites sociétés sans
  données publiques suffisantes : elles sont référencées et rattachées à leur
  propriétaire, mais pas encore notées.
  - **Liste Nutri-Score de Santé publique France** (déclarations des entreprises,
    janvier 2026) :
    - filtre de taille levé (lot 82) ;
    - sociétés étrangères identifiées par leur LEI dans le registre GLEIF, formes
      juridiques ignorées (lots 83 et 87) ;
    - noms proches (lot 84), enseignes (lot 86), déclarants ciblés un à un (lot 88) ;
    - correspondances uniques dans l'annuaire officiel des entreprises, écartées jusqu'ici
      par le filtre d'activité puis relues à la main (lot 91) ;
    - recherche approchée, retenue seulement si le candidat est unique, l'activité
      alimentaire et la forme juridique concordante (lot 92).
  - **Mentions légales des sites officiels de marques** (lots 85, 89, 90, 93 à 95) :
    - l'éditeur est identifié par le SIREN cité sur la page, vérifié dans l'annuaire
      officiel ;
    - la citation retenue nomme la marque et la société.
  - **Pages officielles de groupes** :
    - page « Nos marques » d'Intersnack France ;
    - pages « Nos entreprises » de Sucralliance ;
    - communiqué réglementé de LDC du 28/05/2025 : acquisition de 100 % du groupe Pierre
      Martinet.
  - **Liens de groupe lus dans GLEIF** (relations de consolidation au statut « ACTIVE ») :
    - Labeyrie Fine Foods France → Labeyrie Fine Foods ;
    - Société des Caves (Lanquetot) → Lactalis, fiche LEI non renouvelée depuis 2020 ;
    - Loeuf (Matines) → LDC, par la mère ultime ;
    - Jacquart → Alliance Champagne.
  - **Doublons supprimés** : Paysan Breton, Malo, St Michel, Valfleuri, Sains et Saufs,
    Pastilles Vichy. Règle adoptée : relire la liste de la base juste avant chaque lot et
    comparer les noms sous un même propriétaire.

  **Écartés** :
  - l'hébergeur ou l'agence web relevé à la place de l'éditeur ;
  - les homonymes : Janneau (menuiseries), Popote (Compass Group), Krill (réseau de vente
    aux professionnels), « DUC SAS » (restaurant, sans lien avec les volailles Duc) ;
  - les domaines en vente ou détournés (gringoire.com, kritsen.fr) ;
  - les pages construites en JavaScript, illisibles par le vérificateur (Port Salut,
    Le Gall) ;
  - les sites fermés par un contrôle d'âge (Spirit France) ;
  - les éditeurs personnes physiques (Neisson) ;
  - les pages qui ne nomment pas la marque près de la société (La Baleine, Jardin Bio,
    La Mauny, Trois Rivières) ;
  - les lignes Nutri-Score génériques (« sans marque », « marque générique »), les slogans,
    la restauration, les associations et collectivités ;
  - Bordeau Chesnel, dont la cession par Savencia n'est qu'en négociation.

  **Limite assumée** : une liste « de toutes les marques alimentaires vendues en France »
  n'existe dans aucune source officielle. L'Index n'ajoute une marque que si son
  propriétaire est prouvé.
- **14/10/2026 (notation des groupes très présents en rayon)** — Sans changement de
  calcul. Rappel de la Règle 8 : une marque ne reprend de son groupe racine que les
  indicateurs « de groupe » ; un groupe publiable n'a donc pas toujours des marques
  publiables (l'index Egapro, par exemple, n'est pas transmis). Le suivi se fait
  désormais au niveau des marques : 861 marques publiables sur 1 641 au début de la
  session, plus de 940 à la fin.
  - **Gouvernance, impôt, plan de vigilance**, tirés de documents réglementaires ou
    publiés par l'entreprise :
    - Mousquetaires : évaluation extra-financière EthiFinance publiée par le groupe ;
    - Ebro Foods : rapport de gouvernance sur le modèle officiel de l'autorité boursière
      espagnole ;
    - Casino : document d'enregistrement 2024 ;
    - Bel : document d'enregistrement 2024 d'Unibel, sa holding ;
    - Newell Brands : circulaire déposée à la SEC ;
    - LDC : taux d'impôt, rapport ESEF ;
    - Auchan : plan de vigilance 2025 et rapport financier 2024 d'ELO.
  - **Registres** : HATVP (Ecotone, Euralis, Panzani, DIM, Wattwiller, Herta, Saint
    Louis Sucre) ; registre de transparence de l'UE (Groupement Les Mousquetaires,
    Suntory Global Spirits, Suntory Beverage & Food Europe) ; SBTi (Auchan Retail).
  - **Vérificateur mot pour mot** (règles déterministes, chacune testée) :
    - « une » vaut 1 ;
    - « femme », « administratrice » et « Sexe Féminin » désignent la mixité ;
    - un conseil déclaré sans aucun administrateur indépendant vaut 0 % ;
    - une exception nommée à part (« is not considered an independent ») compte seulement
      si la citation affirme aussi que tous les autres administrateurs sont indépendants ;
    - un montant écrit avec des espaces de milliers est reconnu même quand une autre
      colonne le suit ;
    - une page PDF illisible (image trop volumineuse) est ignorée au lieu de faire
      échouer la lecture.
  - **Marques** (lots 75 à 77, rapports déposés à la SEC) :
    - Mattel : Pictionary, Blokus, Thomas & Friends… ;
    - Newell : Contigo, Sistema, Crockpot, Elmer's ;
    - Irwin, Bostitch, Stérimar ;
    - AB InBev : bières de sa liste officielle pour la France.
  - **Sociétés françaises cotées** (documents déposés à l'AMF ou rapports financiers
    annuels) :
    - Lanson-BCC : mixité, indépendance et impôt du groupe ; ses maisons Philipponnat,
      De Venoge, Besserat de Bellefon, Boizel, Chanoine, Tsarine et Alexandre Bonnet ;
      Heidsieck & Co Monopole, cédée par Maison Pommery le 05/01/2026 ;
    - Maison Pommery & Associés : mixité, indépendance déclarée, taux d'impôt publié
      (négatif, cession exonérée citée) ;
    - AdVini, nouveau groupe : Laroche, L'Oratoire des Papes, Gassier, Ogier ;
    - Fleury Michon : gouvernance ; marque Paso.

  À la fin de la session : 964 marques publiables sur 1 671.

  **En attente d'un humain** : l'inscription HATVP de la holding « Les Mousquetaires »
  (SIREN 789 169 323, distinct de celui d'ITM Entreprises, racine en base).

  **Écartés** :
  - l'homonyme « Alma » (éditeur de logiciels, sans lien avec les eaux) ;
  - les marques de la page française de Kenvue, qui sont des marques américaines ;
  - la mixité du conseil d'Agrial (« une agricultrice » sur 30 : formulation que le
    contrôle déterministe ne peut pas lire) ;
  - le rattachement de Flora Food France et de Suntory Beverage & Food à leur groupe,
    faute de preuve publique.
- **13/10/2026 (couverture des marques, rayons non alimentaires et vins)** — Sans
  changement de calcul. Lots 58 à 69 :
  - **Vins** : maisons Boisset, La Vieille Ferme (famille Perrin), J.P. Chenet (Grands
    Chais de France).
  - **Fromages** : dix fromages de Savencia (Boursault, Le Mottin, Pié d'Angloys…),
    tirés des mentions de marques déposées de son portail.
  - **Petites et moyennes entreprises de la liste du Nutri-Score** : séries
    complémentaires (homonymes départagés par l'activité agroalimentaire et
    l'effectif, noms proches relus un à un, fabricants de 6 à 9 salariés).
  - **Jouets, papeterie, électroménager, électronique** : VTech, Smoby, Playmobil,
    Pilot, Clairefontaine, Bosch électroménager, Beko, Hisense, TCL, Kärcher.
  - **Groupes dont la marque porte le nom** : HP, Canon, LG, Epson, Lenovo,
    Nintendo, Ubisoft, LEGO, Ravensburger, Maped, Michelin… La fiche du groupe sert
    alors de fiche de marque.

  **Écartées** :
  - marques sous licence : Whirlpool, exploitée en Europe par Beko Europe ; Franck
    Provost Expert, exploitée par L'Oréal ;
  - domaines repris par un revendeur de noms de domaine, dont l'éditeur n'a aucun
    lien avec la marque (raid.fr, vigor.fr, monsavon.com) ;
  - homonymes : signal.fr, une entreprise de signalétique ; seni.fr, une entreprise de
    nettoyage ;
  - Tupperware : propriété de la marque incertaine depuis la faillite du groupe.

  **Technique** : une marque sans donnée propre étant notée uniquement à partir de son
  groupe racine, sa note n'est plus recalculée pour chaque marque, mais une seule fois
  par groupe racine, secteur et pays. Le résultat est identique (vérifié), et le
  calcul de l'accueil est divisé par deux.
- **13/10/2026 (couverture des marques, liste officielle du Nutri-Score)** — Sans
  changement de calcul. Nouvelle source d'appartenance : la liste publiée par Santé
  publique France, « Entreprises et marques utilisant le Nutri-Score en France »
  (version de janvier 2026, 1 538 entreprises). Chaque entreprise y déclare elle-même
  les marques sous lesquelles elle vend ses produits en France ; la ligne
  « entreprise → marques » est citée mot pour mot et revérifiée par l'importeur dans
  le PDF officiel. Cette source sert surtout pour les marques de distributeur, que les
  enseignes ne listent nulle part ailleurs : Lidl (Milbona, Crownfield, Alesto,
  Freshona…), Aldi (Les Doris, Golden Bridge, Mr Frites…), Intermarché (Paquito,
  Saint Eloi, Top Budget…), Carrefour (Carrefour Classic, Extra, Original…), Système U
  (U, U Saveurs, U Bio…), Leclerc (Nos régions ont du talent). Elle sert aussi pour
  des fabricants : Nestlé (Buitoni, Contrex, Thomy, Galak), Danone (Gervais,
  Taillefine), Nutrition & Santé (Gerblé, Céréal), Tipiak, Francine, Père Dodu, Prince
  de Bretagne, Fruit d'Or et Planta Fin (Upfield, aujourd'hui Flora Food Group). Deux
  précautions : (1) une déclaration désigne l'entreprise qui vend sous la marque, pas
  toujours son propriétaire ; les licences et coentreprises connues restent donc
  écartées (céréales de Cereal Partners, Paysan Breton surgelé chez Gelagri, Lustucru
  partagée entre plusieurs sociétés, Panzani chez William Saurin), de même que les
  importateurs et distributeurs de marques étrangères (Weetabix chez Pietercil) ;
  (2) une déclaration faite par une filiale n'est rattachée au groupe que si
  l'appartenance de la filiale est déjà prouvée par ailleurs (Materne et Mont Blanc
  chez Bel, Candia chez Sodiaal, Findus chez Nomad Foods) ; sinon la filiale devient
  elle-même le propriétaire affiché. **Homonyme signalé** : « Bear Fruits » (soins
  capillaires de P&G) n'a rien à voir avec « Bear » (en-cas aux fruits de Lotus
  Bakeries). **Série des PME (lot 59, 148 marques, 126 sociétés)** : une société de la
  liste n'est retenue que si son nom correspond exactement à une seule société active
  de l'annuaire officiel des entreprises, qui emploie au moins 10 salariés ; sont
  écartés les entrepreneurs individuels, les organismes publics et associatifs, les
  importateurs, la restauration et les magasins, les noms génériques (« sans marque »,
  « Les Surgelés ») et les descriptions de produit ; chaque ligne a été relue (Mr
  Freeze, probablement sous licence, et une quinzaine d'autres lignes écartées).
- **13/10/2026 (couverture des marques, pages de marques des groupes)** — Sans
  changement de calcul. Environ 145 marques de plus (lots 34 à 42), surtout à partir
  des fiches de marque publiées par les groupes eux-mêmes : Henkel (Le Chat, Mir,
  X-Tra, Somat, Pril, Vernel, Fa, Schauma…), P&G France (Dash, Lenor, Mr Propre…),
  Unilever France (Persil, Omo, Skip, Cajoline, Sun), Garnier (Ambre Solaire, Ultra
  Doux…), Pernod Ricard, Diageo, Purina, Kinder, Yoplait, Lindt ; des rapports
  annuels (AB InBev, Heineken, Casino, Maison Pommery & Associés, 10-K de Spectrum,
  Newell, Energizer, Edgewell, Church & Dwight) ; et des mentions légales (Intersnack
  France, Thiriet, Lanson, Nicolas Feuillatte, Mouton Cadet…). Quand l'éditeur d'un
  site est une filiale, le lien avec le groupe est lu dans le registre GLEIF (société
  mère directe ou ultime) : Bardinet → COFEPP, Sofibel → Church & Dwight, L.I.D. →
  Lanson-BCC, Société des Caves → Groupe Lactalis. **Corrections** : Suchard est
  exploitée en France par Carambar & Co (Mondelez la détient hors de France) ; les
  Laboratoires Juva Santé appartiennent au Groupe Urgo. **Écartées** : Persil chez
  Henkel (en France, la marque est à Unilever), Iams et Eukanuba chez Mars (en Europe,
  elles sont à Spectrum Brands), les coentreprises (Clearblue, Havana Club, Mamie
  Nova), les marques cédées (Heidsieck & Co Monopole) et Terry's (distribuée par
  Carambar & Co, propriété incertaine).
- **13/10/2026 (couverture des marques, mentions de marque déposée)** — Sans
  changement de calcul. Nouvelle source d'appartenance, en plus des mentions
  légales : la mention de marque déposée ou de droits d'auteur du site officiel
  de la marque (« Ebly est une marque déposée de Mars, Inc. », « trademarks of
  Bacardi & Company Limited », « © Groupe Melitta »), citée mot pour mot et
  revérifiée par l'importeur. 23 propriétaires et 42 marques de plus (Albal,
  Handy Bag, Brita, HiPP, Rainett, Scholl, Mustela, Giovanni Rana, Capri-Sun,
  Quézac, Mousline, Lipton, Éléphant, Bacardí, Eristoff, Rio Mare, WC Net…).
  Écartées faute de propriétaire certain : les mentions sans nom de société
  (« Martini… are trademarks »), les sites étrangers d'une marque dont le
  propriétaire diffère en France (Biafine, Smarties, Bugles), les marques sous
  licence (La Laitière), Varta (procédure d'insolvabilité et vente en cours).
  **Correction** : la cession d'Essential Home (Air Wick, Calgon, Cillit Bang,
  Woolite) par Reckitt à Advent International est achevée le 31/12/2025 ; Reckitt
  n'en garde que 30 %. Air Wick était rattachée à Reckitt par une citation tirée
  de cette même section du rapport : elle est désormais rattachée à Essential Home.
- **13/10/2026 (couverture des marques, troisième série)** — Sans changement de
  calcul. 38 groupes et 112 marques de plus : 5 groupes cotés aux États-Unis
  (Findus de Nomad Foods, jeans Wrangler et Lee, WD-40, Batiste, Russell Hobbs),
  les marques françaises de Mars et de Mondelez (Bounty, Twix, Mikado, Pépito,
  Petit Écolier…) et 33 fabricants français identifiés par les mentions légales
  de leurs marques (Carambar & Co, Cofigeo, Panzani, Herta, St Michel, Haribo,
  Campofrío, d'aucy, Hénaff, Carte Noire, Malongo, Charal, Delpeyrat, Vileda,
  Saint Louis, Gavottes…). Les marques cédées sont écartées d'après les rapports
  des groupes (Timotei, Clan Campbell, Cinzano, participation dans Herta), de
  même que les homonymes (le site jacquet.fr appartient à une entreprise du
  bâtiment). Technique : au-delà de 1 000 entités, le site et le pipeline lisent
  désormais la base page par page (l'API plafonne chaque réponse à 1 000 lignes).
- **13/10/2026 (couverture des marques, suite)** — Sans changement de calcul.
  70 groupes et 232 marques de plus, chacune rattachée par une preuve citée
  vérifiée mot pour mot : 17 groupes cotés (jouets Mattel et Hasbro, piles
  Energizer, rasoirs Wilkinson, Post-it et Scotch-Brite de 3M, Sharpie et Spontex
  de Newell, Black+Decker, Monster, Jack Daniel's, Weetabix, champagnes
  Laurent-Perrier, William Peel et San José de Marie Brizard, Philips, De'Longhi,
  Twinings, Ovomaltine et Primark d'ABF, Lindt, Electrolux), 8 groupes non cotés
  suivis par le CDP ou la SBTi (Thai Union pour Petit Navire, Perfetti Van Melle,
  Laïta, Pierre Fabre, Sofidel, Eckes-Granini, McCain, Labeyrie), et 45 sociétés
  françaises identifiées par les mentions légales des sites de leurs marques
  (Banania, Brossard, Cémoi, Sodebo, Daunat, Lorina, St-Yorre, Label 5, Taittinger,
  Connétable, Starwax…), SIREN vérifié dans l'annuaire officiel des entreprises.
  Deux secteurs nouveaux, « Jouets & Jeux » et « Équipement de la maison », sans
  exploitation animale présumée. Les marques sous licence (Scrabble hors
  Amérique du Nord, Braun en petit électroménager, Varta hors Amérique latine et
  Asie) ne sont pas rattachées au licencié ; les marques en copropriété (Mamie
  Nova, Régilait) ne le sont à aucun des copropriétaires. Vérification
  automatique : intensité carbone publiée en kilogrammes par euro, colonnes de
  ratios de rémunération (« 137:1 126:1 ») non fusionnées en milliers.
- **13/10/2026 (couverture des marques)** — Sans changement de calcul. Chaque
  rattachement marque → groupe porte désormais sa preuve citée (« Appartenance
  prouvée », Règle 8) ; les 131 marques rattachées avant cette règle l'ont reçue.
  Ajout de 32 groupes présents en grande surface (dont Carlsberg, Diageo, Reckitt,
  Rémy Cointreau, Campari, Essity, Savencia, LDC, SEB, BIC, Arla, Puig, Coty,
  E.Leclerc, Système U, Les Mousquetaires, Auchan, Casino, Sodiaal, Avril, Tereos)
  et de 349 marques, chacune vérifiée mot pour mot. Les groupes non cotés
  publient peu : leur note reste souvent « en attente » faute de preuves, et c'est
  affiché comme tel. Vérification automatique étendue : sommes et différences dans
  un calcul de part (conseil hors représentants des salariés), intensité carbone
  « par million d'euros de chiffre d'affaires » en anglais.
- **0.7.4 (13/10/2026)** — Décisions de l'éditeur. Sanctions : chaque décision
  officielle de moins de 5 ans retire 15, 8 ou 3 points à la note globale selon
  l'amende (cumul plafonné à 25), en plus de l'indicateur de gouvernance. Les
  versions 0.7.2 (sanctions limitées aux décisions officielles) et 0.7.3
  (plastique vierge, fiabilité jamais baissée par une donnée complémentaire,
  règle du « publié ») sont validées, de même que le refus des chiffres publiés
  sur un seul sous-périmètre, la présomption d'exploitation animale tant qu'aucune
  preuve contraire n'existe (Pernod Ricard, L'Oréal) et le refus de compter une
  baisse d'émissions due aux cessions (Shell, TotalEnergies). Composition des
  conseils : la part d'indépendants reprend ce que l'entreprise déclare, citation
  à l'appui (président déclaré indépendant compris) ; l'effet sur la note globale
  reste inférieur à un point.
- **0.7.3 (13/10/2026)** — Plastique : l'évolution réelle du tonnage de
  plastique vierge remplace la signature d'un engagement (premières données :
  8 groupes de l'alimentation et de l'hygiène, de L'Oréal −37 % à Coca-Cola).
  Fiabilité : un indicateur complémentaire documenté ne peut plus la faire
  baisser. Gouvernance : indépendance et mixité des conseils de Meta et Mondelez
  calculées depuis l'effectif cité, puis Apple, Amazon, Kenvue, Starbucks
  (indépendance) et McDonald's, Restaurant Brands, Kraft Heinz (mixité). Preuves
  héritées sans citation retirées, motif écrit (recensements non datés, articles
  de presse, pages d'accueil) ; il en reste 2 sur 51 (site de Starbucks fermé
  aux programmes, plan de vigilance de Decathlon introuvable). Rapport de l'ONU
  A/HRC/59/23 : citations exactes pour Google, Amazon, Microsoft, BNP Paribas
  (affichées hors note). Liste des fournisseurs : non comptée dans la mode,
  où l'indice de transparence l'évalue déjà. Données obligatoires comptées 0 :
  24 cas revus un par un, 11 corrigés (Crédit Mutuel Alliance Fédérale, Arkéa,
  La Banque Postale, LVMH), 13 confirmés avec leur motif ; exemption pour une
  donnée déclarée non matérielle. Plan de vigilance : obligation rattachée à six
  banques et plans relevés (BNP Paribas, Société Générale, Crédit Agricole, BPCE,
  Crédit Mutuel, Arkéa) ; La Banque Postale relève du plan de La Poste.
  Suite du 13/10/2026 (lots 45 à 52, sans changement de barème) : taux effectif
  d'impôt de 11 groupes (taux publié tel quel, cause citée ; exercice en perte
  sans taux) ; composition de 15 conseils (président indépendant à sa nomination
  compté parmi les indépendants quand le rapport le dit) ; plans de vigilance
  d'AXA, Bonduelle, Lactalis et de La Banque Postale (plan du groupe La Poste) ;
  exploitation animale documentée pour Lactalis, Bel, Ferrero, Fast Retailing,
  Mars et The Magnum Ice Cream Company ; propriétaires à jour (Kellogg's chez
  Mars, Magnum et Ben & Jerry's chez The Magnum Ice Cream Company). Une donnée
  déclarée non matérielle s'affiche avec son motif, y compris quand elle est
  seule dans son pilier (pilier « pour information »). Un rapport volontaire
  présenté comme légal a été reclassé (Samsung, indépendance du conseil, désormais
  tirée de son rapport d'activité légal).
- **0.7.2 (13/10/2026)** — Sanctions : l'indicateur ne retient plus que des
  décisions officielles (Commission européenne, autorités de protection des
  données), notées par la gravité de l'amende ; les anciennes lignes, sourcées
  par la presse et dont un montant était faux, sont retirées. Premières
  décisions : 32 (Google 2,95 Md€, Apple 1,8 Md€, Meta 1,2 Md€, Amazon
  1,128 Md€ en Italie, Google 403 M€ et LinkedIn 310 M€ en Irlande, Mondelez
  337,5 M€, Google 325 M€ et Shein 150 M€ par la CNIL, Gucci 119,7 M€,
  TotalEnergies 115,8 M€ pour l'entente sur les carburants en Corse, Volkswagen
  127,7 M€, entente des constructeurs sur le recyclage des véhicules…).
  Plusieurs controverses : la fiche affiche la plus grave, celle qui fixe la
  pénalité.
- **0.7.1 (12/10/2026)** — Décisions de l'éditeur : un objectif climat validé
  par la SBTi est un engagement (Règle 3), plus un résultat ; nouvel indicateur
  de résultat, l'évolution réelle des émissions totales (scopes 1, 2 et 3),
  notée sur la trajectoire 1,5 °C (−4,2 % par an). Premières données : 21
  groupes, dont Shein (+23 % en un an), Microsoft (+10 % par an depuis 2020),
  Google (+9 % par an depuis 2019), Amazon (+8 % par an), Volkswagen (+7 %),
  Hermès (+0,8 % par an depuis 2018) ; Apple, Danone, Kering, H&M, LVMH,
  Renault, Stellantis, Engie, Pernod Ricard, Mondelez en baisse de plus de
  4,2 % par an. Une baisse sur une seule année ne compte pas. Noms des sources
  affichés en français. Rapports volontaires des entreprises : source de
  niveau 3, validation déléguée sous condition de vérification mot pour mot.
- **0.7.0 (11/10/2026)** — Décisions de l'éditeur. Exploitation animale :
  toute exploitation, même marginale, met le pilier animal à 0 (le barème
  « marginal 0,55 / au cœur de l'activité 0,40 » disparaît) ; le niveau inconnu
  reste présumé, dans tous les secteurs à enjeu animal. Mode et luxe : chaîne
  d'approvisionnement et environnement comptent double. Écart de rémunération
  de H&M (pondéré par poste) confirmé comme non publié. Ratio de rémunération
  d'ENGIE, calculé sur la moyenne faute de médiane calculable, accepté tel que
  publié ; obligation CSRD rattachée à ENGIE. Premier indicateur d'impact de la
  mode : salaire vital réellement versé chez les fournisseurs, noté par le
  collectif Clean Clothes Campaign (édition 2026, 110 marques ; 106 notées E, «
  aucun salaire vital versé ni revendiqué », dont H&M, Inditex, Shein, Nike,
  Adidas, Fast Retailing, Gucci, Hermès, Louis Vuitton). Le classement de l'ONG
  Remake, envisagé, n'est plus publié (l'organisation a cessé son activité).
- **0.6.1 (11/10/2026)** — Règle ANI rétablie : dans la mode et le luxe,
  l'exploitation animale est supposée tant qu'elle n'est pas exclue (plafond
  0,40), y compris pour une entité sur laquelle rien d'autre n'est connu ; un
  label ne peut plus faire baisser une note (H&M Group était noté A et la marque
  H&M B, parce que seule la marque, labellisée « sans fourrure », portait le
  plafond). L'indicateur d'exploitation animale et le label « sans fourrure »
  concernent aussi les groupes de luxe ; les niveaux documentés d'Hermès, Kering
  et LVMH (cuirs, peaux exotiques, élevage de crocodiliens) sont alignés sur le
  barème publié (« extensive » = 0,40 ; ils avaient été saisis à 0).
  Obligation européenne de rapport de durabilité (CSRD, première vague)
  rattachée à cinq groupes de plus, sur la foi de leur propre rapport (base
  légale citée) : Danone, AXA, Kering, Hermès, H&M. Hermès déclare ne pas
  publier encore l'écart de rémunération non ajusté ; H&M publie un écart
  pondéré par poste (99,7 %), pas l'écart non ajusté exigé : la donnée
  manquante compte 0 pour les deux (Règle 1). Pas de rattachement quand le
  groupe publie à titre volontaire (Heineken et Stellantis : directive non
  transposée aux Pays-Bas, disent-ils) ou au titre d'une autre loi (Inditex :
  loi espagnole 11/2018) : ce qu'ils publient compte, ce qu'ils omettent est
  ignoré. Une valeur publiée dans une autre devise est convertie au taux annuel
  moyen de la BCE, contrôlé à la vérification.
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
  à 79). Indicateurs de contexte (budget de lobbying) : affichés, jamais notés.
  **Audit de la saisie initiale** : les 248 lignes approuvées sans vérification
  (curation-v1) ont été remplacées par des connecteurs lisant la donnée publiée
  (KnowTheChain, BBFAW, KSE « Leave Russia », CDP 2025, Registre de transparence
  UE, SBTi, Fashion Transparency Index 2023, Fur Free Retailer) ou par des
  citations vérifiées mot pour mot (Break Free From Plastic, rapports annuels
  déposés à l'AMF, InfluenceMap) ; 52 lignes invérifiables sont remises en
  attente (hors des notes) jusqu'à vérification ; aucune n'est supprimée.
  Indicateurs nés d'une obligation légale (écart de rémunération, ratio de
  rémunération, intensité carbone, scope 3, taxonomie) au socle seulement pour
  les entreprises qui y sont soumises ; Global Commitment (plastique), liste
  fermée close en 2025 : complémentaire.
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
