-- Sociétés françaises qui déclarent des marques dans la liste officielle de Santé publique
-- France « Entreprises et marques utilisant le Nutri-Score en France » (janvier 2026).
-- Sélection en série : nom identique à une seule société active de l'annuaire officiel des
-- entreprises (recherche-entreprises, 13/10/2026), de 6 à 9 salariés (fabricants agroalimentaires, NAF 10 et 11), ni entrepreneur
-- individuel, ni organisme public ou associatif, ni importateur, ni restauration ; relue.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('airchips-nutrition', 'AIRCHIPS NUTRITION', 'Airchips Nutrition', null, '793927294', 'FR', 'food'),
  ('gourmie-s', 'GOURMIE''S', 'Gourmie''S', null, '527700124', 'FR', 'food'),
  ('infuseo', 'SAS INFUSEO', 'Infuseo', null, '884853318', 'FR', 'beverages'),
  ('kim-oanh-foods', 'KIM OANH FOODS', 'Kim Oanh Foods', null, '850903360', 'FR', 'food'),
  ('la-teurgoule-de-cambremer', 'LA TEURGOULE DE CAMBREMER', 'La Teurgoule de Cambremer', null, '538255332', 'FR', 'food'),
  ('le-destin-du-gourmand', 'LE DESTIN DU GOURMAND', 'Le Destin du Gourmand', null, '849133210', 'FR', 'food'),
  ('le-mas-de-l-armandine', 'LE MAS DE L''ARMANDINE', 'Le Mas de l''Armandine', null, '503795361', 'FR', 'food'),
  ('ltc-les-bonnes-choses', 'LTC LES BONNES CHOSES', 'Ltc les Bonnes Choses', null, '894292366', 'FR', 'food'),
  ('manufacture-des-confitures', 'MANUFACTURE DES CONFITURES', 'Manufacture des Confitures', null, '828371484', 'FR', 'food'),
  ('mo-rice', 'MO RICE', 'Mo Rice', null, '832732325', 'FR', 'food'),
  ('neogourmets', 'NEOGOURMETS', 'Neogourmets', null, '840211031', 'FR', 'food'),
  ('nossa-fruits', 'NOSSA   FRUITS', 'Nossa Fruits', null, '788957033', 'FR', 'food'),
  ('numorning', 'NUMORNING', 'Numorning', null, '831343132', 'FR', 'food'),
  ('nutrianne', 'NUTRIANNE', 'Nutrianne', null, '820953453', 'FR', 'food'),
  ('pizza-fraiche', 'PIZZA FRAICHE', 'Pizza Fraiche', null, '793353079', 'FR', 'food'),
  ('ferme-de-letourville', 'SARL FERME DE LETOURVILLE', 'Ferme de Letourville', null, '813635828', 'FR', 'food'),
  ('terra-ceres', 'TERRA CERES', 'Terra Ceres', null, '811757640', 'FR', 'food'),
  ('un-monde-metis', 'UN MONDE METIS', 'Un Monde Metis', null, '815381884', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
