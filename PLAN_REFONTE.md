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

- [ ] R1 — données
- [ ] Vague 0 — outillage
- [ ] Vague 1
- [ ] Vague 2
- [ ] Vague 3
- [ ] Vague 4
- [ ] Vague 5
- [ ] Vague 6
- [ ] R2 — moteur
- [ ] R3 — fiches
- [ ] R4 — pages
- [ ] R5 — méthodologie
- [ ] R6 — contrôle et mise en ligne
