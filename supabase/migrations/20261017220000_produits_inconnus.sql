-- Produits inconnus photographiés par les lecteurs (décision de l'éditeur, 17/10/2026). Quand un code-barres
-- scanné n'est pas reconnu (code absent des bases ouvertes, ou marque pas encore dans l'Index), l'appli
-- propose d'envoyer jusqu'à trois photos : la face avant (nom et marque), le dos (fabricant, adresse,
-- « fabriqué pour… ») et, pour un produit alimentaire, la liste des ingrédients. Ces photos servent à
-- trouver la marque et son propriétaire ; elles ne sont publiées qu'après vérification et avec l'accord
-- donné à l'envoi. Aucune donnée personnelle n'est demandée.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('produits-a-verifier', 'produits-a-verifier', false, 5242880, array['image/jpeg', 'image/png', 'image/webp'])
on conflict (id) do nothing;

create table if not exists product_submissions (
  id uuid primary key default gen_random_uuid(),
  code text not null check (code ~ '^[0-9]{8,14}$'),
  product_name text check (product_name is null or length(product_name) <= 200),
  brand_name text check (brand_name is null or length(brand_name) <= 120),
  alimentaire boolean,
  photo_face text not null,
  photo_dos text,
  photo_ingredients text,
  purchase_place text check (purchase_place is null or length(purchase_place) <= 200),
  consent boolean not null check (consent),
  status text not null default 'pending' check (status in ('pending', 'traite', 'rejected')),
  review_note text,
  reviewed_at timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists product_submissions_status_idx on product_submissions (status, created_at);
create index if not exists product_submissions_code_idx on product_submissions (code);
-- Aucune lecture ni écriture publique : tout passe par le serveur du site (clé de service).
alter table product_submissions enable row level security;
comment on table product_submissions is
  'Photos de produits non reconnus envoyées depuis l''appli (face, dos, ingrédients), à traiter par un éditeur : identifier la marque et son propriétaire.';
