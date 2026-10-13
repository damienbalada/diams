-- Troisième série : fabricants de marques nationales de grande surface identifiés
-- par les mentions légales ou le site officiel de leurs marques. SIREN vérifiés dans
-- l'annuaire officiel des entreprises et LEI dans le registre GLEIF le 13/10/2026.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('carambar-co', 'Carambar and Co.',                       'Carambar & Co',       '969500PE8PLNOU6LI824', '824239214', 'FR', 'food'),
  ('cofigeo',     'Cofigeo',                                'Cofigeo',             '969500YD7U79QGVQNE56', '542076633', 'FR', 'food'),
  ('panzani',     'Panzani',                                'Panzani (société)',   '969500QKSZNHA1VNR784', '961503422', 'FR', 'food'),
  ('herta',       'Herta',                                  'Herta (société)',     null,                   '311043194', 'FR', 'food'),
  ('st-michel',   'St Michel Biscuits',                     'St Michel Biscuits',  '969500929RHP8FBQR419', '421019951', 'FR', 'food'),
  ('dr-oetker',   'Dr. August Oetker Nahrungsmittel KG',    'Dr. Oetker',          '529900PVV369S53P2L20', null,        'DE', 'food'),
  ('alsa-france', 'Alsa France',                            'Alsa France',         null,                   '501551451', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
