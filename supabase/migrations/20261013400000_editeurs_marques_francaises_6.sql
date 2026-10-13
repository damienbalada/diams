-- Sixième série d'éditeurs de marques de grande surface (mentions légales des sites
-- officiels des marques, numéro RCS cité). SIREN vérifiés dans l'annuaire officiel des
-- entreprises et LEI dans le registre GLEIF le 13/10/2026.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('brasserie-meteor',     'Brasserie Meteor',        'Brasserie Meteor',         '894500FHJEYQICBSSR06', '598500643', 'FR', 'beverages'),
  ('sph-gerard-bertrand',  'SPH Gérard Bertrand',     'Gérard Bertrand (société)', '969500SCO4UQIB7YJI41', '382338952', 'FR', 'wines_spirits'),
  ('barton-guestier-sas',  'Barton & Guestier',       'Barton & Guestier (société)', '9695007F9I5K69U4IK69', '592008999', 'FR', 'wines_spirits'),
  ('comptoir-des-lys',     'Comptoir des Lys',        'Comptoir des Lys (Coslys)', null,                  '480737030', 'FR', 'personal_care'),
  ('pierre-cattier',       'Pierre Cattier',          'Pierre Cattier (Cattier)', null,                   '408583698', 'FR', 'personal_care'),
  ('veh-products-france',  'VEH Products France',     'VEH Products France (Destop)', null,               '843497033', 'FR', 'home_care'),
  ('green-family',         'Green Family',            'Green Family (Love & Green)', '969500DV0FD1RUZWAK70', '529777583', 'FR', 'personal_care'),
  ('allegre-puericulture', 'Allègre Puériculture',    'Allègre Puériculture (Tigex)', null,               '407946037', 'FR', 'personal_care'),
  ('sodilac',              'Sodilac',                 'Sodilac (Laboratoire Modilac)', null,              '689801470', 'FR', 'food'),
  ('aurige',               'Aurige',                  'Aurige (Jacquet)',         '969500RBAFUZP4DTIO98', '582111936', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
