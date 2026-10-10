# DIAMS

> **DIAMS** — **D**ocumented, **I**ndependent, **A**uditable, **M**ulti-criteria **S**coring.

Moteur de notation **éthique** des entreprises, multi-critères et **traçable** —
un « B Corp élargi » couvrant environnement, travail/rémunération, chaîne
d'approvisionnement, bien-être animal (humain et non-humain), prises de
position/géopolitique, fiscalité et gouvernance.

Ce qui nous différencie n'est pas la techno mais la **fiabilité** :
résolution d'entités d'abord, chaque point de score adossé à une **preuve
sourcée et datée**, décroissance à 5 ans, faits séparés des jugements, indice de
confiance affiché à part du score, et anti-greenwashing explicite.

👉 Méthodologie publique : [`METHODOLOGY.md`](./METHODOLOGY.md)

## Périmètre de départ

**Luxe / Mode, France + UE** — parce que les obligations légales FR/UE (devoir
de vigilance, CSRD) fournissent de la donnée structurée que les outils US n'ont
jamais eue.

## Architecture

```
diams/
├─ apps/web/            # Next.js (App Router) — fiche entreprise + sliders
├─ supabase/
│  ├─ migrations/       # schéma versionné (source de vérité)
│  ├─ seed/             # données de départ (dimensions, indicateurs, sources, entités)
│  └─ functions/        # Edge Functions (compute_score)
├─ pipeline/            # collecte Python (APIs + scraping) + curation humaine
├─ packages/shared/     # types partagés (générés depuis Supabase)
└─ docs/                # data model, registre des sources
```

## Stack

- **Front** : Next.js (App Router).
- **Données** : Supabase (Postgres).
- **Scoring** : Edge Functions Supabase (pas de logique de score en SQL brut).
- **Collecte** : pipeline Python avec révision humaine avant publication.

## Modèle de données (résumé)

`sectors`, `entities` (auto-référence parent + `ownership_pct` + LEI/SIREN +
secteur), `dimensions`, `indicators`, `sources` (avec `tier` de fiabilité),
`evidence` (cœur : entité + indicateur + source, valeur typée, `observed_on`,
`valid_until` = +5 ans, `nature`, `confidence`, reviewer, extrait + URL),
`value_profiles` + `profile_weights`. Config méthodo en base :
`source_tier_config`, `evidence_nature_config`, `scoring_params`. Vues :
`evidence_active`, `entity_coverage` (= indice de confiance).

## Base de données — reconstruire

Migrations dans `supabase/migrations/` (ordre chronologique), puis **un seul**
fichier de données, l'instantané de production :

```bash
supabase db push
psql "$DATABASE_URL" -f supabase/seed/99_snapshot.sql
```

> ⚠️ Projet de production existant : ses migrations ont été appliquées hors CLI,
> l'historique en base (`supabase_migrations.schema_migrations`) porte d'autres
> numéros de version que les fichiers. Le schéma, lui, est identique (vérifié le
> 10/10/2026). Avant tout `supabase db push` sur ce projet, aligner l'historique
> avec `supabase migration repair --status applied <version>` pour chaque fichier.

`99_snapshot.sql` est généré depuis la production (`node scripts/snapshot-db.mjs`)
et vérifié rejouable sur une base vierge. Les seeds 01 → 35 sont archivés dans
`supabase/seed/history/` : ils documentent la curation mais sont périmés.

### Règle : rien n'existe qu'en base

Toute écriture en production passe par un **connecteur** (`pipeline/`) ou une
**migration** versionnée. Après chaque session de curation ou d'import :

```bash
node scripts/snapshot-db.mjs --check   # échoue si la base a dérivé du repo
node scripts/snapshot-db.mjs           # régénère l'instantané, puis commit
```

Une preuve qui n'est pas dans le repo n'est ni rejouable ni auditable.

## Roadmap

- **Palier 1 — Fondations** *(en cours)* : migrations, résolution d'entités luxe,
  seed dimensions/indicateurs/sources.
- **Palier 2 — Scoring** : Edge Function `compute_score(entity, profile)`.
- **Palier 3 — Collecte** : connecteurs SIRENE/HATVP/GLEIF/Yale puis scraping
  (FTI, plans de vigilance) + file de révision humaine.
- **Palier 4 — Front** : fiche entreprise transparente + sliders de pondération.
