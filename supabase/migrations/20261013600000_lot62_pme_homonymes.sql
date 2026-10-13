-- Sociétés françaises qui déclarent des marques dans la liste officielle de Santé publique
-- France « Entreprises et marques utilisant le Nutri-Score en France » (janvier 2026).
-- Sélection en série : nom identique à une seule société active de l'annuaire officiel des
-- entreprises (recherche-entreprises, 13/10/2026), au moins 10 salariés, ni entrepreneur
-- individuel, ni organisme public ou associatif, ni importateur, ni restauration ; relue.
-- Lot 62 : sociétés qui avaient plusieurs homonymes exacts dans l'annuaire, départagées
-- par l'activité (code NAF agroalimentaire) et l'effectif (au moins 10 salariés).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('alisa', 'ALISA', 'Alisa', null, '500169115', 'FR', 'food'),
  ('beyer', 'SAS BEYER', 'Beyer', null, '947351656', 'FR', 'food'),
  ('charles-christ', 'CHARLES CHRIST', 'Charles Christ', null, '808634075', 'FR', 'food'),
  ('convivial', 'CONVIVIAL', 'Convivial', null, '350499398', 'FR', 'food'),
  ('i-grec', 'I-GREC', 'I-Grec', null, '802576140', 'FR', 'food'),
  ('jbg', 'JBG', 'JBG', null, '831899174', 'FR', 'food'),
  ('khtc', 'KHTC', 'Khtc', null, '800294084', 'FR', 'food'),
  ('la-compagnie-des-pyrenees', 'LA COMPAGNIE DES PYRENEES', 'La Compagnie des Pyrenees', null, '828966754', 'FR', 'beverages'),
  ('le-coq-noir', 'LE COQ NOIR', 'Le Coq Noir', null, '316203942', 'FR', 'food'),
  ('laiterie-de-saint-denis-de-l-hotel', 'LAITERIE DE SAINT-DENIS DE L''HOTEL', 'Laiterie de Saint-Denis de l''Hotel', null, '085581494', 'FR', 'food'),
  ('pains-et-tradition', 'PAINS ET TRADITION SAS', 'Pains et Tradition', null, '498279140', 'FR', 'food'),
  ('palimex', 'PALIMEX', 'Palimex', null, '330177635', 'FR', 'food'),
  ('production-des-elevages-bourgon', 'PRODUCTION DES ELEVAGES BOURGON', 'Production des Elevages Bourgon', null, '311117444', 'FR', 'food'),
  ('rochefontaine', 'ROCHEFONTAINE', 'Rochefontaine', null, '344209663', 'FR', 'food'),
  ('sainte-lucie', 'SAINTE LUCIE', 'Sainte Lucie', null, '572151207', 'FR', 'food'),
  ('seablue', 'SEABLUE', 'Seablue', null, '432083558', 'FR', 'food'),
  ('sias', 'SIAS', 'Sias', null, '883646739', 'FR', 'food'),
  ('sud-mer', 'SUD MER', 'Sud Mer', null, '441041720', 'FR', 'food'),
  ('voie-verte', 'VOIE VERTE', 'Voie Verte', null, '749954038', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
