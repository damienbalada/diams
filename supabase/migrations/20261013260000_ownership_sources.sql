-- Appartenance d'une marque à son groupe : un FAIT sourcé et daté, comme une preuve.
-- Chaque rattachement cite mot pour mot le document officiel du propriétaire (rapport
-- annuel, document d'enregistrement universel, rapport 10-K, page « nos marques »)
-- où la marque figure. Aucune marque n'est rattachée sur la seule foi d'un nom.
create table if not exists entity_ownership_sources (
  id           uuid primary key default gen_random_uuid(),
  entity_id    uuid not null references entities(id) on delete cascade,
  owner_id     uuid not null references entities(id) on delete cascade,
  source_url   text not null,
  excerpt      text not null check (char_length(btrim(excerpt)) > 0),
  observed_on  date not null,
  reviewer     text not null,
  created_at   timestamptz not null default now(),
  unique (entity_id, owner_id, source_url)
);
comment on table entity_ownership_sources is
  'Preuve d''appartenance marque → groupe : citation mot pour mot du document officiel du propriétaire où la marque figure.';
alter table entity_ownership_sources enable row level security;
create policy "public read" on entity_ownership_sources for select using (true);
create index if not exists entity_ownership_sources_entity on entity_ownership_sources (entity_id);
