-- Groupes cotés dont les marques sont vendues en hypermarché en France (boissons,
-- spiritueux, rasage, piles, jouets, papeterie, petit électroménager, outillage,
-- champagne, thé, chocolat). LEI vérifiés dans le registre GLEIF le 13/10/2026
-- (entité active, LEI émis) ; SIREN dans l'annuaire officiel des entreprises.
--   Monster Beverage Corporation              52990090AP0E7HCB6F33  (US)
--   Brown-Forman Corporation                  549300873K3LXF7ARU34  (US)
--   Edgewell Personal Care Company            549300CY8QZDL4Z3RU59  (US)
--   Energizer Holdings, Inc.                  5493000D6NN0V57UME20  (US)
--   Mattel, Inc.                              549300VELLG24KHTJ564  (US)
--   Hasbro, Inc.                              549300NUB6D2R1ITYR45  (US)
--   3M Company                                LUZQVYP4VS22CLWDAR65  (US)
--   Newell Brands Inc.                        549300LWGYFM1TVO1Z12  (US)
--   Stanley Black & Decker, Inc.              549300DJ09SMTO561131  (US)
--   Post Holdings, Inc.                       JM1I5YUAURL6DC8N1468  (US)
--   Laurent-Perrier                           96950036OIHAEGNGJ871  (FR, SIREN 335680096)
--   Marie Brizard Wine and Spirits            969500XQM2JOWHKWI437  (FR, SIREN 380695213)
--   Koninklijke Philips N.V.                  H1FJE8H61JGM1JSGM897  (NL)
--   De' Longhi S.p.A.                         8156000E09A52C4F8A38  (IT)
--   Associated British Foods plc              GBQKSY6W7G0OHCQ8OQ72  (GB)
--   Chocoladefabriken Lindt & Sprüngli AG     529900JYJNNOKKAGK736  (CH)
--   Aktiebolaget Electrolux                   549300Y3HHZB1ZGFPJ93  (SE)
--
-- Deux secteurs nouveaux, sans exploitation animale présumée (comme la tech) mais
-- concernés par le plastique : jouets, et équipement durable de la maison.
insert into sectors (code, name, description, animal_relevant, wap_relevant, inv_relevant, plastic_relevant, water_relevant) values
  ('toys_games', 'Jouets & Jeux', 'Jouets, jeux de société, loisirs créatifs.', false, false, false, true, false),
  ('household_durables', 'Équipement de la maison', 'Électroménager, outillage, piles, papeterie, articles ménagers durables.', false, false, false, true, false)
on conflict (code) do nothing;

insert into indicator_sectors (indicator_id, sector_id)
select i.id, s.id from indicators i, sectors s
where i.code = 'ENV_GHG_TREND' and s.code in ('toys_games', 'household_durables')
on conflict (indicator_id, sector_id) do nothing;

insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('monster-beverage',     'Monster Beverage Corporation',          'Monster Beverage',         '52990090AP0E7HCB6F33', null,        'US', 'beverages'),
  ('brown-forman',         'Brown-Forman Corporation',              'Brown-Forman',             '549300873K3LXF7ARU34', null,        'US', 'wines_spirits'),
  ('edgewell',             'Edgewell Personal Care Company',        'Edgewell',                 '549300CY8QZDL4Z3RU59', null,        'US', 'personal_care'),
  ('energizer',            'Energizer Holdings, Inc.',              'Energizer Holdings',       '5493000D6NN0V57UME20', null,        'US', 'household_durables'),
  ('mattel',               'Mattel, Inc.',                          'Mattel',                   '549300VELLG24KHTJ564', null,        'US', 'toys_games'),
  ('hasbro',               'Hasbro, Inc.',                          'Hasbro',                   '549300NUB6D2R1ITYR45', null,        'US', 'toys_games'),
  ('3m',                   '3M Company',                            '3M',                       'LUZQVYP4VS22CLWDAR65', null,        'US', 'household_durables'),
  ('newell-brands',        'Newell Brands Inc.',                    'Newell Brands',            '549300LWGYFM1TVO1Z12', null,        'US', 'household_durables'),
  ('stanley-black-decker', 'Stanley Black & Decker, Inc.',          'Stanley Black & Decker',   '549300DJ09SMTO561131', null,        'US', 'household_durables'),
  ('post-holdings',        'Post Holdings, Inc.',                   'Post Holdings',            'JM1I5YUAURL6DC8N1468', null,        'US', 'food'),
  ('laurent-perrier',      'Laurent-Perrier',                       'Groupe Laurent-Perrier',   '96950036OIHAEGNGJ871', '335680096', 'FR', 'wines_spirits'),
  ('marie-brizard',        'Marie Brizard Wine and Spirits',        'Marie Brizard Wine & Spirits', '969500XQM2JOWHKWI437', '380695213', 'FR', 'wines_spirits'),
  ('philips',              'Koninklijke Philips N.V.',              'Philips',                  'H1FJE8H61JGM1JSGM897', null,        'NL', 'tech_electronics'),
  ('delonghi',             'De'' Longhi S.p.A.',                    'De''Longhi',               '8156000E09A52C4F8A38', null,        'IT', 'household_durables'),
  ('abf',                  'Associated British Foods plc',          'Associated British Foods', 'GBQKSY6W7G0OHCQ8OQ72', null,        'GB', 'fmcg_group'),
  ('lindt',                'Chocoladefabriken Lindt & Sprüngli AG', 'Lindt & Sprüngli',         '529900JYJNNOKKAGK736', null,        'CH', 'food'),
  ('electrolux',           'Aktiebolaget Electrolux',               'Electrolux',               '549300Y3HHZB1ZGFPJ93', null,        'SE', 'household_durables')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
