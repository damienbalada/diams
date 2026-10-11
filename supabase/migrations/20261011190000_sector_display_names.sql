-- =============================================================================
-- Noms de secteurs lisibles par le public
-- -----------------------------------------------------------------------------
-- « (holding) » est une précision interne (des groupes multi-marques, comparés
-- entre eux) qui n'a pas sa place dans un titre. Codes inchangés.
-- =============================================================================

update sectors set name = 'Grande consommation' where code = 'fmcg_group' and name = 'Grande consommation (holding)';
update sectors set name = 'Groupes de luxe'     where code = 'luxury_group' and name = 'Groupe de luxe (holding)';
