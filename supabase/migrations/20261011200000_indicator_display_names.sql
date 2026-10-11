-- =============================================================================
-- Libellés d'indicateurs lisibles par le public
-- -----------------------------------------------------------------------------
-- Les codes et les méthodes ne changent pas ; seuls les noms affichés sur les
-- fiches perdent leurs abréviations (« rému », « F/H »).
-- =============================================================================

update indicators set name = v.name
from (values
  ('LAB_CEO_PAY_RATIO',    'Écart de rémunération dirigeant / salarié médian'),
  ('LAB_GENDER_PAYGAP',    'Écart de salaire femmes-hommes'),
  ('LAB_EGAPRO_INDEX',     'Index égalité femmes-hommes (Égapro)'),
  ('SUP_VIGILANCE_PLAN',   'Plan de vigilance (devoir de vigilance)'),
  ('SUP_KNOWTHECHAIN',     'Lutte contre le travail forcé (KnowTheChain)'),
  ('SUP_BHRRC_ALLEG',      'Allégations d''atteintes aux droits humains'),
  ('ANI_BBFAW_TIER',       'Bien-être animal (classement BBFAW)'),
  ('ENV_SCOPE3_DISCLOSED', 'Émissions indirectes (scope 3) publiées'),
  ('ENV_SBTI_VALIDATED',   'Objectifs climat validés (SBTi)'),
  ('GEO_LOBBYING_TRANSP',  'Transparence du lobbying'),
  ('TAX_CBCR_PUBLISHED',   'Reporting fiscal pays par pays publié')
) as v(code, name)
where indicators.code = v.code;
