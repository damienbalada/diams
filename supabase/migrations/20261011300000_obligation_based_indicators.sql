-- =============================================================================
-- Indicateurs nés d'une obligation légale : au socle seulement pour les
-- entreprises qui y sont soumises (v0.6.0)
-- -----------------------------------------------------------------------------
-- La fiabilité mesure ce qu'on sait d'une entreprise par rapport à ce qu'on peut
-- savoir. Certains indicateurs n'ont qu'une source systématique : une
-- obligation de publication (CSRD et taxonomie verte dans l'Union, Reg. S-K aux
-- États-Unis). Pour une entreprise qui n'y est pas soumise, leur absence n'est
-- pas une donnée qu'on aurait manqué de collecter : rien ne l'oblige à publier.
--
-- Ils deviennent complémentaires, ce qui donne exactement la règle voulue :
--   * entreprise soumise à l'obligation (régime rattaché) : manquant = 0 et
--     fiabilité en baisse (Règle 1, inchangée) ;
--   * entreprise non soumise : publié volontairement, il compte ; absent, il ne
--     pèse ni sur la note ni sur la fiabilité.
--
--   LAB_GENDER_PAYGAP     écart de rémunération non ajusté (CSRD, ESRS S1-16)
--   LAB_CEO_PAY_RATIO     ratio de rémunération (CSRD S1-16 ; Reg. S-K 402(u))
--   ENV_GHG_INTENSITY     intensité carbone (CSRD, ESRS E1-6)
--   ENV_SCOPE3_DISCLOSED  émissions indirectes (CSRD, ESRS E1-6)
--   ENV_TAXONOMY_CAPEX    part verte des investissements (taxonomie, art. 8)
--
-- Et PLA_REDUCTION (Global Commitment de la Fondation Ellen MacArthur) : liste
-- fermée de signataires, close en 2025 — complémentaire comme les autres
-- benchmarks à périmètre fermé.
-- =============================================================================

update indicators set complementary = true
where code in ('LAB_GENDER_PAYGAP', 'LAB_CEO_PAY_RATIO', 'ENV_GHG_INTENSITY',
               'ENV_SCOPE3_DISCLOSED', 'ENV_TAXONOMY_CAPEX', 'PLA_REDUCTION');
