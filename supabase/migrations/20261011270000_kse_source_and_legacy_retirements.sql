-- =============================================================================
-- Russie : base KSE « Leave Russia » ; retrait de lignes anciennes sans valeur probante
-- -----------------------------------------------------------------------------
-- 1. Source KSE_LEAVE_RUSSIA (Kyiv School of Economics). La liste complète des
--    entreprises suivies est chargée par import_kse : une entreprise absente
--    n'était pas présente en Russie ou n'a pas été suivie. GEO_RUSSIA_EXIT
--    devient complémentaire (benchmark à périmètre fermé, comme KnowTheChain).
--    La liste Yale, publiée en images et sans données téléchargeables, n'est
--    plus utilisée : ses 52 lignes saisies à la main sont retirées par
--    import_kse au profit des statuts KSE.
--
-- 2. Lignes saisies à la main (curation-v1) retirées car elles ne disent rien de
--    la conduite de l'entreprise, ou sont rangées sous le mauvais indicateur :
--    - GEO_POL_FINANCING / LEGIFRANCE (19) : « financement politique des
--      entreprises interdit en France » — c'est la loi, pas un fait sur
--      l'entreprise ; il valait 0,5 et gonflait la fiabilité ;
--    - ENV_CDP_CLIMATE / RECLAIM_FINANCE (3) : critiques de Reclaim Finance
--      (nouveaux projets fossiles) rangées sous la note CDP, qu'elles ne sont
--      pas ; l'expansion fossile sera mesurée par une source dédiée (GOGEL) ;
--    - ENV_SBTI_VALIDATED / NEW_CLIMATE (2) : évaluation du NewClimate
--      Institute rangée sous la validation SBTi, qu'elle n'est pas.
-- =============================================================================

insert into sources (code, name, tier, publisher, url, description) values
  ('KSE_LEAVE_RUSSIA', 'KSE Institute — Leave Russia', 'audited_ngo', 'Kyiv School of Economics',
   'https://leave-russia.org/',
   'Base de plus de 4 000 entreprises étrangères présentes en Russie en 2022 : statut tenu à jour (activité poursuivie, réduite, suspendue, sortie annoncée ou effective) et source de chaque décision.')
on conflict (code) do nothing;

update indicators set complementary = true where code = 'GEO_RUSSIA_EXIT';

update evidence e set review_status = 'rejected', reviewer = 'retire:loi-pas-un-fait-2026-10-11'
from indicators i, sources s
where e.indicator_id = i.id and e.source_id = s.id
  and e.reviewer = 'curation-v1' and e.review_status = 'approved'
  and i.code = 'GEO_POL_FINANCING' and s.code = 'LEGIFRANCE';

update evidence e set review_status = 'rejected', reviewer = 'retire:mauvais-indicateur-2026-10-11'
from indicators i, sources s
where e.indicator_id = i.id and e.source_id = s.id
  and e.reviewer = 'curation-v1' and e.review_status = 'approved'
  and ((i.code = 'ENV_CDP_CLIMATE' and s.code = 'RECLAIM_FINANCE')
    or (i.code = 'ENV_SBTI_VALIDATED' and s.code = 'NEW_CLIMATE'));
