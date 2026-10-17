-- Étiquettes photographiées par la communauté (décision de l'éditeur, 17/10/2026). L'étiquette est le
-- document légal du produit (règlement (UE) n° 1169/2011, INCO : liste des ingrédients et allergènes
-- mis en évidence). Circuit : dépôt d'une photo (espace privé) → vérification humaine et recopie de la
-- liste d'ingrédients contre la photo → la photo passe dans l'espace public comme pièce justificative,
-- et le produit entre dans la table products. Aucune donnée personnelle du contributeur n'est demandée.

-- Espaces de stockage : privé pour les photos à vérifier, public pour les photos validées.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('etiquettes-a-verifier', 'etiquettes-a-verifier', false, 5242880, array['image/jpeg', 'image/png', 'image/webp']),
       ('etiquettes', 'etiquettes', true, 5242880, array['image/jpeg', 'image/png', 'image/webp'])
on conflict (id) do nothing;

create table if not exists label_submissions (
  id uuid primary key default gen_random_uuid(),
  entity_id uuid not null references entities(id) on delete cascade,
  product_name text not null check (length(product_name) between 2 and 200),
  photo_path text not null,
  purchase_date date,
  purchase_place text check (purchase_place is null or length(purchase_place) <= 200),
  consent boolean not null check (consent),
  status text not null default 'pending' check (status in ('pending', 'approved', 'rejected')),
  transcription text,
  review_note text,
  reviewed_at timestamptz,
  product_id uuid references products(id) on delete set null,
  created_at timestamptz not null default now()
);
create index if not exists label_submissions_status_idx on label_submissions (status, created_at);
-- Aucune lecture ni écriture publique : tout passe par le serveur du site (clé de service).
alter table label_submissions enable row level security;
comment on table label_submissions is
  'Photos d''étiquettes déposées depuis les fiches, en attente de vérification humaine (recopie de la liste d''ingrédients contre la photo).';

-- Produits : origine de la lecture (fiche du site de la marque ou étiquette photographiée).
alter table products add column if not exists source_kind text not null default 'fiche_marque'
  check (source_kind in ('fiche_marque', 'etiquette'));
alter table products add column if not exists purchase_date date;
alter table products add column if not exists purchase_place text;
