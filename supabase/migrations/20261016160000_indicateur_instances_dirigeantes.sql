-- =============================================================================
-- Femmes dans les instances dirigeantes (loi Rixain) — décision de l'éditeur du 16/10/2026
-- -----------------------------------------------------------------------------
-- Indicateur distinct de la mixité du conseil (GOV_BOARD_GENDER) : les « instances
-- dirigeantes » sont le comité exécutif ou de direction, pas le conseil d'administration.
-- Source : déclarations publiques de la représentation équilibrée sur le site Égapro du
-- ministère du Travail (export public), par SIREN. La valeur est la part de femmes parmi les
-- membres des instances dirigeantes ; la part parmi les cadres dirigeants est citée à côté.
-- Comme l'index Égapro, l'obligation pèse sur chaque société employeuse (owner_level) et sur
-- les seules sociétés françaises (jurisdiction FR) : une filiale française déclare pour
-- elle-même, pas pour son groupe étranger.
-- =============================================================================
insert into indicators (code, dimension_id, name, kind, direction, sector_specific, applies_to_sector_id, weight, unit,
                        methodology, presence_only, jurisdiction, complementary, group_level, owner_level, disclosure)
select 'GOV_EXEC_GENDER', d.id, 'Femmes dans les instances dirigeantes (loi Rixain)', 'quantitative', 'higher_better',
       false, null, 0.7, '%',
       'Part de femmes parmi les membres des instances dirigeantes (comité exécutif ou de direction), déclarée chaque année au ministère du Travail par les entreprises d''au moins 1 000 salariés (loi Rixain). Distinct de la mixité du conseil d''administration.',
       false, 'FR', false, false, true, false
from dimensions d where d.code = 'GOV'
on conflict (code) do nothing;

insert into disclosure_regimes (code, name, jurisdiction, legal_basis, scope, url, in_force_since) values
  ('FR_RIXAIN', 'Représentation équilibrée des femmes et des hommes parmi les cadres dirigeants et les instances dirigeantes', 'FR',
   'Loi n° 2021-1774 du 24 décembre 2021 (loi Rixain), art. 14 ; Code du travail, art. L1142-11 à L1142-13',
   'Entreprises qui emploient au moins 1 000 salariés pour le troisième exercice consécutif : calcul et publication chaque année, au plus tard le 1er mars, des écarts de représentation parmi les cadres dirigeants et les membres des instances dirigeantes ; objectif de 30 % de chaque sexe à compter du 1er mars 2026, de 40 % à compter du 1er mars 2029.',
   'https://egapro.travail.gouv.fr/representation-equilibree', '2022-03-01')
on conflict (code) do nothing;

insert into indicator_regimes (indicator_id, regime_id, note)
select i.id, r.id, 'Part de femmes parmi les membres des instances dirigeantes.'
from indicators i, disclosure_regimes r
where i.code = 'GOV_EXEC_GENDER' and r.code = 'FR_RIXAIN'
on conflict do nothing;
