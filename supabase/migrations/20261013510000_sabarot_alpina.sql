-- Fabricants français de légumes secs, céréales et pâtes vendus en hypermarché,
-- identifiés par les mentions légales de leurs sites officiels ; SIREN et LEI vérifiés
-- dans l'annuaire officiel des entreprises et le registre GLEIF le 13/10/2026.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('sabarot-wassner', 'Sabarot Wassner', 'Sabarot Wassner', '969500TDT8HED5NDSC55', '585750813', 'FR', 'food'),
  ('alpina-savoie', 'Alpina Savoie', 'Alpina Savoie (société)', '969500DE5GV8FT8QZN56', '745721134', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
