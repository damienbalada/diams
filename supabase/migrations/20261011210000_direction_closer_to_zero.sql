-- =============================================================================
-- Sens d'indicateur « au plus près de zéro » (étape 1/2 : valeur d'énumération)
-- -----------------------------------------------------------------------------
-- Méthodologie v0.5.1. L'écart de salaire femmes-hommes vise l'égalité : un écart
-- en faveur des hommes comme des femmes s'en éloigne. Classer « plus bas =
-- mieux » rangeait premier un groupe où les femmes gagnent 30 % de plus.
-- La valeur est ajoutée seule : elle n'est utilisable qu'une fois validée.
-- =============================================================================

alter type indicator_direction add value if not exists 'closer_to_zero';
