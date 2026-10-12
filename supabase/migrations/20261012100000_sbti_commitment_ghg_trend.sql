-- =============================================================================
-- Un objectif n'est pas un résultat ; la baisse réelle des émissions en est un
-- (décisions de l'éditeur du 12/10/2026, v0.7.1)
-- -----------------------------------------------------------------------------
-- 1. Objectifs climat validés par la SBTi : un objectif, même validé, est une
--    promesse sur l'avenir. Ces preuves passent de « résultat » à « engagement »
--    (Règle 3 : multiplicateur 0,4, plafond 0,5). S'engager à fixer un objectif
--    vaut moitié moins qu'un objectif validé (1,0 → 0,5). Un engagement retiré
--    reste un fait (0).
--    Exemple : Shein, dont les émissions augmentent, avait 100 sur
--    l'environnement grâce à son seul objectif validé.
-- 2. Nouvel indicateur ENV_GHG_TREND : évolution réelle des émissions totales
--    (scopes 1, 2 et 3) publiées par l'entreprise, en rythme annuel moyen entre
--    l'année de référence et la dernière année publiée :
--      r = (E_dernière / E_référence)^(1/années) − 1
--    note = 1 si r ≤ −4,2 % par an (trajectoire 1,5 °C de la SBTi, réduction
--    linéaire absolue), 0 si les émissions ne baissent pas (r ≥ 0), linéaire
--    entre les deux. Poids 1,5 : c'est le résultat du pilier climat.
--    Indicateur de groupe et complémentaire (compte s'il est publié).
-- =============================================================================

-- 1. Objectifs validés : engagements
update evidence e set nature = 'commitment'
from indicators i
where i.id = e.indicator_id and i.code = 'ENV_SBTI_VALIDATED'
  and e.nature = 'result' and coalesce(e.normalized_value, 0) > 0;

update evidence e set normalized_value = 0.5
from indicators i
where i.id = e.indicator_id and i.code = 'ENV_SBTI_VALIDATED'
  and e.nature = 'commitment' and e.normalized_value = 1
  and e.value_text ilike '%commit%';

update indicators set methodology =
  'Objectif de court terme SBTi. Validé 1,5 °C = 1 ; validé (autre) = 0,6 ; engagement à fixer un objectif = 0,5 ; tous traités comme des engagements (Règle 3 : ×0,4, plafond 0,5). Engagement retiré = 0 (fait).'
where code = 'ENV_SBTI_VALIDATED';

-- 2. Évolution réelle des émissions
insert into indicators (code, dimension_id, name, kind, direction, sector_specific, applies_to_sector_id, weight, unit,
                        methodology, presence_only, jurisdiction, complementary, group_level, disclosure)
select 'ENV_GHG_TREND', d.id, 'Évolution réelle des émissions (scopes 1, 2 et 3)', 'quantitative', 'lower_better',
       false, null, 1.5, '%/an',
       'Rythme annuel moyen d''évolution des émissions totales publiées (scopes 1+2+3) entre l''année de référence et la dernière année : 1 si baisse de 4,2 % par an ou plus (trajectoire 1,5 °C SBTi), 0 si les émissions ne baissent pas, linéaire entre les deux.',
       false, null, true, true, false
from dimensions d where d.code = 'ENV'
on conflict (code) do nothing;
