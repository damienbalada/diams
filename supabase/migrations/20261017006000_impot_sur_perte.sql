-- Taux effectif d'imposition (17/10/2026) : la règle de la méthodologie exclut les exercices en perte
-- avant impôt (taux non interprétable). Deux preuves l'enfreignaient : Stellantis 2025 (« produit d'impôt
-- sur une perte avant impôt », affiché à tort comme « 16,1 % des bénéfices ») et Ubisoft 2025-2026
-- (charge d'impôt sur une perte, −9,2 %). Retirées ; la donnée reste manquante, consignée au journal.
update evidence ev set review_status = 'rejected', reviewer = 'retire:perte-avant-impot-2026-10-17'
from indicators i, entities e
where ev.indicator_id = i.id and ev.entity_id = e.id and i.code = 'TAX_EFFECTIVE_RATE'
  and ev.review_status = 'approved'
  and ((e.slug = 'stellantis' and ev.excerpt like '%perte avant impôt%')
    or (e.slug = 'ubisoft' and ev.excerpt like '%perte avant impôt%'));
