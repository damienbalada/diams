-- =============================================================================
-- Textes affichés cohérents avec v0.7.1
-- -----------------------------------------------------------------------------
-- 1. Les extraits des objectifs SBTi, écrits à l'import, disaient « (résultat
--    validé) » : depuis v0.7.1, un objectif validé est un engagement. La fiche
--    affichait donc une contradiction. Le texte suit la règle.
-- 2. GEO_RUSSIA_EXIT s'appelait « Position Russie (liste Yale) » alors que la
--    donnée vient de la liste complète du KSE Institute.
-- =============================================================================

update evidence e set excerpt = replace(e.excerpt, '(résultat validé).',
                                        '(objectif validé par la SBTi : un engagement sur l''avenir, pas un résultat).')
from indicators i
where i.id = e.indicator_id and i.code = 'ENV_SBTI_VALIDATED' and e.excerpt like '%(résultat validé).%';

update evidence e set excerpt = replace(e.excerpt, '(engagement non encore validé).',
                                        '(engagement à fixer un objectif, non encore validé).')
from indicators i
where i.id = e.indicator_id and i.code = 'ENV_SBTI_VALIDATED' and e.excerpt like '%(engagement non encore validé).%';

update indicators set name = 'Sortie de Russie (depuis l''invasion de l''Ukraine)' where code = 'GEO_RUSSIA_EXIT';
