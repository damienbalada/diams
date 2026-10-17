-- Lot 210 : propriétaires de marques non alimentaires vendues en grande surface, absentes de l'Index
-- (relevé des scans non reconnus et comparaison avec Open Products Facts, 17/10/2026).
--  - STABILO International GmbH (Heroldsberg), éditrice du site stabilo.com, « Ein Unternehmen der
--    Gruppe Schwan-STABILO » ; LEI vérifié dans le registre GLEIF le 17/10/2026
--    (8945002AZLB148E16C91, entité active).
--  - Hamelin SAS (Caen), groupe des marques Oxford, Pelikan, Herlitz, Elba, scribzee et Unilux ;
--    SIREN vérifié dans l'annuaire officiel des entreprises le 17/10/2026 (552132961, active, APE 17.23Z).
--  - VARTA AG (Ellwangen) ; LEI vérifié dans GLEIF le 17/10/2026 (529900E7KB95KOXBWP63, active).
--  - Opinel SAS (Chambéry), éditrice d'opinel.com ; SIREN vérifié le 17/10/2026 (745821025, active,
--    APE 25.71Z).
--  - Arc France (Arques), marques Luminarc et Cristal d'Arques Paris ; SIREN vérifié le 17/10/2026
--    (504313032, active, APE 23.13Z).
insert into entities (slug, legal_name, display_name, lei, siren, country, sector_id, is_brand)
select v.slug, v.legal_name, v.display_name, v.lei, v.siren, v.country, s.id, false
from (values
  ('stabilo-international', 'STABILO International GmbH', 'STABILO International (groupe Schwan-STABILO)', '8945002AZLB148E16C91', null, 'DE', 'household_durables'),
  ('hamelin', 'HAMELIN SAS', 'Hamelin', null, '552132961', 'FR', 'household_durables'),
  ('varta-ag', 'VARTA Aktiengesellschaft', 'VARTA AG', '529900E7KB95KOXBWP63', null, 'DE', 'household_durables'),
  ('opinel-sas', 'OPINEL SAS', 'Opinel (société)', null, '745821025', 'FR', 'household_durables'),
  ('arc-france', 'ARC FRANCE', 'Arc France', null, '504313032', 'FR', 'household_durables')
) as v(slug, legal_name, display_name, lei, siren, country, sector)
join sectors s on s.code = v.sector
on conflict (slug) do nothing;
