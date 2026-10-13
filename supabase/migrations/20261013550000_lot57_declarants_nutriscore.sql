-- Sociétés qui déclarent des marques vendues en hypermarché dans la liste officielle de
-- Santé publique France « Entreprises et marques utilisant le Nutri-Score en France »
-- (janvier 2026) et qui n'étaient pas encore dans DIAMS. SIREN vérifiés dans l'annuaire
-- officiel des entreprises et LEI dans le registre GLEIF le 13/10/2026.
-- Upfield France SAS (SIREN 812 853 844) porte aujourd'hui la dénomination Flora Food
-- France SAS : les annonces du BODACC pour ce numéro passent de « UPFIELD FRANCE SAS »
-- (comptes 2024) à « Flora Food France SAS » (modification du 15/11/2024).
-- Nardobel est la société mère directe de Nutrition et Santé (registre GLEIF).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('aldi-france', 'ALDI Centrale d''achat et Compagnie', 'Aldi (France)', null, '378569040', 'FR', 'retail_distribution'),
  ('nardobel', 'Nardobel', 'Nardobel (Nutrition & Santé : Gerblé, Céréal)', '9695001WYT7WBGZ0WF36', '488061318', 'FR', 'food'),
  ('grands-moulins-de-paris', 'Grands Moulins de Paris', 'Grands Moulins de Paris', null, '351466495', 'FR', 'food'),
  ('tipiak', 'SA Tipiak', 'Tipiak (société)', '969500JWHZYG3D8QLZ17', '301691655', 'FR', 'food'),
  ('galliance-elabores', 'Galliance Élaborés', 'Galliance Élaborés', null, '305375651', 'FR', 'food'),
  ('mutti-france', 'Mutti France SAS', 'Mutti France', null, '752053892', 'FR', 'food'),
  ('comolive', 'Comptoir Méditerranéen de l''Olive', 'Comptoir Méditerranéen de l''Olive (Comolive)', null, '612680272', 'FR', 'food'),
  ('conserves-france', 'Conserves France', 'Conserves France', '969500KZZI1WBNFI9924', '706220548', 'FR', 'food'),
  ('valade-sas', 'Valade', 'Valade (société)', '9695004MP0F91TYKH882', '677120263', 'FR', 'food'),
  ('nueva-pescanova-france', 'Nueva Pescanova France', 'Nueva Pescanova France', '96950023UG08D4EHCN50', '399276088', 'FR', 'food'),
  ('cereco', 'Cereco', 'Cereco (Grillon d''Or)', null, '381364959', 'FR', 'food'),
  ('daco-france', 'SA Daco France', 'Daco France', '969500IJYWRHFOR3S575', '300482916', 'FR', 'food'),
  ('maitres-laitiers-du-cotentin', 'Les Maîtres Laitiers du Cotentin', 'Les Maîtres Laitiers du Cotentin', '969500H6HD3XJAKBWV50', '338154610', 'FR', 'food'),
  ('francap', 'Francap Distribution', 'Francap', '9695005NIUZVC9BCSB06', '331087593', 'FR', 'retail_distribution'),
  ('cerafel', 'Cerafel', 'Cerafel (Prince de Bretagne)', '969500ZNY7TG3YIOLR19', '777572702', 'FR', 'food'),
  ('flora-food-france', 'Flora Food France SAS', 'Flora Food France (ex-Upfield France)', null, '812853844', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
