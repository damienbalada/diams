-- Groupes non cotés en France (ou cotés hors UE) dont les marques sont vendues en
-- hypermarché : thon, confiserie, beurre, dermo-cosmétique, essuie-tout, jus de
-- fruits, frites surgelées, saumon fumé. LEI vérifiés dans le registre GLEIF le
-- 13/10/2026 (entité active) ; SIREN dans l'annuaire officiel des entreprises.
--   Thai Union Group Public Company Limited   25490047VDGNFMEYZW95  (TH)
--   Perfetti Van Melle Group B.V.             875500PFUPGWRD0APL65  (NL)
--   Laïta                                     969500V6B10Q5VDTBT43  (FR, SIREN 380656439)
--   Pierre Fabre SA                           969500JTOO1CD097BI59  (FR, SIREN 662006170)
--   Sofidel S.p.A.                            8156004E70AB6119D319  (IT)
--   Eckes-Granini Group GmbH                  529900RQDBRLSIV59E72  (DE)
--   McCain Foods Limited                      549300JY1SNI78TP4048  (CA)
--   Labeyrie Fine Foods                       9695006DAQ2QM2EZ8H43  (FR, SIREN 414816967)
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('thai-union',         'Thai Union Group Public Company Limited', 'Thai Union',          '25490047VDGNFMEYZW95', null,        'TH', 'food'),
  ('perfetti-van-melle', 'Perfetti Van Melle Group B.V.',           'Perfetti Van Melle',  '875500PFUPGWRD0APL65', null,        'NL', 'food'),
  ('laita',              'Laïta',                                   'Laïta',               '969500V6B10Q5VDTBT43', '380656439', 'FR', 'food'),
  ('pierre-fabre',       'Pierre Fabre SA',                         'Pierre Fabre',        '969500JTOO1CD097BI59', '662006170', 'FR', 'personal_care'),
  ('sofidel',            'Sofidel S.p.A.',                          'Sofidel',             '8156004E70AB6119D319', null,        'IT', 'home_care'),
  ('eckes-granini',      'Eckes-Granini Group GmbH',                'Eckes-Granini',       '529900RQDBRLSIV59E72', null,        'DE', 'beverages'),
  ('mccain',             'McCain Foods Limited',                    'McCain Foods',        '549300JY1SNI78TP4048', null,        'CA', 'food'),
  ('labeyrie',           'Labeyrie Fine Foods',                     'Labeyrie Fine Foods', '9695006DAQ2QM2EZ8H43', '414816967', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
