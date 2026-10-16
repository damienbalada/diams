-- Lot 113 : propriétaires de deux marques absentes de l'Index.
--  - Pågen Aktiebolag (Malmö), qui lance et fabrique Krisprolls (site krisprolls.fr) ; LEI vérifié
--    dans le registre GLEIF le 16/10/2026 (54930083O7X177ZIIV16, entité active).
--  - La Fournée Dorée (Les Achards), société désignée comme propriétaire dans les mentions légales
--    de lafourneedoree.fr ; SIREN vérifié dans l'annuaire officiel des entreprises le 16/10/2026
--    (817390941, active, code APE 10.71A).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('pagen', 'Pågen Aktiebolag', 'Pågen', '54930083O7X177ZIIV16', null, 'SE', 'food'),
  ('la-fournee-doree', 'La Fournée Dorée', 'La Fournée Dorée (société)', null, '817390941', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
