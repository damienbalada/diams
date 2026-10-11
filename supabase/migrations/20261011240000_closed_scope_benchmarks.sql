-- =============================================================================
-- Benchmarks à périmètre fermé : KnowTheChain et BBFAW (v0.6.0)
-- -----------------------------------------------------------------------------
-- KnowTheChain n'évalue qu'une liste fermée de sociétés (60 en alimentation &
-- boissons, 65 en habillement, 45 en technologies) et le BBFAW 149 entreprises
-- alimentaires. Leurs listes complètes sont désormais chargées par des
-- connecteurs déterministes (import_ktc, import_bbfaw) : une entreprise absente
-- n'a PAS été évaluée — ce n'est pas une donnée qu'on aurait manqué de
-- collecter. Ces indicateurs deviennent complémentaires : présents, ils
-- comptent ; absents, ils ne pèsent ni sur la note ni sur la fiabilité.
--
-- Le Fashion Transparency Index reste au socle tant que sa liste complète n'est
-- pas chargée par un connecteur.
-- =============================================================================

update indicators set complementary = true
where code in ('SUP_KNOWTHECHAIN', 'ANI_BBFAW_TIER');
