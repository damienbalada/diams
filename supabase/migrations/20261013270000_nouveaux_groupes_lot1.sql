-- Nouveaux groupes de grande consommation présents dans les hypermarchés français.
-- Chaque LEI a été vérifié dans le registre mondial GLEIF (entité active, LEI émis)
-- le 13/10/2026 ; le nom légal est celui du registre.
--   Carlsberg A/S                    5299001O0WJQYB5GYZ19  (DK)
--   Diageo plc                       213800ZVIELEA55JMJ32  (GB)
--   Reckitt Benckiser Group plc      5493003JFSMOJG48V108  (GB)
--   Rémy Cointreau                   5493004V6A3Z027YT216  (FR)
--   Davide Campari-Milano N.V.       213800ED5AN2J56N6Z02  (siège légal IT, droit NL)
--   Lotus Bakeries                   5493004C0K34IFI67I03  (BE)
--   Essity Aktiebolag (publ)         549300G8E6YUVJ1DA153  (SE)
--   Ebro Foods, S.A.                 959800NW6DLQT89M3240  (ES)
--   General Mills, Inc.              2TGYMUGI08PO8X8L6150  (US)
--   McCormick & Company, Inc.        549300JQQA6MQ4OJP259  (US)
--   Kimberly-Clark Corporation       MP3J6QPYPGN75NVW2S34  (US)
insert into entities (slug, legal_name, display_name, lei, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.country, s.id, false
from (values
  ('carlsberg',       'Carlsberg A/S',                           'Carlsberg',        '5299001O0WJQYB5GYZ19', 'DK', 'wines_spirits'),
  ('diageo',          'Diageo plc',                              'Diageo',           '213800ZVIELEA55JMJ32', 'GB', 'wines_spirits'),
  ('reckitt',         'Reckitt Benckiser Group plc',             'Reckitt',          '5493003JFSMOJG48V108', 'GB', 'fmcg_group'),
  ('remy-cointreau',  'Rémy Cointreau',                          'Rémy Cointreau',   '5493004V6A3Z027YT216', 'FR', 'wines_spirits'),
  ('campari',         'Davide Campari-Milano N.V.',              'Campari Group',    '213800ED5AN2J56N6Z02', 'IT', 'wines_spirits'),
  ('lotus-bakeries',  'Lotus Bakeries',                          'Lotus Bakeries',   '5493004C0K34IFI67I03', 'BE', 'food'),
  ('essity',          'Essity Aktiebolag (publ)',                'Essity',           '549300G8E6YUVJ1DA153', 'SE', 'personal_care'),
  ('ebro-foods',      'Ebro Foods, S.A.',                        'Ebro Foods',       '959800NW6DLQT89M3240', 'ES', 'food'),
  ('general-mills',   'General Mills, Inc.',                     'General Mills',    '2TGYMUGI08PO8X8L6150', 'US', 'fmcg_group'),
  ('mccormick',       'McCormick & Company, Incorporated',       'McCormick',        '549300JQQA6MQ4OJP259', 'US', 'food'),
  ('kimberly-clark',  'Kimberly-Clark Corporation',              'Kimberly-Clark',   'MP3J6QPYPGN75NVW2S34', 'US', 'personal_care')
) as v(slug, legal_name, display_name, lei, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
