-- Lot 95 : Biscuiterie La Mère Poulard, éditrice du site officiel des biscuits La Mère Poulard
-- (mentions légales mises à jour le 01/09/2026, après la cession de la biscuiterie) ; SIREN
-- vérifié dans l'annuaire officiel des entreprises le 14/10/2026 (actif).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('biscuiterie-la-mere-poulard', 'BISCUITERIE LA MERE POULARD', 'Biscuiterie La Mère Poulard', null, '423919299', 'FR', 'food')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
