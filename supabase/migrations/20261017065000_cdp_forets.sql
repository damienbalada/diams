-- Déforestation (17/10/2026), première brique en attendant l'application du règlement européen
-- (UE) 2023/1115, reportée par le règlement (UE) 2025/2650 au 30/12/2026 pour les grandes et moyennes
-- entreprises et au 30/06/2027 pour les petites : la note publique du questionnaire « forêts » du CDP
-- (soja, bœuf et cuir, cacao, huile de palme, café, caoutchouc, bois). Le CDP ne l'adresse qu'aux
-- entreprises exposées à ces matières : « F » signifie sollicitée sans réponse. Secteurs concernés : liste
-- indicator_sectors (comme la taxonomie).
insert into indicators (code, dimension_id, name, kind, direction, sector_specific, weight, unit, methodology, group_level, complementary)
select 'ENV_CDP_FORESTS', d.id, 'Déforestation : note forêts du CDP', 'ordinal', 'higher_better', false, 1, 'grade',
       'Note publique du questionnaire forêts du CDP (A à D-, F = sollicitée sans réponse), mappée sur [0,1] comme les notes climat et eau. Couvre les matières à risque de déforestation visées par le règlement (UE) 2023/1115 : soja, bovins et cuir, cacao, huile de palme, café, caoutchouc, bois.',
       true, true
from dimensions d where d.code = 'ENV'
on conflict (code) do nothing;
insert into indicator_sectors (indicator_id, sector_id)
select i.id, s.id from indicators i cross join sectors s
where i.code = 'ENV_CDP_FORESTS'
  and s.code in ('food', 'restaurant', 'retail_distribution', 'fmcg_group', 'pet_care', 'fashion_leather', 'luxury_group',
                 'beauty_fragrance', 'personal_care', 'home_care', 'household_durables', 'automotive', 'wines_spirits', 'beverages')
on conflict do nothing;
