-- Groupes cotés aux États-Unis dont des marques sont vendues en hypermarché en
-- France : petit électroménager et aquariophilie (Spectrum Brands), jeans (Kontoor),
-- lubrifiant WD-40, shampoing sec Batiste (Church & Dwight), surgelés Findus (Nomad
-- Foods, rapport annuel 20-F). LEI vérifiés dans le registre GLEIF le 13/10/2026.
insert into entities (slug, legal_name, display_name, lei, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.country, s.id, false
from (values
  ('spectrum-brands', 'Spectrum Brands Holdings, Inc.', 'Spectrum Brands', '549300JM0MJETDD30O20', 'US', 'household_durables'),
  ('kontoor',         'Kontoor Brands, Inc.',           'Kontoor Brands',  '549300M0CPXV65RFF271', 'US', 'fashion_leather'),
  ('wd-40',           'WD-40 Company',                  'WD-40 Company',   '549300UZHTN0CNKBOB19', 'US', 'home_care'),
  ('church-dwight',   'Church & Dwight Co., Inc.',      'Church & Dwight', 'POOXSI30AWAQGYJZC921', 'US', 'personal_care'),
  ('nomad-foods',     'Nomad Foods Limited',            'Nomad Foods',     '5493000ZZ1837DS2SI43', 'VG', 'food')
) as v(slug, legal_name, display_name, lei, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
