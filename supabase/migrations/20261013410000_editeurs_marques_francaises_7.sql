-- Septième série d'éditeurs (mentions légales des sites officiels des marques).
-- SIREN vérifiés dans l'annuaire officiel des entreprises, LEI dans le registre GLEIF, le 13/10/2026.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('saint-louis-sucre', 'Saint Louis Sucre',  'Saint Louis Sucre',           '96950041VR4VXNVKTW82', '602056749', 'FR', 'food'),
  ('lmt-biscuiteries',  'LMT Biscuiteries',   'LMT Biscuiteries (Gavottes)', '969500SQ6SVTSRYLGB15', '379340151', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
