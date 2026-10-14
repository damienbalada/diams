-- =============================================================================
-- Refonte R1 : date de l'événement et journal de relecture (PLAN_REFONTE.md)
-- -----------------------------------------------------------------------------
-- 1. evidence.event_date : date de l'événement que la preuve établit (décision,
--    publication du rapport, validation d'un objectif, sortie d'un marché), distincte
--    de observed_on (date de notre relevé). Sert à la chronologie des fiches.
-- 2. indicator_reviews : journal de la relecture complète, indicateur par indicateur.
--    Chaque passage y laisse une trace, que la preuve soit reconfirmée, corrigée,
--    trouvée, ou que son absence soit confirmée dans le rapport réglementé. Aucune
--    absence « obligatoire » n'est affichée sans une ligne « absence_confirmee ».
-- =============================================================================

alter table evidence add column if not exists event_date date;
comment on column evidence.event_date is
  'Date de l''événement établi par la preuve (décision, publication, validation), distincte de observed_on (date du relevé).';

create or replace view evidence_active as
 select id, entity_id, indicator_id, source_id, value_type, value_numeric, value_boolean, value_text,
        normalized_value, nature, observed_on, valid_until, confidence, reviewer, review_status,
        excerpt, source_url, created_at, updated_at, contested, event_date
   from evidence e
  where review_status = 'approved'::review_status and valid_until >= current_date;

create table if not exists indicator_reviews (
  id           uuid primary key default gen_random_uuid(),
  entity_id    uuid not null references entities(id) on delete cascade,
  indicator_id uuid not null references indicators(id) on delete cascade,
  evidence_id  uuid references evidence(id) on delete set null,
  outcome      text not null check (outcome in (
                 'confirmee',          -- citation et valeur retrouvées mot pour mot dans la source
                 'ecart',              -- citation ou valeur introuvable : preuve à corriger
                 'source_inaccessible',-- source muette au moment du passage : à refaire
                 'non_verifiable',     -- aucun vérificateur automatique : relecture humaine
                 'trouvee',            -- donnée absente jusque-là, trouvée et ajoutée
                 'absence_confirmee',  -- donnée obligatoire absente du rapport réglementé, lu
                 'non_trouvee')),      -- donnée non obligatoire, cherchée sans résultat
  detail       text,
  source_url   text,
  checked_on   date not null default current_date,
  reviewer     text not null,
  wave         smallint,
  created_at   timestamptz not null default now()
);
create index if not exists indicator_reviews_entity_idx on indicator_reviews (entity_id, indicator_id);
comment on table indicator_reviews is
  'Journal de la relecture complète (PLAN_REFONTE.md) : une ligne par passage sur un indicateur d''une entité.';
alter table indicator_reviews enable row level security;
drop policy if exists "public read" on indicator_reviews;
create policy "public read" on indicator_reviews for select using (true);
