-- Deuxième série de sociétés françaises éditrices de marques vendues en hypermarché
-- (mentions légales des sites officiels des marques, numéro RCS cité). SIREN vérifiés
-- dans l'annuaire officiel des entreprises et LEI dans le registre GLEIF le 13/10/2026.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('chancerelle', 'Conserverie Chancerelle', 'Chancerelle (Connétable)', '9695008SWD8DPY0EHJ85', '443146873', 'FR', 'food'),
  ('taittinger', 'Taittinger Compagnie Commerciale et Viticole Champenoise', 'Taittinger CCVC', '9695000S7TCVUU48M310', '490341062', 'FR', 'wines_spirits'),
  ('fromagerie-de-livarot', 'Fromagerie de Livarot', 'Fromagerie de Livarot (Graindorge)', null, '428937932', 'FR', 'food'),
  ('compagnie-madrange', 'Compagnie Madrange', 'Compagnie Madrange', null, '829323211', 'FR', 'food'),
  ('brunel', 'Brunel', 'Brunel (Starwax)', '969500F4AMOHTXENJ704', '378517148', 'FR', 'home_care'),
  ('patisseries-gourmandes', 'Pâtisseries Gourmandes', 'Pâtisseries Gourmandes (Ker Cadélac)', null, '302476106', 'FR', 'food'),
  ('bjorg-et-compagnie', 'Bjorg et Compagnie', 'Bjorg et Compagnie', null, '402712350', 'FR', 'food'),
  ('la-fermiere', 'Société La Fermière', 'La Fermière (société)', null, '055811996', 'FR', 'food'),
  ('charcuterie-vendeenne', 'Charcuterie Vendéenne', 'Charcuterie Vendéenne Petitgas', null, '322950817', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
