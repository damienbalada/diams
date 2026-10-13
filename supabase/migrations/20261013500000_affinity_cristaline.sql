-- Affinity Petcare S.A. (Espagne ; Ultima, Advance, Brekkies, Libra), page « Our brands »
-- de son site officiel ; LEI vérifié dans le registre GLEIF le 13/10/2026.
-- GIE Cristaline, propriétaire du site officiel de l'eau Cristaline selon ses mentions
-- légales (RCS Cusset 387 584 972) ; ses membres sont des sociétés d'eaux de source
-- (Société d'exploitation des sources Roxane, Société générale des eaux minérales
-- naturelles de Chambon, Pierval, Source Chantereine) selon l'annuaire officiel des
-- entreprises. Aucune société mère unique n'est déclarée : le GIE est retenu tel quel.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('affinity-petcare', 'Affinity Petcare, S.A.', 'Affinity Petcare', '549300L9109V36J94123', null, 'ES', 'pet_care'),
  ('gie-cristaline', 'GIE Cristaline', 'GIE Cristaline (eaux de source)', null, '387584972', 'FR', 'beverages')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
