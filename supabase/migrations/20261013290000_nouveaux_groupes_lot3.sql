-- Groupes de beauté et laitiers présents dans les hypermarchés français. LEI vérifiés
-- dans le registre GLEIF (entité active, LEI émis) le 13/10/2026.
--   Arla Foods amba        529900IJ6T4P1O10R377  (DK, coopérative ; rapport annuel ESEF)
--   Puig Brands, S.A.      549300OVHNSX30L1AQ94  (ES)
--   Interparfums           969500SARWF33OPQED48  (FR, SIREN 350219382)
--   Coty Inc.              549300BO9IWPF3S48F93  (US)
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('arla',         'Arla Foods amba',   'Arla Foods',   '529900IJ6T4P1O10R377', null,        'DK', 'food'),
  ('puig',         'Puig Brands, S.A.', 'Puig',         '549300OVHNSX30L1AQ94', null,        'ES', 'beauty_fragrance'),
  ('interparfums', 'Interparfums',      'Interparfums', '969500SARWF33OPQED48', '350219382', 'FR', 'beauty_fragrance'),
  ('coty',         'Coty Inc.',         'Coty',         '549300BO9IWPF3S48F93', null,        'US', 'beauty_fragrance')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
