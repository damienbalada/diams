-- Fabricants français de viennoiseries et d'apéritifs vendus en hypermarché,
-- identifiés par les mentions légales des sites de leurs marques ; SIREN vérifiés dans
-- l'annuaire officiel des entreprises le 13/10/2026. La société Menguy's (RCS Toulouse
-- 333 821 692) porte aujourd'hui la dénomination France Snacking Apéritif.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('la-boulangere-et-co', 'La Boulangère & Co', 'La Boulangère & Co', null, '429081565', 'FR', 'food'),
  ('france-snacking-aperitif', 'France Snacking Apéritif', 'France Snacking Apéritif (Menguy''s)', null, '333821692', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
