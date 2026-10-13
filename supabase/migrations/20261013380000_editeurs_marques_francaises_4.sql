-- Quatrième série d'éditeurs de marques de grande surface (mentions légales des sites
-- officiels des marques). SIREN vérifiés dans l'annuaire officiel des entreprises le
-- 13/10/2026 (aucun LEI émis pour ces sociétés).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('haribo',                        'Haribo Ricqlès Zan',                   'Haribo (France)',            null, '572149169', 'FR', 'food'),
  ('campofrio-france',              'Campofrío Food Group France Holding',  'Campofrío France',           null, '420001257', 'FR', 'food'),
  ('grandes-sources-de-wattwiller', 'Les Grandes Sources de Wattwiller',    'Grandes Sources de Wattwiller', null, '383616307', 'FR', 'beverages'),
  ('guyader-gastronomie',           'Guyader Gastronomie',                  'Guyader Gastronomie',        null, '392488847', 'FR', 'food'),
  ('ac-marca',                      'AC Marca Idéal',                       'AC Marca (Sanytol)',         null, '971502869', 'FR', 'home_care')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
