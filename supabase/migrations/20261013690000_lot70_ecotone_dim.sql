-- Ecotone France (SIREN 343 173 647), éditrice du site français d'Ecotone qui présente sa
-- « famille de marques » (Bjorg, Clipper, Bonneterre, Alter Eco, Danival…), et DIM France
-- SAS (SIREN 488 727 298), éditrice du site de Dim. SIREN vérifiés dans l'annuaire
-- officiel des entreprises le 13/10/2026. Bjorg reste rattachée à Bjorg et Compagnie,
-- la société qui édite son site : aucun document lu ne relie cette société à Ecotone France.
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('ecotone-france', 'Ecotone France', 'Ecotone France', null, '343173647', 'FR', 'food'),
  ('dim-france', 'DIM France SAS', 'DIM France', null, '488727298', 'FR', 'fashion_leather')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
