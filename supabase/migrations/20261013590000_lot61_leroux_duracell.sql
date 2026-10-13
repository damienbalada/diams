-- Leroux (chicorée) : société Leroux, nom d'usage Chicorée Leroux, SIREN 045 750 817 et
-- LEI vérifiés le 13/10/2026. Duracell : The Duracell Company (États-Unis), exploitante
-- des sites de la marque selon leurs conditions d'utilisation ; pas de LEI trouvé.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('leroux', 'Leroux', 'Chicorée Leroux (société Leroux)', '969500P3AGNM1M2NZD46', '045750817', 'FR', 'food'),
  ('duracell', 'The Duracell Company', 'The Duracell Company', null, null, 'US', 'household_durables')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
