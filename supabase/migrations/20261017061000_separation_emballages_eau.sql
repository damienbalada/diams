-- Décisions 13 et 14 de l'éditeur (17/10/2026) : deux mesures différentes ne sont plus classées
-- ensemble. Chaque pilier garde ses deux indicateurs.
--   Plastique : « recyclables ou réutilisables dès la conception » (PLA_RECYCLABLE, nouveau) et
--               « part de matière recyclée » (PLA_RECYCLED).
--   Eau       : « consommation d'eau » au sens de l'ESRS E3-4 (WAT_INTENSITY) et « prélèvements d'eau »
--               (WAT_WITHDRAWAL_INTENSITY, nouveau).
-- Les preuves sont réparties d'après la mesure que cite leur extrait ; les constats de journal attachés
-- à une preuve la suivent.

insert into indicators (code, dimension_id, name, kind, direction, sector_specific, applies_to_sector_id, weight, unit,
                        methodology, presence_only, jurisdiction, complementary, group_level, disclosure, owner_level)
select 'PLA_RECYCLABLE', dimension_id, 'Emballages recyclables ou réutilisables dès la conception', kind, direction,
       sector_specific, applies_to_sector_id, weight, unit,
       'Part des emballages conçus pour être recyclables, réutilisables (consignés) ou compostables, telle que publiée par l''entreprise (ESRS E5) ; rang entre pairs du secteur. Ne mesure pas la part réellement recyclée.',
       presence_only, jurisdiction, complementary, group_level, disclosure, owner_level
from indicators where code = 'PLA_RECYCLED'
on conflict (code) do nothing;

update indicators
   set name = 'Part de matière recyclée dans les emballages',
       methodology = 'Part de matière recyclée (ou, quand l''entreprise les regroupe, recyclée ou biosourcée) dans les emballages, telle que publiée par l''entreprise (ESRS E5) ; rang entre pairs du secteur. La recyclabilité des emballages est un indicateur distinct (PLA_RECYCLABLE).'
 where code = 'PLA_RECYCLED';

insert into indicators (code, dimension_id, name, kind, direction, sector_specific, applies_to_sector_id, weight, unit,
                        methodology, presence_only, jurisdiction, complementary, group_level, disclosure, owner_level)
select 'WAT_WITHDRAWAL_INTENSITY', dimension_id, 'Intensité de prélèvement d''eau', kind, direction,
       sector_specific, applies_to_sector_id, weight, unit,
       'Prélèvements d''eau rapportés au chiffre d''affaires (m³ par million d''euros), tels que publiés par l''entreprise ; rang entre pairs du secteur. Distinct de la consommation d''eau (WAT_INTENSITY) : l''eau prélevée inclut celle qui est rendue au milieu.',
       presence_only, jurisdiction, complementary, group_level, disclosure, owner_level
from indicators where code = 'WAT_INTENSITY'
on conflict (code) do nothing;

update indicators
   set name = 'Intensité de consommation d''eau',
       methodology = 'Consommation d''eau rapportée au chiffre d''affaires (ESRS E3-4 § 29 : m³ par million d''euros), normalisée face aux pairs du secteur. Les prélèvements sont un indicateur distinct (WAT_WITHDRAWAL_INTENSITY).'
 where code = 'WAT_INTENSITY';

-- Copie des secteurs et des régimes éventuels (aucun aujourd'hui : indicateurs transversaux).
insert into indicator_sectors (indicator_id, sector_id)
select n.id, s.sector_id from indicator_sectors s join indicators o on o.id = s.indicator_id
join indicators n on (o.code, n.code) in (('PLA_RECYCLED', 'PLA_RECYCLABLE'), ('WAT_INTENSITY', 'WAT_WITHDRAWAL_INTENSITY'))
on conflict do nothing;

-- Répartition des preuves.
with deplace as (
  update evidence v set indicator_id = (select id from indicators where code = 'PLA_RECYCLABLE')
  from entities e
  where e.id = v.entity_id
    and v.indicator_id = (select id from indicators where code = 'PLA_RECYCLED')
    and e.slug in ('ab-inbev', 'arla', 'bonduelle', 'campari', 'carlsberg', 'carrefour', 'coca-cola', 'danone',
                   'ferrero', 'greenyard', 'haleon', 'interparfums', 'kering', 'lotus-bakeries',
                   'magnum-ice-cream-company', 'mars', 'mondelez', 'nestle', 'pepsico', 'pernod-ricard',
                   'procter-gamble', 'unilever')
  returning v.id, v.indicator_id
)
update indicator_reviews r set indicator_id = d.indicator_id from deplace d where r.evidence_id = d.id;

with deplace as (
  update evidence v set indicator_id = (select id from indicators where code = 'WAT_WITHDRAWAL_INTENSITY')
  from entities e
  where e.id = v.entity_id
    and v.indicator_id = (select id from indicators where code = 'WAT_INTENSITY')
    and e.slug in ('bonduelle', 'danone')
  returning v.id, v.indicator_id
)
update indicator_reviews r set indicator_id = d.indicator_id from deplace d where r.evidence_id = d.id;
