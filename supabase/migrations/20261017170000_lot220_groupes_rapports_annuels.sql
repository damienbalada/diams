-- Lot 220 : propriétaires de marques non alimentaires absentes (Open Products Facts, 17/10/2026),
-- prouvées par leur rapport annuel officiel. LEI vérifiés dans le registre GLEIF le 17/10/2026 (actifs).
--  - Corsair Gaming, Inc. (Corsair, Elgato) : 549300Y7YT18L8G0H525
--  - Masco Corporation (Hansgrohe, Axor ; 68 % de Hansgrohe SE) : 5GCSNMQXHEYA1JO8QN11
--  - Ecolab Inc. (Anios, Laboratoires Anios acquis) : 82DYEISM090VG8LTLS26
--  - Arkema (Bostik) : 9695000EHMS84KKP2785
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('corsair-gaming', 'Corsair Gaming, Inc.', 'Corsair Gaming', '549300Y7YT18L8G0H525', null, 'US', 'tech_electronics'),
  ('masco', 'Masco Corporation', 'Masco', '5GCSNMQXHEYA1JO8QN11', null, 'US', 'household_durables'),
  ('ecolab', 'Ecolab Inc.', 'Ecolab', '82DYEISM090VG8LTLS26', null, 'US', 'home_care'),
  ('arkema', 'ARKEMA', 'Arkema', '9695000EHMS84KKP2785', '445074685', 'FR', 'household_durables')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
