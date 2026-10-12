-- =============================================================================
-- Dernières preuves héritées en attente : retirées ou remplacées, motif écrit
-- -----------------------------------------------------------------------------
-- - Coca-Cola, mixité du conseil (« ~54 % », circulaire 2024) : la circulaire 2026
--   ne donne le nombre de femmes qu'en graphique ; rien à citer.
-- - Coca-Cola, scope 3 « publié » (réponse CDP 2023) : la mise à jour 2025 ne
--   publie que quelques catégories du scope 3 (services sous-traités, voyages,
--   franchisés), pas les achats de matières et d'emballages ; non confirmé.
-- - Stellantis, intensité en eau « 5,02 m³ par véhicule » : unité différente de
--   celle de l'indicateur (m³ par million d'euros de chiffre d'affaires).
-- - H&M, liste des fournisseurs attribuée à KnowTheChain : remplacée par la page
--   de H&M elle-même (lot 38).
-- =============================================================================

update evidence e set review_status = 'rejected', reviewer = 'retire:non-confirme-2026-10-13'
from entities en, indicators i, sources s
where en.id = e.entity_id and i.id = e.indicator_id and s.id = e.source_id and e.review_status = 'pending'
  and ((en.slug = 'coca-cola' and i.code in ('GOV_BOARD_GENDER', 'ENV_SCOPE3_DISCLOSED'))
    or (en.slug = 'stellantis' and i.code = 'WAT_INTENSITY'));

update evidence e set review_status = 'rejected', reviewer = 'remplace:lot38-page-hm-2026-10-13'
from entities en, indicators i, sources s
where en.id = e.entity_id and i.id = e.indicator_id and s.id = e.source_id and e.review_status = 'pending'
  and en.slug = 'hm-group' and i.code = 'SUP_SUPPLIER_LIST' and s.code = 'KNOWTHECHAIN';
