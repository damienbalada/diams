-- Relevé des codes-barres scannés que l'Index ne reconnaît pas, pour choisir les marques à ajouter.
-- Aucune donnée personnelle : le code, ce que les bases ouvertes en disent, un compteur et deux dates.
create table if not exists public.scans_non_reconnus (
  code text primary key,
  -- code_inconnu : absent des bases ouvertes ; marque_absente : marque lue mais pas dans l'Index ;
  -- marque_non_renseignee : produit connu, marque vide dans la base ouverte.
  motif text not null check (motif in ('code_inconnu', 'marque_absente', 'marque_non_renseignee')),
  produit text,
  marques text[] not null default '{}',
  base text,
  nombre integer not null default 1,
  premier timestamptz not null default now(),
  dernier timestamptz not null default now()
);

alter table public.scans_non_reconnus enable row level security;
-- Aucune politique : seule la clé de service (site, back-office) lit et écrit.

create index if not exists scans_non_reconnus_nombre on public.scans_non_reconnus (nombre desc, dernier desc);

create or replace function public.noter_scan_non_reconnu(p_code text, p_motif text, p_produit text, p_marques text[], p_base text)
returns void
language sql
security definer
set search_path = public
as $$
  insert into public.scans_non_reconnus (code, motif, produit, marques, base)
  values (p_code, p_motif, p_produit, coalesce(p_marques, '{}'), p_base)
  on conflict (code) do update set
    motif = excluded.motif,
    produit = coalesce(excluded.produit, scans_non_reconnus.produit),
    marques = excluded.marques,
    base = coalesce(excluded.base, scans_non_reconnus.base),
    nombre = scans_non_reconnus.nombre + 1,
    dernier = now();
$$;

revoke all on function public.noter_scan_non_reconnu(text, text, text, text[], text) from public, anon, authenticated;
grant execute on function public.noter_scan_non_reconnu(text, text, text, text[], text) to service_role;
