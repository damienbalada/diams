-- Cinquième série d'éditeurs de marques de grande surface (mentions légales des sites
-- officiels des marques, numéro RCS cité). SIREN vérifiés dans l'annuaire officiel des
-- entreprises et LEI dans le registre GLEIF le 13/10/2026.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('daucy-france',        'd''aucy France',                             'd''aucy France',                 '969500QMTCU456CPWJ67', '652008632', 'FR', 'food'),
  ('jean-henaff',         'Jean Hénaff SA',                             'Groupe Jean Hénaff',             null,                   '375580594', 'FR', 'food'),
  ('gb-foods-france',     'GB Foods France',                            'GB Foods France',                null,                   '391128378', 'FR', 'food'),
  ('st-hubert',           'St Hubert',                                  'St Hubert (société)',            null,                   '752329318', 'FR', 'food'),
  ('carte-noire-sas',     'Carte Noire SAS',                            'Carte Noire SAS',                null,                   '813978038', 'FR', 'beverages'),
  ('cafes-malongo',       'Compagnie Méditerranéenne des Cafés',        'Compagnie Méditerranéenne des Cafés (Malongo)', '969500YNKNT6RWAK0K09', '955802061', 'FR', 'beverages'),
  ('eaux-saint-amand',    'Société des Eaux Minérales de Saint-Amand',  'Eaux Minérales de Saint-Amand', null,                   '678800749', 'FR', 'beverages'),
  ('charal-sas',          'Charal',                                     'Charal (société)',               null,                   '546950379', 'FR', 'food'),
  ('delpeyrat-sas',       'Delpeyrat',                                  'Delpeyrat (société)',            '9695005XND174IRSJ074', '645680026', 'FR', 'food'),
  ('fhp-vileda',          'FHP-Vileda',                                 'FHP-Vileda',                     null,                   '341662112', 'FR', 'home_care'),
  ('phoceenne-cosmetique','La Phocéenne de Cosmétique',                 'La Phocéenne de Cosmétique',     '969500CG81KRI3DOG873', '408156131', 'FR', 'personal_care')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
