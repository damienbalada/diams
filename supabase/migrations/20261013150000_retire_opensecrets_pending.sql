-- =============================================================================
-- Lobbying et financement politique aux États-Unis : lignes en attente retirées
-- -----------------------------------------------------------------------------
-- Montants recopiés d'OpenSecrets ou de la presse, sans citation. La source
-- officielle (déclarations de lobbying du Sénat, désormais lda.gov) refuse l'accès
-- aux programmes depuis l'Europe, et OpenSecrets les bloque : rien n'est
-- vérifiable mot pour mot. Indicateurs de contexte (ils n'entrent pas dans la
-- note) : aucun effet sur les notes.
-- =============================================================================

update evidence e set review_status = 'rejected', reviewer = 'retire:source-officielle-inaccessible-2026-10-13'
from sources s, indicators i
where s.id = e.source_id and i.id = e.indicator_id and e.review_status = 'pending'
  and s.code = 'OPENSECRETS' and i.code in ('GEO_LOBBYING_SPEND', 'GEO_POL_FINANCING');
