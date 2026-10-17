-- Fiches produits : liste d'ingrédients (alimentation, cosmétique) ou composition (vêtements, chaussures :
-- laine, cuir, soie, duvet…). La colonne ingredients garde le texte relu mot pour mot dans les deux cas.
alter table public.products
  add column if not exists nature text not null default 'ingredients'
  check (nature in ('ingredients', 'composition'));
