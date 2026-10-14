-- Sociétés étrangères qui déclarent des marques vendues en France dans la liste officielle de
-- Santé publique France « Entreprises et marques utilisant le Nutri-Score en France »
-- (janvier 2026) : nom légal identique à une seule entité active du registre GLEIF
-- (identifiants d'entités juridiques), formes juridiques ignorées, lu le 14/10/2026 ; écartés à la
-- relecture : forme juridique ou pays différents du déclarant, doublon du lot 84.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('all-freez', 'ALL-FREEZ', 'ALL-FREEZ', '549300VZTFX8B118LN86', null, 'BE', 'food'),
  ('blue-skies-holdings-limited', 'BLUE SKIES HOLDINGS LIMITED', 'BLUE SKIES HOLDINGS LIMITED', '213800HYXMDTG93QDZ10', null, 'GB', 'food'),
  ('crop-s-ready-meals', 'Crop''s Ready Meals', 'Crop''s Ready Meals', '699400BV1FVJ4EDUC523', null, 'BE', 'food'),
  ('neri-industria-alimentare', 'NERI INDUSTRIA ALIMENTARE S.P.A.', 'NERI INDUSTRIA ALIMENTARE', '815600BA3DFA178CA102', null, 'IT', 'food'),
  ('theo-coertjens-international', 'Theo Coertjens International', 'Theo Coertjens International', '875500XMXB8ZUQS6Y516', null, 'BE', 'food'),
  ('vitaver', 'Vitaver', 'Vitaver', '967600WVPZCCL83LOI49', null, 'BE', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
