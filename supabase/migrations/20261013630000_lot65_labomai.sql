-- Activilong : le site de la marque est « édité par la société LABOMAI […] immatriculée au
-- RCS de Meaux, sous le N° 327 235 818 ». Dans l'annuaire officiel des entreprises, ce
-- SIREN est celui de Miss Antilles International (sigle MAI), Saint-Soupplets, fabrication
-- de savons et produits d'entretien et de toilette (vérifié le 13/10/2026).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select 'labomai', 'Miss Antilles International', 'Labomai (Miss Antilles International)', null, '327235818', 'FR', s.id, false
from sectors s where s.code = 'personal_care'
on conflict (slug) do nothing;
