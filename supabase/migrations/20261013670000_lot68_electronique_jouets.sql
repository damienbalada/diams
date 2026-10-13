-- Groupes de l'électronique, du jeu vidéo, du jouet et de l'animalerie dont la marque
-- vendue en hypermarché porte le nom même de la société (HP, Canon, LEGO, Ravensburger…).
-- Aucune marque distincte n'est créée : la fiche du groupe sert de fiche de marque. LEI
-- vérifiés dans le registre GLEIF et SIREN dans l'annuaire officiel des entreprises le
-- 13/10/2026 (pas de LEI trouvé pour Canon Inc.). Playmobil France SARL (SIREN
-- 324 896 091) exploite la marque Playmobil en France (mentions légales du site, lot 68).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('hp-inc', 'HP Inc.', 'HP', 'WHKXQACZ14C5XRO8LW03', null, 'US', 'tech_electronics'),
  ('logitech', 'Logitech International S.A.', 'Logitech', '549300SN6PRK6IJJC215', null, 'CH', 'tech_electronics'),
  ('canon', 'Canon Inc.', 'Canon', null, null, 'JP', 'tech_electronics'),
  ('panasonic', 'Panasonic Holdings Corporation', 'Panasonic', '254900GE1G59KGWPHX32', null, 'JP', 'tech_electronics'),
  ('lg-electronics', 'LG Electronics Inc.', 'LG Electronics', '988400RMQFTGZIOG0609', null, 'KR', 'tech_electronics'),
  ('seiko-epson', 'Seiko Epson Corporation', 'Epson (Seiko Epson)', '549300NIOFQDR749W206', null, 'JP', 'tech_electronics'),
  ('brother-industries', 'Brother Industries, Ltd.', 'Brother', '549300O5FACQ67KI6R92', null, 'JP', 'tech_electronics'),
  ('dyson', 'Dyson Technology Limited', 'Dyson', '213800CME59HCE5XBI94', null, 'GB', 'household_durables'),
  ('lenovo', 'Lenovo Group Limited', 'Lenovo', '254900VUZRGD5U73RE46', null, 'HK', 'tech_electronics'),
  ('xiaomi', 'Xiaomi Corporation', 'Xiaomi', '2549001ACVFAZRNMKL32', null, 'KY', 'tech_electronics'),
  ('nintendo', 'Nintendo Co., Ltd.', 'Nintendo', '353800FEEXU6I9M0ZF27', null, 'JP', 'tech_electronics'),
  ('ubisoft', 'Ubisoft Entertainment', 'Ubisoft', '969500I7C8V1LBIMSM05', '335186094', 'FR', 'tech_electronics'),
  ('garmin', 'Garmin Ltd.', 'Garmin', '2549001E0HIPIJQ0W046', null, 'CH', 'tech_electronics'),
  ('acer', 'Acer Incorporated', 'Acer', '2549006Z3IVAZIQEUM25', null, 'TW', 'tech_electronics'),
  ('asus', 'ASUSTeK Computer Inc.', 'ASUS', '254900B3WB4OGRB7HM13', null, 'TW', 'tech_electronics'),
  ('lego', 'LEGO System A/S', 'LEGO', 'UGKYQUOFW6QSIS3P4P93', null, 'DK', 'toys_games'),
  ('ravensburger', 'Ravensburger Aktiengesellschaft', 'Ravensburger', '529900SNJW6AFFYN0P96', null, 'DE', 'toys_games'),
  ('clementoni', 'Clementoni S.p.A.', 'Clementoni', '815600858736EE7D6192', null, 'IT', 'toys_games'),
  ('maped', 'Maped', 'Maped', '969500I91GPMXI3NP144', '325720423', 'FR', 'household_durables'),
  ('vitakraft', 'Vitakraft pet care GmbH & Co. KG', 'Vitakraft', '529900KXJ7UQAEPEBJ41', null, 'DE', 'pet_care'),
  ('playmobil-france', 'Playmobil France SARL', 'Playmobil France', null, '324896091', 'FR', 'toys_games')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
