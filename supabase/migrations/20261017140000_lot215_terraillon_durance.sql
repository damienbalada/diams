-- Lot 215 : Terraillon et Durance (Open Products Facts, 17/10/2026).
--  - Terraillon SAS (Rueil-Malmaison), éditrice de terraillon.com ; SIREN vérifié dans l'annuaire
--    officiel des entreprises le 17/10/2026 (796080455, active, APE 46.43Z).
--  - Les Comptoirs de Durance (Grignan), éditrice de durance.fr ; SIREN vérifié le 17/10/2026
--    (443093562, active, APE 47.75Z).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, null, v.siren, 'FR', s.id, false
from (values
  ('terraillon-sas', 'TERRAILLON', 'Terraillon (société)', '796080455', 'household_durables'),
  ('les-comptoirs-de-durance', 'LES COMPTOIRS DE DURANCE', 'Les Comptoirs de Durance', '443093562', 'beauty_fragrance')
) as v(slug, legal_name, display_name, siren, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
