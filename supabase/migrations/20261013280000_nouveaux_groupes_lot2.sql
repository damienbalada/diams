-- Groupes français cotés présents dans les hypermarchés. LEI vérifiés dans le
-- registre GLEIF (entité active, LEI émis) et SIREN lu dans le même registre
-- (champ « registeredAs »), le 13/10/2026.
--   Savencia SA        5299006UH636V4UOZS07  SIREN 847120185
--   Société L.D.C.     969500W6740M4US9ES57  SIREN 576850697
--   SEB SA             969500WP61NBK098AC47  SIREN 300349636
--   Société BIC        969500UR00DF63I0VH67  SIREN 552008443
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, 'FR', s.id, false
from (values
  ('savencia', 'Savencia SA',    'Savencia',   '5299006UH636V4UOZS07', '847120185', 'food'),
  ('ldc',      'Société L.D.C.', 'Groupe LDC', '969500W6740M4US9ES57', '576850697', 'food'),
  ('seb',      'SEB SA',         'Groupe SEB', '969500WP61NBK098AC47', '300349636', 'tech_electronics'),
  ('bic',      'Société BIC',    'BIC',        '969500UR00DF63I0VH67', '552008443', 'fmcg_group')
) as v(slug, legal_name, display_name, lei, siren, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
