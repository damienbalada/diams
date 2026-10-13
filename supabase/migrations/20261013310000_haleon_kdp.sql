-- Haleon (santé grand public : Sensodyne, parodontax, Voltaren…) et Keurig Dr Pepper,
-- propriétaire de JDE Peet's depuis le 01/04/2026 (rapport trimestriel 10-Q au
-- 30/06/2026 : « The acquisition of JDE Peet's on April 1, 2026 »). LEI vérifiés dans
-- le registre GLEIF le 13/10/2026 (entité active, LEI émis).
--   Haleon plc               549300PSB3WWEODCUP19  (GB)
--   Keurig Dr Pepper Inc.    DYTQ8KRTKO7Y2BVU5K74  (US)
insert into entities (slug, legal_name, display_name, lei, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.country, s.id, false
from (values
  ('haleon',           'Haleon plc',            'Haleon',           '549300PSB3WWEODCUP19', 'GB', 'personal_care'),
  ('keurig-dr-pepper', 'Keurig Dr Pepper Inc.', 'Keurig Dr Pepper', 'DYTQ8KRTKO7Y2BVU5K74', 'US', 'beverages')
) as v(slug, legal_name, display_name, lei, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
