-- Sociétés éditrices des sites officiels de marques alimentaires (mentions légales), SIREN
-- vérifiés dans l'annuaire officiel des entreprises le 14/10/2026. Marques découvertes par
-- Wikidata (découverte seulement, jamais une preuve) ; l'appartenance est prouvée par la page
-- de mentions légales citée mot pour mot.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('abeilles-sante', 'ABEILLES SANTE', 'Abeilles Santé (Ballot-Flurin)', null, '388150906', 'FR', 'food'),
  ('isigny-sainte-mere', 'ISIGNY SAINTE-MERE', 'Isigny Sainte-Mère', null, '317750818', 'FR', 'food'),
  ('cave-de-lugny', 'SOC COOPERATIVE VINICOLE LUGNY L''AURORE', 'Cave de Lugny', null, '778593103', 'FR', 'wines_spirits'),
  ('cave-de-tain', 'CAVE TAIN L''HERMITAGE, UNION DES PROPRIETAIRES', 'Cave de Tain', null, '301193520', 'FR', 'wines_spirits'),
  ('hafner-entreprises', 'HAFNER ENTREPRISES', 'Hafner', null, '539020339', 'FR', 'food'),
  ('capver', 'CAPVER', 'Capver (Delespaul-Havez)', null, '480106061', 'FR', 'food'),
  ('tea-heritage', 'TEA HERITAGE', 'Tea Heritage', null, '828285221', 'FR', 'beverages'),
  ('famille-michaud-apiculteurs', 'FAMILLE MICHAUD APICULTEURS', 'Famille Michaud Apiculteurs', null, '775638117', 'FR', 'food'),
  ('origine-truffe', 'ORIGINE TRUFFE', 'Origine Truffe', null, '922410501', 'FR', 'food'),
  ('nutri-et-co', 'NUTRI&CO', 'Nutri&Co', null, '825396492', 'FR', 'food'),
  ('biovie', 'BIOVIE', 'Biovie', null, '819328808', 'FR', 'food'),
  ('daregal', 'DAREGAL', 'Darégal', null, '964202295', 'FR', 'food'),
  ('nougat-chabert-et-guillot', 'NOUGAT CHABERT ET GUILLOT', 'Nougat Chabert et Guillot', null, '401620513', 'FR', 'food'),
  ('francois-doucet-confiseur', 'FRANCOIS DOUCET CONFISEUR', 'François Doucet Confiseur', null, '310727151', 'FR', 'food'),
  ('brasserie-pietra', 'BRASSERIE PIETRA', 'Brasserie Pietra', null, '400016622', 'FR', 'wines_spirits'),
  ('brasserie-lancelot', 'BRASSERIE LANCELOT', 'Brasserie Lancelot', null, '950471177', 'FR', 'wines_spirits'),
  ('brasserie-goudale', 'BRASSERIE GOUDALE', 'Brasserie Goudale (Brasserie de Saint-Omer)', null, '487767816', 'FR', 'wines_spirits'),
  ('ninkasi-entreprises', 'NINKASI ENTREPRISES', 'Ninkasi', null, '421739285', 'FR', 'wines_spirits'),
  ('brasserie-cambier', 'BRASSERIE CAMBIER', 'Brasserie Cambier', null, '802817635', 'FR', 'wines_spirits'),
  ('tiliz', 'TILIZ', 'Tiliz (Le Mochi Glacé)', null, '799144696', 'FR', 'food'),
  ('earth-made', 'EARTH MADE', 'Earth Made (Nudj)', null, '878468370', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
