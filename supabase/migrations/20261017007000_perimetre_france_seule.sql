-- Méthodologie (v0.7.3) : un chiffre limité à un pays ne remplace pas le chiffre de groupe demandé par la
-- CSRD (TotalEnergies : ratios sur la France seule, non retenus). Même règle appliquée le 17/10/2026 à
-- LDC (ratio de rémunération et écart salarial, France seule) et à Rémy Cointreau (ratio, France seule) :
-- preuves retirées, chiffres consignés au journal comme « publiés sous une autre forme ». Les ratios
-- britanniques de Diageo et Haleon (groupes non soumis à la CSRD, ratio imposé par leur loi sur le
-- périmètre du Royaume-Uni) sont conservés, périmètre écrit.
update evidence ev set review_status = 'rejected', reviewer = 'retire:perimetre-france-seule-2026-10-17'
from indicators i, entities e
where ev.indicator_id = i.id and ev.entity_id = e.id and ev.review_status = 'approved'
  and ((e.slug = 'ldc' and i.code in ('LAB_CEO_PAY_RATIO', 'LAB_GENDER_PAYGAP'))
    or (e.slug = 'remy-cointreau' and i.code = 'LAB_CEO_PAY_RATIO'));
