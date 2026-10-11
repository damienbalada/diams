-- =============================================================================
-- Écart de salaire femmes-hommes : classé par l'écart à zéro (étape 2/2)
-- -----------------------------------------------------------------------------
-- Le moteur compare la valeur absolue de l'écart à celles des pairs du secteur :
-- 0 % (égalité) est le meilleur rang, quel que soit le sens de l'écart.
-- =============================================================================

update indicators set direction = 'closer_to_zero',
  methodology = 'Écart de rémunération femmes-hommes non ajusté (ESRS S1-16) ; rang intra-secteur de l''écart absolu : l''égalité (0 %) est le meilleur rang, quel que soit le sens de l''écart.'
where code = 'LAB_GENDER_PAYGAP';
