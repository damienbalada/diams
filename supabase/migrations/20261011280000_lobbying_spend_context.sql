-- =============================================================================
-- Budget de lobbying : donnée de contexte, jamais notée (v0.6.0)
-- -----------------------------------------------------------------------------
-- GEO_LOBBYING_SPEND (direction `contextual`) était, pour le moteur, une valeur
-- brute classée comme « plus c'est haut, mieux c'est » : dépenser davantage en
-- lobbying aurait amélioré la note. Le moteur traite désormais toute direction
-- `contextual` comme une information (affichée, comptée dans la fiabilité,
-- jamais dans la note). Les budgets sont chargés depuis l'export ouvert du
-- Registre de transparence de l'UE (import_eu_register).
--
-- Indicateur complémentaire : un budget n'existe que pour une entreprise
-- inscrite à un registre ; son absence ne dit rien.
-- =============================================================================

update indicators set complementary = true where code = 'GEO_LOBBYING_SPEND';

comment on column indicators.direction is
  'Sens de l''indicateur : higher_better, lower_better, closer_to_zero (objectif zéro, quel que soit le signe), contextual (information : affichée, comptée dans la fiabilité, jamais notée — v0.6.0).';
