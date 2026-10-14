-- =============================================================================
-- Relecture complète, vague 0 (PLAN_REFONTE.md) : corrections issues des sources relues
-- -----------------------------------------------------------------------------
-- 1. SBTi, export officiel « companies-excel.xlsx » (mis à jour le 08/10/2026) : trois
--    statuts ont changé depuis l'export du 31/07/2026 qui avait servi le 14/10. La preuve du
--    14/10 est corrigée avec ce que produit le connecteur (import_sbti.build_rows) sur le
--    nouvel export : Ecotone et Pilot ont désormais un objectif validé (1,5 °C) ; Alsace
--    Lait a retiré son engagement.
-- 2. Registre de transparence de l'UE, export du 14/10/2026 : Kellanova n'y figure plus.
--    Ses deux preuves (inscription, dépenses) sont retirées (remplace:relecture).
-- =============================================================================

update evidence e set
  value_text = 'Commitment Removed', normalized_value = 0.0, nature = 'result',
  excerpt = 'SBTi, export « Companies taking action » (consulté le 14/10/2026) : « Alsace Lait » — objectif de court terme : engagement retiré (engagement retiré).',
  reviewer = 'auto:import_sbti', updated_at = now()
from entities en, indicators i, sources s
where e.entity_id = en.id and e.indicator_id = i.id and e.source_id = s.id
  and en.slug = 'alsace-lait' and i.code = 'ENV_SBTI_VALIDATED' and s.code = 'SBTI' and e.observed_on = '2026-10-14';

update evidence e set
  value_text = 'Validated Targets', normalized_value = 1.0, nature = 'commitment',
  excerpt = 'SBTi, export « Companies taking action » (consulté le 14/10/2026) : « ECOTONE » — objectif de court terme validé (1,5 °C) (objectif validé par la SBTi : un engagement sur l''avenir, pas un résultat).',
  reviewer = 'auto:import_sbti', updated_at = now()
from entities en, indicators i, sources s
where e.entity_id = en.id and e.indicator_id = i.id and e.source_id = s.id
  and en.slug = 'ecotone-france' and i.code = 'ENV_SBTI_VALIDATED' and s.code = 'SBTI' and e.observed_on = '2026-10-14';

update evidence e set
  value_text = 'Validated Targets', normalized_value = 1.0, nature = 'commitment',
  excerpt = 'SBTi, export « Companies taking action » (consulté le 14/10/2026) : « Pilot Corporation of Europe » — objectif de court terme validé (1,5 °C) (objectif validé par la SBTi : un engagement sur l''avenir, pas un résultat).',
  reviewer = 'auto:import_sbti', updated_at = now()
from entities en, indicators i, sources s
where e.entity_id = en.id and e.indicator_id = i.id and e.source_id = s.id
  and en.slug = 'pilot-corporation-of-europe' and i.code = 'ENV_SBTI_VALIDATED' and s.code = 'SBTI' and e.observed_on = '2026-10-14';

update evidence e set review_status = 'rejected', reviewer = 'remplace:relecture', updated_at = now()
from entities en, indicators i, sources s
where e.entity_id = en.id and e.indicator_id = i.id and e.source_id = s.id
  and en.slug = 'kellanova' and i.code in ('GEO_LOBBYING_TRANSP', 'GEO_LOBBYING_SPEND') and s.code = 'EU_TRANSPARENCY'
  and e.review_status = 'approved';
