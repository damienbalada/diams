-- =============================================================================
-- Évolution des émissions : une baisse sur une seule année ne compte pas
-- -----------------------------------------------------------------------------
-- Une baisse ne vaut preuve que si elle couvre au moins deux ans : sur une seule
-- année, elle peut tenir aux ventes, aux prix ou à la météo (TotalEnergies −2 %,
-- BMW −5,5 %, Shell −2 % entre 2024 et 2025, seules années de leur tableau
-- réglementaire). Une hausse, même sur un an, est retenue : elle montre que les
-- émissions ne baissent pas (Shein +23 %, Volkswagen +7 %). Ces trois preuves
-- sont retirées, en attendant une série plus longue publiée par l'entreprise.
-- =============================================================================

update evidence e set review_status = 'rejected', reviewer = 'retire:baisse-sur-un-an-2026-10-12'
from indicators i, entities en
where i.id = e.indicator_id and en.id = e.entity_id
  and i.code = 'ENV_GHG_TREND' and e.review_status = 'approved'
  and en.slug in ('totalenergies', 'bmw', 'shell')
  and e.value_numeric < 0;
