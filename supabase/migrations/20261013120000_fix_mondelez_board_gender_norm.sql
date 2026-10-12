-- =============================================================================
-- Mixité du conseil de Mondelez (lot 33) : note normalisée corrigée
-- -----------------------------------------------------------------------------
-- La mixité se normalise par rapport à la parité (part / 50, plafonnée à 1) :
-- 40 % de femmes = 0,8, et non 0,4 (saisie erronée). verify_curated contrôle
-- désormais cette normalisation.
-- =============================================================================

update evidence e set normalized_value = 0.8
from entities en, indicators i, sources s
where en.id = e.entity_id and i.id = e.indicator_id and s.id = e.source_id
  and en.slug = 'mondelez' and i.code = 'GOV_BOARD_GENDER' and s.code = 'SEC_FILING'
  and e.observed_on = date '2026-04-03' and e.value_numeric = 40;
