-- Lot 221 : propriétaires de marques non alimentaires (suivi Open Products Facts, 17/10/2026), nommés dans
-- les mentions légales du site officiel de chaque marque. SIREN vérifiés dans l'annuaire officiel des
-- entreprises et LEI dans le registre GLEIF le 17/10/2026 (tous actifs) ; sans LEI : Westmark GmbH,
-- A.W. Faber-Castell Retail GmbH, PNY Technologies Inc. (absents de GLEIF sous ce nom).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('zefal-sa', 'ZEFAL', 'Zéfal (société)', null, '572029106', 'FR', 'household_durables'),
  ('duralex-scop', 'DURALEX SCOP SA', 'Duralex SCOP', null, '931037998', 'FR', 'household_durables'),
  ('glenat-editions', 'GLENAT EDITIONS', 'Glénat Éditions', null, '302069414', 'FR', 'publishing'),
  ('upsa-sas', 'UPSA SAS', 'UPSA (société)', null, '803247956', 'FR', 'personal_care'),
  ('cooperation-pharmaceutique-francaise', 'COOPERATION PHARMACEUTIQUE FRANCAISE', 'Cooper (Coopération pharmaceutique française)', null, '399227636', 'FR', 'personal_care'),
  ('delta-mundolsheim', 'DELTA', 'Delta (Livoo)', null, '324432186', 'FR', 'household_durables'),
  ('magnard-vuibert', 'MAGNARD-VUIBERT', 'Magnard-Vuibert', null, '347686792', 'FR', 'publishing'),
  ('pileje-sas', 'PILEJE', 'PiLeJe (société)', null, '950450452', 'FR', 'personal_care'),
  ('skis-rossignol', 'SKIS ROSSIGNOL', 'Skis Rossignol', null, '056502958', 'FR', 'fashion_leather'),
  ('staedtler-france', 'STAEDTLER FRANCE', 'Staedtler France', null, '419264171', 'FR', 'household_durables'),
  ('berlin-packaging-france', 'BERLIN PACKAGING FRANCE', 'Berlin Packaging France', null, '529681520', 'FR', 'household_durables'),
  ('ricoh-imaging-europe', 'RICOH IMAGING EUROPE SAS', 'Ricoh Imaging Europe', null, '519989420', 'FR', 'tech_electronics'),
  ('polti-france', 'POLTI FRANCE', 'Polti France', null, '402957617', 'FR', 'household_durables'),
  ('vaude-sport', 'VauDe Sport GmbH & Co. KG', 'VAUDE Sport', '529900A5OOTBS1YY1997', null, 'DE', 'fashion_leather'),
  ('schneider-schreibgerate', 'Schneider Schreibgeräte GmbH', 'Schneider Schreibgeräte', '967600PDX8UWJFKBOC90', null, 'DE', 'household_durables'),
  ('westmark-gmbh', 'Westmark GmbH', 'Westmark (société)', null, null, 'DE', 'household_durables'),
  ('wolfcraft-gmbh', 'wolfcraft GmbH', 'wolfcraft (société)', '529900WSG3K9A6KZ7C39', null, 'DE', 'household_durables'),
  ('faber-castell-retail', 'A.W. Faber-Castell Retail GmbH', 'Faber-Castell (groupe)', null, null, 'DE', 'household_durables'),
  ('fairphone-bv', 'FAIRPHONE B.V.', 'Fairphone (société)', '724500CMLPSLXBZSUL67', null, 'NL', 'tech_electronics'),
  ('razer-inc', 'Razer Inc.', 'Razer (société)', '529900B3H0RSWJ089K63', null, 'KY', 'tech_electronics'),
  ('pny-technologies', 'PNY Technologies Inc.', 'PNY Technologies', null, null, 'US', 'tech_electronics'),
  ('d-link-europe', 'D-LINK (EUROPE) LIMITED', 'D-Link (Europe)', '2138008KQEF136JB3188', null, 'GB', 'tech_electronics')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
