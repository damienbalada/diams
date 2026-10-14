-- Lot 91 : déclarants de la liste Nutri-Score (Santé publique France, janvier 2026) dont le nom
-- correspond exactement et à une seule société active de l'annuaire officiel des entreprises,
-- écartés jusqu'ici par le filtre d'activité et relus à la main le 14/10/2026 (restauration,
-- personnes physiques, associations, collectivités et homonymes probables exclus).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('110-graines', '110 GRAINES', '110 Graines (société)', null, '842651150', 'FR', 'food'),
  ('alterfoodie', 'ALTERFOODIE', 'Alterfoodie', null, '817458938', 'FR', 'food'),
  ('au-royaume-des-dattes', 'AU ROYAUME DES DATTES', 'Au Royaume des Dattes (société)', null, '820105542', 'FR', 'food'),
  ('barjo-nutrition', 'BARJO NUTRITION', 'Barjo Nutrition', null, '977557461', 'FR', 'food'),
  ('bofrost-france', 'BOFROST*FRANCE', 'Bofrost France', null, '418037768', 'FR', 'food'),
  ('carreleon', 'CARRELEON', 'CarréLéon', null, '832193304', 'FR', 'food'),
  ('chazal-dole', 'CHAZAL DOLE', 'Chazal Dole', null, '479753170', 'FR', 'food'),
  ('colorevi', 'COLOREVI', 'Colorévi', null, '830419875', 'FR', 'food'),
  ('dim-sum-cantine', 'DIM SUM CANTINE', 'Dim Sum Cantine', null, '793125568', 'FR', 'food'),
  ('el-ekeko', 'EL EKEKO', 'El Ekeko (société)', null, '920279692', 'FR', 'food'),
  ('gloria-maris-groupe', 'GLORIA MARIS GROUPE', 'Gloria Maris Groupe', null, '805237153', 'FR', 'food'),
  ('ilovert', 'ILOVERT', 'Ilovert', null, '821515772', 'FR', 'food'),
  ('kappa-drinks', 'KAPPA DRINKS', 'Kappa Drinks', null, '914388491', 'FR', 'food'),
  ('la-main-dans-le-bol', 'LA MAIN DANS LE BOL', 'La Main dans le Bol (société)', null, '851464701', 'FR', 'food'),
  ('laura-todd', 'LAURA TODD', 'Laura Todd (société)', null, '562100107', 'FR', 'food'),
  ('craquelins-de-saint-malo', 'LES CRAQUELINS DE SAINT-MALO', 'Les Craquelins de Saint-Malo (société)', null, '318175171', 'FR', 'food'),
  ('eleveurs-de-la-charentonne', 'LES ELEVEURS DE LA CHARENTONNE', 'Les Éleveurs de la Charentonne (société)', null, '478753353', 'FR', 'food'),
  ('lld-et-cie', 'LLD&CIE', 'LLD & Cie', null, '849937024', 'FR', 'food'),
  ('monsieur-muesli', 'MONSIEUR MUESLI', 'Monsieur Muesli (société)', null, '880318662', 'FR', 'food'),
  ('regals-du-touquet', 'REGALS DU TOUQUET', 'Régals du Touquet (Maison Pérard)', null, '339741076', 'FR', 'food'),
  ('so-fast-so-good', 'SO FAST SO GOOD', 'So Fast So Good', null, '815338850', 'FR', 'food'),
  ('so-shape', 'SO SHAPE', 'So Shape (société)', null, '798038345', 'FR', 'food'),
  ('toupargel', 'TOUPARGEL', 'Toupargel (société)', null, '957526858', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
