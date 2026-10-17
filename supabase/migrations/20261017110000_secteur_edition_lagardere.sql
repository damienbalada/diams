-- Secteur « Édition » (décision de l'éditeur du 17/10/2026) : livres vendus en grande surface,
-- jusqu'ici hors de l'Index faute de secteur. Pas d'enjeu animal, plastique ni eau propre au métier
-- d'éditeur ; s'appliquent l'évolution réelle des émissions (comme pour tous les secteurs) et la note
-- forêts du CDP (le bois et le papier sont des matières visées par le règlement (UE) 2023/1115).
insert into sectors (code, name, description, animal_relevant, plastic_relevant, water_relevant)
values ('publishing', 'Édition', 'Livres, édition scolaire et parascolaire, dictionnaires.', false, false, false)
on conflict (code) do nothing;

insert into indicator_sectors (indicator_id, sector_id)
select i.id, s.id from indicators i cross join sectors s
where i.code in ('ENV_GHG_TREND', 'ENV_CDP_FORESTS') and s.code = 'publishing'
on conflict do nothing;

-- Lagardère SA (Paris), maison mère de Lagardère Publishing (Hachette Livre) ; LEI vérifié dans GLEIF
-- le 17/10/2026 (969500VX2NV2AQQ65G45, actif, SIREN 320366446) et SIREN dans l'annuaire officiel des
-- entreprises (actif, APE 70.10Z).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select 'lagardere', 'LAGARDERE SA', 'Lagardère', '969500VX2NV2AQQ65G45', '320366446', 'FR', s.id, false
from sectors s where s.code = 'publishing'
on conflict (slug) do nothing;
