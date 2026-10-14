-- Relecture complète, vague 6 : chaque preuve d'appartenance marque → groupe est relue mot pour
-- mot contre sa source ; le résultat du dernier passage est noté sur la preuve elle-même.
alter table entity_ownership_sources add column if not exists checked_on date;
alter table entity_ownership_sources add column if not exists check_result text
  check (check_result in ('confirmee', 'ecart', 'source_inaccessible', 'non_verifiable'));
alter table entity_ownership_sources add column if not exists check_detail text;
comment on column entity_ownership_sources.check_result is
  'Dernière relecture de la citation contre sa source (PLAN_REFONTE.md, vague 6).';
