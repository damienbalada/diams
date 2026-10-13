-- Sociétés étrangères qui déclarent dans la liste officielle du Nutri-Score (Santé publique
-- France, janvier 2026) des marques vendues couramment en hypermarché en France. LEI
-- vérifiés dans le registre GLEIF le 13/10/2026 quand ils existent.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('fage-international', 'FAGE International S.A.', 'FAGE', null, null, 'LU', 'food'),
  ('wonderful-brands', 'Wonderful Brands BV', 'Wonderful Brands', '6994005L1GSNQRM4AG03', null, 'BE', 'food'),
  ('foods-for-tomorrow', 'Foods for Tomorrow SL', 'Foods for Tomorrow (Heura)', '959800MH7VT2SW70WM08', null, 'ES', 'food'),
  ('vivil', 'VIVIL A. Müller GmbH & Co. KG', 'Vivil', '5299005ZP8KKA2B34357', null, 'DE', 'food'),
  ('green-park-snacks', 'Green Park Snacks Ltd', 'Green Park Snacks (Hippeas)', null, null, 'GB', 'food'),
  ('greenyard', 'Greenyard NV', 'Greenyard', '5493000VB1LNC3MESW25', null, 'BE', 'food'),
  ('kioene', 'Kioene S.p.A.', 'Kioene (société)', null, null, 'IT', 'food'),
  ('planted-foods', 'Planted Foods GmbH', 'Planted Foods', null, null, 'DE', 'food'),
  ('beyond-meat', 'Beyond Meat, Inc.', 'Beyond Meat (société)', '549300XQ946NCE51DR09', null, 'US', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
