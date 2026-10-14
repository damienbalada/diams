-- Sociétés françaises qui déclarent des marques dans la liste officielle de Santé publique
-- France « Entreprises et marques utilisant le Nutri-Score en France » (janvier 2026).
-- Troisième passe (nom commercial ou enseigne d'un établissement identique à la marque, ou nom identique au déclarant ; candidat unique d'activité alimentaire), toutes tailles (demande de l'éditeur du 14/10/2026 : toutes les marques
-- alimentaires vendues en France) : nom identique ou contenu dans celui d'une seule société active de
-- l'annuaire officiel des entreprises (recherche-entreprises), activité alimentaire (fabrication,
-- commerce de gros, exploitation agricole ou piscicole, holding, vente à distance), ni
-- entrepreneur individuel, ni organisme public ou associatif, ni importateur, ni
-- restauration, ni boutique artisanale ; relue ligne par ligne.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('benoit-promotion', 'BENOIT PROMOTION', 'Benoit Promotion', null, '398589119', 'FR', 'food'),
  ('le-maraichef', 'LE MARAICHEF', 'Le Maraichef', null, '388456485', 'FR', 'food'),
  ('2a-distrib', '2A DISTRIB', '2a Distrib', null, '942563263', 'FR', 'beverages'),
  ('lowcal', 'LOWCAL', 'Lowcal', null, '917709198', 'FR', 'food'),
  ('les-oeufs-de-thibault', 'LES OEUFS DE THIBAULT', 'Les Oeufs de Thibault', null, '939746632', 'FR', 'food'),
  ('les-gourmands-exigeants', 'LES GOURMANDS EXIGEANTS', 'Les Gourmands Exigeants', null, '841557549', 'FR', 'food'),
  ('mk-factory', 'MK FACTORY', 'Mk Factory', null, '885078733', 'FR', 'food'),
  ('eat4good-france', 'EAT4GOOD FRANCE', 'Eat4good France', null, '450246152', 'FR', 'food'),
  ('oppan', 'OPPAN', 'Oppan', null, '328089792', 'FR', 'food'),
  ('rebelle', 'REBELLE', 'Rebelle', null, '901053934', 'FR', 'food'),
  ('bellycare', 'BELLYCARE', 'Bellycare', null, '982137291', 'FR', 'food'),
  ('h-oat-naturel', 'H''OAT NATUREL', 'H''Oat Naturel', null, '900126525', 'FR', 'food'),
  ('les-chips-de-l-aveyron', 'LES CHIPS DE L''AVEYRON', 'Les Chips de l''Aveyron', null, '410607816', 'FR', 'food'),
  ('pepite', 'PEPITE', 'Pepite', null, '830469516', 'FR', 'food'),
  ('jampi', 'JAMPI', 'Jampi', null, '310644315', 'FR', 'food'),
  ('transparence', 'TRANSPARENCE', 'Transparence', null, '885041764', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
