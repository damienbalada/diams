-- =============================================================================
-- Correctif : devise des extraits « taux effectif d'impôt » (ESEF)
-- -----------------------------------------------------------------------------
-- Le connecteur import_esef libellait toujours les montants en M€. AB InBev et
-- Shell présentent leurs comptes en dollars (unité iso4217:USD des faits IFRS
-- balisés) : les montants étaient justes, l'unité affichée non. Le taux, sans
-- unité, est inchangé. Le connecteur lit désormais la devise balisée.
-- =============================================================================

update evidence e
set excerpt = replace(e.excerpt, ' M€', ' M$')
from entities en, indicators i, sources s
where en.id = e.entity_id and i.id = e.indicator_id and s.id = e.source_id
  and en.slug in ('ab-inbev', 'shell')
  and i.code = 'TAX_EFFECTIVE_RATE'
  and s.code = 'ESEF'
  and e.excerpt like '% M€%';
