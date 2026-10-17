-- Table des produits (essai du 17/10/2026, décision de l'éditeur) : la liste d'ingrédients d'une fiche
-- produit, lue sur le site de la marque, confirme l'exploitation animale (un ingrédient animal suffit)
-- ou signale un produit végétal.
--   ingredient_animal                 : au moins un ingrédient d'origine animale certaine (hors traces) ;
--   aucun_ingredient_animal_declare   : rien d'animal dans la liste lue — ce n'est PAS une preuve de
--                                        produit végétal (carmin, gélatine, vitamine D3, arômes…) ;
--   vegetal_declare                   : la marque présente le produit comme 100 % végétal ou végan ;
--   vegetal_certifie                  : label végan d'un tiers (V-Label, Vegan Society…).
-- La liste d'ingrédients est recopiée telle qu'affichée, avec la date de lecture. Approbation : la
-- liste doit être retrouvée mot pour mot sur la page.
create table if not exists products (
  id uuid primary key default gen_random_uuid(),
  entity_id uuid not null references entities(id) on delete cascade,
  name text not null,
  source_url text not null,
  ingredients text,
  animal_ingredients text[] not null default '{}',
  doubtful_ingredients text[] not null default '{}',
  status text not null check (status in ('ingredient_animal', 'aucun_ingredient_animal_declare', 'vegetal_declare', 'vegetal_certifie')),
  vegetal_proof text,
  observed_on date not null,
  reviewer text,
  review_status text not null default 'pending' check (review_status in ('pending', 'approved', 'rejected')),
  created_at timestamptz not null default now(),
  unique (entity_id, source_url)
);
create index if not exists products_entity_idx on products (entity_id);
alter table products enable row level security;
drop policy if exists "public read approved" on products;
create policy "public read approved" on products for select using (review_status = 'approved');
comment on table products is
  'Fiches produits lues sur le site de la marque : ingrédients recopiés, ingrédients animaux repérés, statut végétal prouvé ou non (essai du 17/10/2026).';
